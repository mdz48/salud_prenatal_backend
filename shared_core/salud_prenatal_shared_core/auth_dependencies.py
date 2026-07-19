"""Autorización basada en headers de identidad (X-User-*) — SIN decodificar JWT.

Modelo de confianza (Traefik + ForwardAuth): el JWT se valida UNA sola vez en el
edge. Traefik llama al validador del gateway (`/validate` valida-si-viene, o
`/validate/strict` que rechaza anónimos) antes de enrutar; el validador
decodifica el token con `principal_from_token` e inyecta los headers de
identidad, y Traefik BORRA cualquier X-User-* que trajera el cliente (todo
header listado en `authResponseHeaders` se elimina del request entrante antes
de copiar el del validador). Los servicios reconstruyen el `Principal` leyendo
esos headers: nunca ven el JWT ni la llave de firma.

Contrato: header vacío == ausente == anónimo. `X-User-Email` es el criterio de
presencia (espejo del claim `sub`). `principal_from_token` se conserva aquí
porque el validador del gateway es su único consumidor — el futuro plan
Vault/RS256 solo tocará ese punto.

ADVERTENCIA: pegarle a un servicio directamente (sin pasar por Traefik) se cree
cualquier X-User-* que le mandes. El perímetro de confianza es la red del
compose: en el VPS los servicios no publican puertos; en local los puertos
8001-8004 existen solo para debug.
"""
import os
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime
from jose import JWTError, jwt
from pydantic import BaseModel

from salud_prenatal_shared_core.jwt_key_provider import get_jwt_key_provider
from salud_prenatal_shared_core.enums import RoleEnum, SubscriptionStatusEnum
from salud_prenatal_shared_core.time import now_cdmx

# tokenUrl solo alimenta el botón "Authorize" de Swagger UI; no cambia la validación
# (esa vive en el edge). Debe ser una URL ABSOLUTA: el login vive únicamente en el
# servicio auth y este módulo se usa desde todos los servicios. AUTH_LOGIN_URL debe
# apuntar al EDGE (Traefik) para que el try-it-out funcione: los requests que salen
# de Swagger tienen que pasar por el ForwardAuth para ganar identidad.
AUTH_LOGIN_URL = os.getenv("AUTH_LOGIN_URL", "http://localhost:8000/api/v1/users/login")

# Esquemas SOLO-DECLARATIVOS: los servicios ya no consumen el token, pero mantener
# la sub-dependencia hace que el esquema OAuth2 aparezca en el OpenAPI de cada
# router protegido (botón Authorize) y que Swagger mande `Authorization: Bearer`,
# que es exactamente lo que el ForwardAuth del edge valida.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=AUTH_LOGIN_URL)
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl=AUTH_LOGIN_URL, auto_error=False)

# Contrato de identidad entre el validador del gateway y los servicios.
HEADER_USER_ID = "X-User-Id"
HEADER_USER_EMAIL = "X-User-Email"
HEADER_USER_ROLE = "X-User-Role"
HEADER_SUBSCRIPTION_STATUS = "X-Subscription-Status"
HEADER_SUBSCRIPTION_PERIOD_END = "X-Subscription-Period-End"
IDENTITY_HEADERS = (
    HEADER_USER_ID,
    HEADER_USER_EMAIL,
    HEADER_USER_ROLE,
    HEADER_SUBSCRIPTION_STATUS,
    HEADER_SUBSCRIPTION_PERIOD_END,
)


class Principal(BaseModel):
    """Identidad del usuario reconstruida desde los headers del edge (sin DB)."""
    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[RoleEnum] = None
    subscription_status: Optional[str] = None
    subscription_current_period_end: Optional[datetime] = None


