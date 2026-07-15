from app.features.notifications.infrastructure.repositories.device_token_repository import DeviceTokenRepository

class UnregisterDeviceTokenUseCase:
    def __init__(self, device_token_repository: DeviceTokenRepository):
        self.device_token_repository = device_token_repository

    def execute(self, user_id: int, token: str) -> bool:
        return self.device_token_repository.unregister_token(user_id, token)
