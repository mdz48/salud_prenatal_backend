from unittest.mock import MagicMock

from app.features.notifications.application.use_cases.register_device_token_use_case import (
    RegisterDeviceTokenUseCase,
)
from app.features.notifications.application.use_cases.unregister_device_token_use_case import (
    UnregisterDeviceTokenUseCase,
)


class TestRegisterDeviceTokenUseCase:
    def test_delegates_to_repository_with_user_id(self):
        mock_repo = MagicMock()
        mock_repo.register_token.return_value = "device-row"

        usecase = RegisterDeviceTokenUseCase(mock_repo)
        result = usecase.execute(user_id=5, token="tok", device_type="ios")

        mock_repo.register_token.assert_called_once_with(5, "tok", "ios")
        assert result == "device-row"

    def test_delegates_to_repository_with_none_user_id(self):
        # Registro de dispositivo antes de login.
        mock_repo = MagicMock()

        usecase = RegisterDeviceTokenUseCase(mock_repo)
        usecase.execute(user_id=None, token="tok-anon", device_type="android")

        mock_repo.register_token.assert_called_once_with(None, "tok-anon", "android")

    def test_defaults_device_type_when_not_given(self):
        mock_repo = MagicMock()
        usecase = RegisterDeviceTokenUseCase(mock_repo)

        usecase.execute(user_id=1, token="tok")

        mock_repo.register_token.assert_called_once_with(1, "tok", "android")


class TestUnregisterDeviceTokenUseCase:
    def test_delegates_to_repository_and_returns_true(self):
        mock_repo = MagicMock()
        mock_repo.unregister_token.return_value = True

        usecase = UnregisterDeviceTokenUseCase(mock_repo)
        result = usecase.execute(user_id=1, token="tok")

        mock_repo.unregister_token.assert_called_once_with(1, "tok")
        assert result is True

    def test_returns_false_when_repository_reports_not_found(self):
        mock_repo = MagicMock()
        mock_repo.unregister_token.return_value = False

        usecase = UnregisterDeviceTokenUseCase(mock_repo)
        result = usecase.execute(user_id=1, token="missing")

        assert result is False