def principal_from_token(token: str) -> Optional[Principal]:
    """Decodifica el JWT y arma un `Principal`. Devuelve None si el token es
    inválido o no trae `sub` (email). Único consumidor: el validador del gateway
    (ForwardAuth) — los servicios usan `principal_from_headers`."""
    provider = get_jwt_key_provider()
    try:
        payload = jwt.decode(token, provider.get_verification_key(), algorithms=[provider.algorithm])
    except JWTError:
        return None

    email = payload.get("sub")
    if not email:
        return None

    role_raw = payload.get("role")
    role = None
    if role_raw is not None:
        try:
            role = RoleEnum(role_raw)
        except ValueError:
            role = None

    end_ts = payload.get("subscription_current_period_end")
    end_dt = datetime.fromisoformat(end_ts) if end_ts else None

    return Principal(
        user_id=payload.get("user_id"),
        email=email,
        role=role,
        subscription_status=payload.get("subscription_status"),
        subscription_current_period_end=end_dt,
    )


def principal_from_headers(headers) -> Optional[Principal]:
    """Reconstruye el `Principal` desde los headers X-User-* inyectados por el
    edge. Acepta cualquier Mapping (starlette Headers o dict; lookup
    case-insensitive). Devuelve None (anónimo) si no hay email. Valores
    malformados degradan a None campo por campo — nunca lanzan: un header roto
    debe degradar a menos identidad, no tirar un 500."""
    h = {k.lower(): v for k, v in headers.items()}

    def _get(name: str) -> Optional[str]:
        value = (h.get(name.lower()) or "").strip()
        return value or None

    email = _get(HEADER_USER_EMAIL)
    if not email:
        return None

    user_id = None
    raw_id = _get(HEADER_USER_ID)
    if raw_id:
        try:
            user_id = int(raw_id)
        except ValueError:
            user_id = None

    role = None
    raw_role = _get(HEADER_USER_ROLE)
    if raw_role:
        try:
            role = RoleEnum(raw_role)
        except ValueError:
            role = None

    end_dt = None
    raw_end = _get(HEADER_SUBSCRIPTION_PERIOD_END)
    if raw_end:
        try:
            end_dt = datetime.fromisoformat(raw_end)
        except ValueError:
            end_dt = None

    return Principal(
        user_id=user_id,
        email=email,
        role=role,
        subscription_status=_get(HEADER_SUBSCRIPTION_STATUS),
        subscription_current_period_end=end_dt,
    )


def get_current_user_optional(
    request: Request,
    _token: Optional[str] = Depends(oauth2_scheme_optional),
) -> Optional[Principal]:
    """Identidad desde los headers del edge; None si anónimo. `_token` se IGNORA:
    la sub-dependencia existe solo para propagar el esquema OAuth2 al OpenAPI
    (botón Authorize) — quien valida el Bearer es el ForwardAuth de Traefik."""
    return principal_from_headers(request.headers)


def get_current_user(
    principal: Optional[Principal] = Depends(get_current_user_optional),
) -> Principal:
    if principal is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return principal


def require_active_subscription(
    current_user: Principal = Depends(get_current_user),
) -> Principal:
    """Exige suscripción activa a los doctores. Otros roles pasan sin verificar
    (solo los doctores pagan). Lee la identidad inyectada por el edge, no la DB.
    Sin status activo -> HTTP 402."""
    role = current_user.role
    role_str = role.value if hasattr(role, "value") else str(role)
    if role_str != RoleEnum.doctor.value:
        return current_user

    current_status = current_user.subscription_status or "none"
    if current_status != SubscriptionStatusEnum.active.value:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Active subscription required. Current status: {current_status}",
        )

    end_dt = current_user.subscription_current_period_end
    if end_dt is not None:
        compare_now = now_cdmx()
        if end_dt.tzinfo is None:
            compare_now = compare_now.replace(tzinfo=None)
        if end_dt < compare_now:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Subscription expired",
            )

    return current_user


class RoleChecker:
    """Dependencia que gatea por rol leyendo la identidad inyectada por el edge."""

    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: Principal = Depends(get_current_user)) -> Principal:
        role = current_user.role
        user_role_str = role.value if hasattr(role, "value") else str(role)
        allowed_strs = [r.value if hasattr(r, "value") else str(r) for r in self.allowed_roles]
        if user_role_str not in allowed_strs:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for this role",
            )
        return current_user
