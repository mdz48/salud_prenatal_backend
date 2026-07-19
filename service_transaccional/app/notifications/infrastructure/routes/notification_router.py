from typing import Optional

# pyrefly: ignore [missing-import]
from container import Container
from salud_prenatal_shared_core.db_cleanup import close_db_after
from fastapi import APIRouter, Depends, status
from app.notifications.infrastructure.schemas.notification_schema import DeviceTokenCreate, DeviceTokenUnregister
from app.notifications.infrastructure.controllers.notification_controller import NotificationController
from salud_prenatal_shared_core.auth_dependencies import get_current_user, get_current_user_optional
from salud_prenatal_shared_core.auth_dependencies import Principal as UserEntity

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
@close_db_after(Container)
def register_token(
    data: DeviceTokenCreate,
    current_user: Optional[UserEntity] = Depends(get_current_user_optional)
):
    # Sin sesión iniciada se registra el token a nivel de dispositivo
    # (user_id=None); al loguearse, un nuevo llamado a este endpoint
    # reasigna el token al usuario (ver DeviceTokenRepository.register_token).
    controller = Container.notification_controller()
    user_id = current_user.user_id if current_user else None
    return controller.register_token(user_id=user_id, data=data)


@router.post("/unregister", status_code=status.HTTP_200_OK)
@close_db_after(Container)
def unregister_token(
    data: DeviceTokenUnregister,
    current_user: UserEntity = Depends(get_current_user)
):
    controller = Container.notification_controller()
    return controller.unregister_token(user_id=current_user.user_id, data=data)
