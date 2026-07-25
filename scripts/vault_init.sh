#!/usr/bin/env bash
# vault_init.sh — inicialización ÚNICA del Vault persistente de producción.
# Hace: operator init (1/1) -> guarda unseal key + root token en ~/proyectos/.vault-init
# (chmod 600) -> desella. De ahí en adelante el sidecar vault_unsealer se encarga.
#
# CORRE UNA SOLA VEZ. Re-inicializar exige borrar el volumen vault_data, y eso
# destruye el par RSA -> mueren todos los tokens vivos.
#
# Uso: cd ~/proyectos && ./salud_prenatal_backend/scripts/vault_init.sh
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-$HOME/proyectos}"
INIT_FILE="$PROJECT_DIR/.vault-init"
CONTAINER="${VAULT_CONTAINER:-vault}"

if [ -s "$INIT_FILE" ]; then
  echo "ABORTA: $INIT_FILE ya tiene contenido -> Vault ya fue inicializado." >&2
  echo "  Si solo está sellado: docker compose up -d vault_unsealer" >&2
  exit 1
fi

if ! docker ps --format '{{.Names}}' | grep -qx "$CONTAINER"; then
  echo "ABORTA: el contenedor '$CONTAINER' no está corriendo (docker compose up -d vault)." >&2
  exit 1
fi

echo "==> [1/4] Esperando a que Vault responda"
for i in $(seq 1 30); do
  # exit 2 = sellado/no inicializado; también cuenta como "responde"
  if docker exec -e VAULT_ADDR=http://127.0.0.1:8200 "$CONTAINER" vault status 2>&1 | grep -q 'Initialized'; then break; fi
  sleep 2
done
echo "    Vault responde ✓"

# 1 sola unseal key: simplificación para un VPS de un solo administrador. Con varios
# operadores serían 5/3 repartidas entre personas distintas.
echo "==> [2/4] vault operator init (key-shares=1, key-threshold=1)"
RAW="$(docker exec -e VAULT_ADDR=http://127.0.0.1:8200 "$CONTAINER" \
  vault operator init -key-shares=1 -key-threshold=1 -format=json)"

PARSED="$(printf '%s' "$RAW" | python3 -c '
import json, sys
d = json.load(sys.stdin)
print("VAULT_UNSEAL_KEY=" + d["unseal_keys_b64"][0])
print("VAULT_ROOT_TOKEN=" + d["root_token"])
')"

if [ "$(printf '%s\n' "$PARSED" | grep -c '=')" -ne 2 ]; then
  echo "ABORTA: no pude parsear 'operator init'. NO se escribió nada." >&2
  printf '%s\n' "$RAW" >&2
  exit 1
fi

echo "==> [3/4] Guardando en $INIT_FILE (chmod 600)"
umask 077
{
  echo "# Generado por vault_init.sh. NO commitear, NO borrar: sin la unseal key el"
  echo "# Vault sellado es irrecuperable y con él el par RSA de firma."
  printf '%s\n' "$PARSED"
} > "$INIT_FILE"
chmod 600 "$INIT_FILE"
printf '%s\n' "$PARSED" | sed -E 's/=(.{6}).*/=\1…/' | sed 's/^/      /'

echo "==> [4/4] Desellando por primera vez"
UNSEAL_KEY="$(grep -m1 '^VAULT_UNSEAL_KEY=' "$INIT_FILE" | cut -d= -f2-)"
docker exec -e VAULT_ADDR=http://127.0.0.1:8200 "$CONTAINER" \
  vault operator unseal "$UNSEAL_KEY" >/dev/null
docker exec -e VAULT_ADDR=http://127.0.0.1:8200 "$CONTAINER" vault status | grep -E 'Sealed|Initialized'

cat <<EOF

LISTO. Ahora bootstrapea con el ROOT TOKEN nuevo (ya no es "root" como en dev-mode):

  export VAULT_TOKEN=\$(grep '^VAULT_ROOT_TOKEN=' $INIT_FILE | cut -d= -f2-)
  docker run --rm --network proyectos_app_network \\
    -e VAULT_ADDR=http://vault:8200 -e VAULT_TOKEN="\$VAULT_TOKEN" \\
    -v $PROJECT_DIR/salud_prenatal_backend/scripts/vault_bootstrap.py:/b.py \\
    python:3.11-slim sh -c "pip install -q hvac cryptography && python /b.py"

Y luego: docker compose up -d vault_unsealer
EOF
