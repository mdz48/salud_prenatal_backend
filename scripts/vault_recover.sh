#!/usr/bin/env bash
# vault_recover.sh — recuperación de un solo comando cuando Vault (dev-mode) se
# reinicia y pierde las llaves/AppRoles, dejando auth/gateway sin poder firmar/validar.
#
# Hace: re-bootstrapea Vault (par RSA + políticas + AppRoles), escribe las nuevas
# credenciales en el .env del PROYECTO (~/proyectos/.env, donde compose lee ${...}),
# y recrea auth + gateway.
#
# Uso:
#   ./vault_recover.sh            # recuperación real
#   ./vault_recover.sh --dry-run  # solo bootstrapea y muestra las creds; NO toca .env ni contenedores
#
# Síntoma de que hace falta: login falla / rutas protegidas dan 500; `docker compose ps vault`
# muestra uptime bajo; `docker logs sp_auth` muestra errores de Vault al firmar.
set -euo pipefail

DRY_RUN=0
[ "${1:-}" = "--dry-run" ] && DRY_RUN=1

PROJECT_DIR="${PROJECT_DIR:-$HOME/proyectos}"
ENV_FILE="$PROJECT_DIR/.env"
NETWORK="${NETWORK:-proyectos_app_network}"
BOOTSTRAP="$PROJECT_DIR/salud_prenatal_backend/scripts/vault_bootstrap.py"
VADDR="${VAULT_ADDR_INTERNAL:-http://vault:8200}"
VTOKEN="${VAULT_TOKEN:-root}"

echo "==> [1/4] Re-bootstrap de Vault (dry-run=$DRY_RUN)"
if [ ! -f "$BOOTSTRAP" ]; then
  echo "ERROR: no existe $BOOTSTRAP" >&2
  echo "  scripts/ está gitignoreado — el bootstrap DEBE estar en el VPS. Restáuralo antes." >&2
  exit 1
fi

OUT="$(docker run --rm --network "$NETWORK" \
  -e VAULT_ADDR="$VADDR" -e VAULT_TOKEN="$VTOKEN" \
  -v "$BOOTSTRAP:/b.py" \
  python:3.11-slim sh -c 'pip install -q hvac cryptography 2>/dev/null && python /b.py' || true)"

CREDS="$(echo "$OUT" | grep -E '^(VAULT_ROLE_ID_|VAULT_SECRET_ID_)(AUTH|GATEWAY)=' || true)"
N="$(printf '%s\n' "$CREDS" | grep -cE '=' || true)"
if [ "$N" -ne 4 ]; then
  echo "ERROR: esperaba 4 credenciales, obtuve $N. NO se modifica nada." >&2
  echo "--- salida del bootstrap ---" >&2
  echo "$OUT" >&2
  exit 1
fi
echo "    4 credenciales obtenidas ✓"
# Mostrar enmascaradas (solo los primeros 8 chars del valor)
printf '%s\n' "$CREDS" | sed -E 's/=(.{8}).*/=\1…/' | sed 's/^/      /'

if [ "$DRY_RUN" -eq 1 ]; then
  echo
  echo "DRY-RUN: NO se tocó el .env ni se recrearon contenedores. Fin."
  exit 0
fi

echo "==> [2/4] Actualizando $ENV_FILE (backup automático)"
cp "$ENV_FILE" "$ENV_FILE.bak-$(date +%s)" 2>/dev/null || true
grep -vE '^(JWT_KEY_BACKEND|VAULT_ROLE_ID_|VAULT_SECRET_ID_)=' "$ENV_FILE" 2>/dev/null > "$ENV_FILE.tmp" || true
{ echo "JWT_KEY_BACKEND=vault"; printf '%s\n' "$CREDS"; } >> "$ENV_FILE.tmp"
mv "$ENV_FILE.tmp" "$ENV_FILE"
echo "    .env actualizado ✓"

echo "==> [3/4] Recreando auth + gateway"
cd "$PROJECT_DIR"
docker compose up -d --force-recreate auth gateway
sleep 7

echo "==> [4/4] Verificación"
docker compose ps auth gateway 2>/dev/null | tail -3
ERR="$(docker logs sp_auth 2>&1 | tail -30 | grep -ciE 'error|runtime' || true)"
echo "    errores recientes en auth: $ERR"
echo
echo "LISTO. Confirma con un login que el token es alg:RS256:"
echo "  curl -s -X POST https://saludprenatal.sytes.net/api/v1/users/login \\"
echo "    -H 'Content-Type: application/json' -d '{\"email\":\"<doc>\",\"password\":\"<pass>\"}'"
