from typing import Optional

# pyrefly: ignore [missing-import]
from dependency_injector.wiring import inject, Provide
from container import Container
from fastapi import APIRouter, Depends, status
from app.notifications.infrastructure.schemas.notification_schema import DeviceTokenCreate, DeviceTokenUnregister
from app.notifications.infrastructure.controllers.notification_controller import NotificationController
from salud_prenatal_shared_core.auth_dependencies import get_current_user, get_current_user_optional
from salud_prenatal_shared_core.auth_dependencies import Principal as UserEntity

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
@inject
def register_token(
    data: DeviceTokenCreate,
    controller: NotificationController = Depends(Provide[Container.notification_controller]),
    current_user: Optional[UserEntity] = Depends(get_current_user_optional)
):
    # Sin sesión iniciada se registra el token a nivel de dispositivo
    # (user_id=None); al loguearse, un nuevo llamado a este endpoint
    # reasigna el token al usuario (ver DeviceTokenRepository.register_token).
    user_id = current_user.user_id if current_user else None
    return controller.register_token(user_id=user_id, data=data)

@router.post("/unregister", status_code=status.HTTP_200_OK)
@inject
def unregister_token(
    data: DeviceTokenUnregister,
    controller: NotificationController = Depends(Provide[Container.notification_controller]),
    current_user: UserEntity = Depends(get_current_user)
):
    return controller.unregister_token(user_id=current_user.user_id, data=data)
