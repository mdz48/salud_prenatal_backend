"""Puertos del slice jwt_validation (Ports & Adapters, estilo del repo).

El validador es el ÚNICO punto del sistema que decodifica JWTs: Traefik le
pregunta por cada request (ForwardAuth) y él responde con la identidad en
headers. Cambiar el mecanismo de verificación (p. ej. RS256 con llave pública
de Vault) = escribir otro adapter de ITokenVerifier; router y service no se
enteran.
"""
from typing import Optional, Protocol

from salud_prenatal_shared_core.auth_dependencies import Principal, principal_from_token


class ITokenVerifier(Protocol):
    def verify(self, token: str) -> Optional[Principal]:
        """Devuelve la identidad del token, o None si es inválido/expirado."""
        ...


class SharedCoreTokenVerifier:
    """Adapter default: delega en shared_core (HS256 vía jwt_key_provider)."""

    def verify(self, token: str) -> Optional[Principal]:
        return principal_from_token(token)
