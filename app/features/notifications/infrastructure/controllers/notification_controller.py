from typing import Optional

from fastapi import HTTPException, status
from app.features.notifications.infrastructure.schemas.notification_schema import DeviceTokenCreate, DeviceTokenUnregister
from app.features.notifications.application.use_cases.register_device_token_use_case import RegisterDeviceTokenUseCase
from app.features.notifications.application.use_cases.unregister_device_token_use_case import UnregisterDeviceTokenUseCase

class NotificationController:
    def __init__(
        self,
        register_device_token_use_case: RegisterDeviceTokenUseCase,
        unregister_device_token_use_case: UnregisterDeviceTokenUseCase
    ):
        self.register_device_token_use_case = register_device_token_use_case
        self.unregister_device_token_use_case = unregister_device_token_use_case

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
