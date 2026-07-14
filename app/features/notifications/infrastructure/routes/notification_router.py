from typing import Optional

# pyrefly: ignore [missing-import]
from dependency_injector.wiring import inject, Provide
from app.core.containers import Container
from fastapi import APIRouter, Depends, status
from app.features.notifications.infrastructure.schemas.notification_schema import DeviceTokenCreate, DeviceTokenUnregister
from app.features.notifications.infrastructure.controllers.notification_controller import NotificationController
from app.core.dependencies import get_current_user, get_current_user_optional
from app.features.users.infrastructure.models.user_model import Usuario

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
@inject
def register_token(
    data: DeviceTokenCreate,
    controller: NotificationController = Depends(Provide[Container.notification_controller]),
    current_user: Optional[Usuario] = Depends(get_current_user_optional)
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
    current_user: Usuario = Depends(get_current_user)
):
    return controller.unregister_token(user_id=current_user.user_id, data=data)
