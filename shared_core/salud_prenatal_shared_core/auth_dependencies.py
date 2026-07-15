"""Autenticación/autorización basada en claims del JWT — SIN acceso a base de datos.

Cada servicio valida el token localmente con la `SECRET_KEY` compartida y arma un
`Principal` liviano desde los claims (`sub`, `user_id`, `role`, `subscription_status`).
No consulta ningún repositorio: por eso vive en shared_core y sirve a los 4 servicios.

Solo el servicio `auth` EMITE tokens (con esos claims, ver el use case de login);
el resto de servicios solo los VALIDA con estas dependencias.
"""
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from salud_prenatal_shared_core.security import get_secret_key, ALGORITHM
from salud_prenatal_shared_core.enums import RoleEnum, SubscriptionStatusEnum

# tokenUrl solo alimenta el botón "Authorize" de la doc OpenAPI; no cambia la validación.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")
# auto_error=False: no lanza 401 si falta el token (endpoints que funcionan con o sin sesión).
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/v1/login", auto_error=False)


class Principal(BaseModel):
    """Identidad del usuario reconstruida desde los claims del JWT (sin DB)."""
    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[RoleEnum] = None
    subscription_status: Optional[str] = None


def principal_from_token(token: str) -> Optional[Principal]:
    """Decodifica el JWT y arma un `Principal`. Devuelve None si el token es
    inválido o no trae `sub` (email)."""
    try:
        payload = jwt.decode(token, get_secret_key(), algorithms=[ALGORITHM])
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

    return Principal(
        user_id=payload.get("user_id"),
        email=email,
        role=role,
        subscription_status=payload.get("subscription_status"),
    )


def get_current_user(token: str = Depends(oauth2_scheme)) -> Principal:
    principal = principal_from_token(token)
    if principal is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return principal


def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme_optional),
) -> Optional[Principal]:
    if token is None:
        return None
    return principal_from_token(token)


def require_active_subscription(
    current_user: Principal = Depends(get_current_user),
) -> Principal:
    """Exige suscripción activa a los doctores. Otros roles pasan sin verificar
    (solo los doctores pagan). Lee el claim `subscription_status` del token, no la DB.
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
    return current_user


class RoleChecker:
    """Dependencia que gatea por rol leyendo el claim `role` del token."""

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
