#!/bin/sh
# vault_unseal_loop.sh — sidecar que mantiene DESSELLADO el Vault persistente.
# Con storage en disco Vault arranca sellado en cada reinicio, y sellado = no
# entrega llaves = auth no firma y gateway no valida. Este loop lo desella con la
# key de ~/proyectos/.vault-init (montada read-only como /vault-init).
#
# Es "auto-unseal del pobre": la key vive en un archivo chmod 600 del VPS, mismo
# problema de secret-zero que el SECRET_ID del AppRole. Un auto-unseal real delega
# el sello a un KMS externo. Lo que sí se gana frente a dev-mode: el par RSA ya no
# se pierde en un reboot, así que nadie se desloguea.
set -u

INIT_FILE=/vault-init
: "${VAULT_ADDR:=http://vault:8200}"
: "${UNSEAL_POLL_SECONDS:=10}"
export VAULT_ADDR

log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] unsealer: $*"; }

if [ ! -f "$INIT_FILE" ]; then
  log "FATAL: falta $INIT_FILE. Corre vault_init.sh primero."
  exit 1
fi

KEY="$(grep -m1 '^VAULT_UNSEAL_KEY=' "$INIT_FILE" | cut -d= -f2-)"
if [ -z "$KEY" ]; then
  log "FATAL: $INIT_FILE no contiene VAULT_UNSEAL_KEY."
  exit 1
fi

log "arrancado (VAULT_ADDR=$VAULT_ADDR, poll=${UNSEAL_POLL_SECONDS}s)"

while true; do
  STATUS="$(vault status -format=json 2>/dev/null || true)"

  case "$STATUS" in
    '')
      log "Vault no responde todavía"
      ;;
    *'"initialized": false'*)
      # No auto-inicializamos: generar llaves sin custodiar la unseal key sería
      # peor que la caída.
      log "Vault NO inicializado -> corre scripts/vault_init.sh en el VPS"
      ;;
    *'"sealed": true'*)
      log "Vault SELLADO -> desellando"
      if vault operator unseal "$KEY" >/dev/null 2>&1; then
        log "  desellado OK"
      else
        log "  FALLO al desellar (¿unseal key equivocada / volumen recreado?)"
      fi
      ;;
    *'"sealed": false'*)
      : # normal, sin ruido en logs
      ;;
    *)
      log "estado inesperado de 'vault status'"
      ;;
  esac

  sleep "$UNSEAL_POLL_SECONDS"
done
