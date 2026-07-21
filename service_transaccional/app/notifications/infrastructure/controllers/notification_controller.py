from typing import Optional
from fastapi import HTTPException, status
from app.notifications.infrastructure.schemas.notification_schema import DeviceTokenCreate, DeviceTokenUnregister
from app.notifications.application.use_cases.register_device_token_use_case import RegisterDeviceTokenUseCase
from app.notifications.application.use_cases.unregister_device_token_use_case import UnregisterDeviceTokenUseCase
from app.notifications.application.get_user_notifications_usecase import GetUserNotificationsUseCase
from app.notifications.application.mark_notification_read_usecase import MarkNotificationReadUseCase
from app.notifications.application.publish_patient_linked_event_usecase import PublishPatientLinkedEventUseCase


class NotificationController:
    def __init__(
        self,
        register_device_token_use_case: RegisterDeviceTokenUseCase,
        unregister_device_token_use_case: UnregisterDeviceTokenUseCase,
        get_user_notifications_use_case: Optional[GetUserNotificationsUseCase] = None,
        mark_notification_read_use_case: Optional[MarkNotificationReadUseCase] = None,
        publish_patient_linked_event_use_case: Optional[PublishPatientLinkedEventUseCase] = None,
    ):
        self.register_device_token_use_case = register_device_token_use_case
        self.unregister_device_token_use_case = unregister_device_token_use_case
        self.get_user_notifications_use_case = get_user_notifications_use_case
        self.mark_notification_read_use_case = mark_notification_read_use_case
        self.publish_patient_linked_event_use_case = publish_patient_linked_event_use_case

    def register_token(self, user_id: Optional[int], data: DeviceTokenCreate):
        try:
            return self.register_device_token_use_case.execute(
                user_id=user_id,
                token=data.token,
                device_type=data.device_type
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred while registering the device token: {str(e)}"
            )

    def unregister_token(self, user_id: int, data: DeviceTokenUnregister):
        try:
            success = self.unregister_device_token_use_case.execute(
                user_id=user_id,
                token=data.token
            )
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Token not found for this user."
                )
            return {"status": "success", "message": "Token unregistered successfully."}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred while unregistering the device token: {str(e)}"
            )

    def get_user_notifications(self, user_id: int):
        if not self.get_user_notifications_use_case:
            raise HTTPException(status_code=500, detail="Use case not configured")
        return self.get_user_notifications_use_case.execute(user_id=user_id)

    def mark_as_read(self, notification_id: int, user_id: int):
        if not self.mark_notification_read_use_case:
            raise HTTPException(status_code=500, detail="Use case not configured")
        success = self.mark_notification_read_use_case.execute(notification_id=notification_id, user_id=user_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
        return {"status": "success", "message": "Notification marked as read"}

    def publish_patient_linked_event(self, patient_id: int, doctor_id: int):
        if not self.publish_patient_linked_event_use_case:
            raise HTTPException(status_code=500, detail="Use case not configured")
        self.publish_patient_linked_event_use_case.execute(patient_id=patient_id, doctor_id=doctor_id)
        return {"status": "success"}
