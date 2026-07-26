from typing import List, Optional

# pyrefly: ignore [missing-import]
from container import Container
from salud_prenatal_shared_core.db_cleanup import close_db_after
from fastapi import APIRouter, Depends, status
from app.notifications.infrastructure.schemas.notification_schema import (
    DeviceTokenCreate,
    DeviceTokenUnregister,
    PatientLinkedEventRequest,
)
from app.notifications.domain.notification_entity import NotificationEntity
from salud_prenatal_shared_core.auth_dependencies import get_current_user, get_current_user_optional
from salud_prenatal_shared_core.auth_dependencies import Principal as UserEntity
from app.core.internal_auth import verify_internal_service_token

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
@close_db_after(Container)
def register_token(
    data: DeviceTokenCreate,
    current_user: Optional[UserEntity] = Depends(get_current_user_optional)
):
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


@router.get("/", response_model=List[NotificationEntity], status_code=status.HTTP_200_OK)
@close_db_after(Container)
def get_user_notifications(
    current_user: UserEntity = Depends(get_current_user)
):
    controller = Container.notification_controller()
    return controller.get_user_notifications(user_id=current_user.user_id)


@router.patch("/{notification_id}/read", status_code=status.HTTP_200_OK)
@close_db_after(Container)
def mark_notification_read(
    notification_id: int,
    current_user: UserEntity = Depends(get_current_user)
):
    controller = Container.notification_controller()
    return controller.mark_as_read(notification_id=notification_id, user_id=current_user.user_id)


@router.post(
    "/internal/patient-linked",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_internal_service_token)],
    include_in_schema=False,
)
@close_db_after(Container)
def publish_patient_linked_event(data: PatientLinkedEventRequest):
    """Llamado server-to-server por service_usuarios al vincular un paciente con un
    doctor. Protegido por INTERNAL_SERVICE_TOKEN (ver app/core/internal_auth.py),
    no por identidad de usuario -- el catch-all de transaccional expone /api/v1
    completo detrás de jwt-auth (anónimo permitido), así que este endpoint no
    puede depender solo de la red del compose."""
    controller = Container.notification_controller()
    return controller.publish_patient_linked_event(patient_id=data.patient_id, doctor_id=data.doctor_id)
