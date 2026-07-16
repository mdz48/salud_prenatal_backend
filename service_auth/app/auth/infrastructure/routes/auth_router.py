"""Ruta de login. Se conserva el path del monolito (`/api/v1/users/login`) para
NO cambiar el contrato del frontend: prefijo del router `/users` + `/login`,
montado bajo `/api/v1` en main.py.

Acepta JSON `{email, password}` o Form (`username`/`email`, `password`) igual que
antes, para seguir sirviendo el flujo OAuth2 de la doc.
"""
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, status, Request, HTTPException

from salud_prenatal_shared_core.auth_dependencies import get_current_user, Principal
from app.auth.infrastructure.schemas.auth_schema import Token, RefreshResponse
from app.auth.infrastructure.controllers.auth_controller import AuthController
from container import Container

router = APIRouter(prefix="/users", tags=["Auth"])


@router.post("/login", response_model=Token)
@inject
async def login(
    request: Request,
    controller: AuthController = Depends(Provide[Container.auth_controller]),
):
    content_type = request.headers.get("content-type", "")
    if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        form = await request.form()
        email = form.get("username") or form.get("email")
        password = form.get("password")
    else:
        try:
            body = await request.json()
            email = body.get("email") or body.get("username")
            password = body.get("password")
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Formato invalido. Envia JSON (email, password) o Form Data (username, password).",
            )

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Se requieren credenciales (email/username y password).",
        )

    return controller.login(email=str(email), password=str(password))


@router.post("/refresh", response_model=RefreshResponse)
@inject
def refresh(
    current_user: Principal = Depends(get_current_user),
    controller: AuthController = Depends(Provide[Container.auth_controller]),
):
    role_str = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    return controller.refresh(
        email=current_user.email, user_id=current_user.user_id, role=role_str
    )
