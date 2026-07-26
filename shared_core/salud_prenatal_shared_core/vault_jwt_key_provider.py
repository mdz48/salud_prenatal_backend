"""Implementación de IJwtKeyProvider basada en HashiCorp Vault.

Utiliza AppRole para autenticarse, lee un par de llaves asimétricas RSA
desde `secret/jwt/private` y `secret/jwt/public`, y devuelve formato PEM.
Maneja caché interna a nivel de instancia para evitar consultas a Vault en cada request.
"""
from typing import Optional
import os

from .jwt_key_provider import IJwtKeyProvider


class VaultJwtKeyProvider(IJwtKeyProvider):
    def __init__(self):
        self._client = None
        self._private_key_cache = None
        self._public_key_cache = None

    @property
    def algorithm(self) -> str:
        return "RS256"

    def _get_client(self):
        if self._client is not None:
            return self._client

        import hvac

        vault_addr = os.getenv("VAULT_ADDR")
        role_id = os.getenv("VAULT_ROLE_ID")
        secret_id = os.getenv("VAULT_SECRET_ID")

        if not vault_addr or not role_id or not secret_id:
            raise RuntimeError("Faltan variables de entorno para Vault (VAULT_ADDR, VAULT_ROLE_ID, VAULT_SECRET_ID).")

        try:
            client = hvac.Client(url=vault_addr)
            # Login con AppRole
            client.auth.approle.login(role_id=role_id, secret_id=secret_id)
            if not client.is_authenticated():
                raise RuntimeError("Autenticación con Vault falló: token inválido tras AppRole login.")
            self._client = client
            return self._client
        except Exception as e:
            raise RuntimeError(f"Error inicializando cliente Vault: {str(e)}") from e

    def get_signing_key(self) -> str:
        if self._private_key_cache is not None:
            return self._private_key_cache
        
        client = self._get_client()
        try:
            # En KV v2 la ruta real de lectura de datos lleva 'data/'
            response = client.secrets.kv.v2.read_secret_version(path='jwt/private')
            private_key = response['data']['data'].get('private_key')
            if not private_key:
                raise RuntimeError("Llave 'private_key' no encontrada en secret/jwt/private")
            self._private_key_cache = private_key
            return private_key
        except Exception as e:
            raise RuntimeError(f"Error leyendo private key desde Vault: {str(e)}") from e

    def get_verification_key(self, kid: Optional[str] = None) -> str:
        if self._public_key_cache is not None:
            return self._public_key_cache
        
        client = self._get_client()
        try:
            response = client.secrets.kv.v2.read_secret_version(path='jwt/public')
            public_key = response['data']['data'].get('public_key')
            if not public_key:
                raise RuntimeError("Llave 'public_key' no encontrada en secret/jwt/public")
            self._public_key_cache = public_key
            return public_key
        except Exception as e:
            raise RuntimeError(f"Error leyendo public key desde Vault: {str(e)}") from e
