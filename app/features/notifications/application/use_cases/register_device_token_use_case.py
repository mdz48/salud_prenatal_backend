from typing import Optional

from app.features.notifications.infrastructure.repositories.device_token_repository import DeviceTokenRepository

class RegisterDeviceTokenUseCase:
    def __init__(self, device_token_repository: DeviceTokenRepository):
        self.device_token_repository = device_token_repository

    def execute(self, user_id: Optional[int], token: str, device_type: str = "android"):
        return self.device_token_repository.register_token(user_id, token, device_type)
