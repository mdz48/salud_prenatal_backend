"""Driving adapter HTTP del validador ForwardAuth.

Traefik llama a estos endpoints ANTES de enrutar cada request:
- 2xx  -> la petición continúa; Traefik copia los headers de identidad
         (authResponseHeaders) al request que llega al servicio.
- 401  -> la petición muere en el edge.
"""
from typing import Optional

from fastapi import APIRouter, Header, HTTPException, Response, status

from .ports import SharedCoreTokenVerifier
from .service import identity_headers_for, resolve_principal

router = APIRouter()

# Sin estado: instancia de módulo, igual que los adapters del resto del repo.
_verifier = SharedCoreTokenVerifier()


def _validate(authorization: Optional[str], forwarded_uri: Optional[str], strict: bool) -> Response:
    principal, had_token = resolve_principal(_verifier, authorization, forwarded_uri)
    if had_token and principal is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if strict and principal is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Response(status_code=status.HTTP_200_OK, headers=identity_headers_for(principal))


@router.get("/validate", include_in_schema=False)
def validate(
    authorization: Optional[str] = Header(None),
    x_forwarded_uri: Optional[str] = Header(None),
):
    """Valida-si-viene (portero universal): anónimo pasa con identidad vacía;
    token inválido muere aquí. Rutas con público y protegido mezclados."""
    return _validate(authorization, x_forwarded_uri, strict=False)


@router.get("/validate/strict", include_in_schema=False)
def validate_strict(
    authorization: Optional[str] = Header(None),
    x_forwarded_uri: Optional[str] = Header(None),
):
    """Fail-closed: anónimo -> 401. Prefijos 100% protegidos (chat, forums,
    subscriptions sin webhook, refresh)."""
    return _validate(authorization, x_forwarded_uri, strict=True)
