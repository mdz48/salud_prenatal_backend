// Vault de PRODUCCIÓN. Reemplaza el `-dev` de staging: el storage en disco hace que
// el par RSA, las políticas y los AppRoles sobrevivan a reinicios y reboots.
// A cambio arranca SELLADO -> lo desella el sidecar vault_unsealer.

storage "file" {
  path = "/vault/file"
}

listener "tcp" {
  address = "0.0.0.0:8200"
  // Sin TLS: Vault no publica puertos, solo lo alcanzan auth/gateway/unsealer
  // dentro de app_network. TLS hacia Vault sigue pendiente (Nivel B).
  tls_disable = 1
}

api_addr     = "http://vault:8200"
cluster_addr = "http://vault:8201"

ui = false

// mlock activo (el contenedor trae cap_add: IPC_LOCK) para que los secretos no
// caigan a swap. Si arranca con "Failed to lock memory", descomentar:
// disable_mlock = true
