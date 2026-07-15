from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.features.notifications.infrastructure.controllers.notification_controller import (
    NotificationController,
)
from app.features.notifications.infrastructure.schemas.notification_schema import (
    DeviceTokenCreate,
    DeviceTokenUnregister,
)


@pytest.fixture
def register_use_case():
    return MagicMock()


@pytest.fixture
def unregister_use_case():
    return MagicMock()


@pytest.fixture
def controller(register_use_case, unregister_use_case):
    return NotificationController(register_use_case, unregister_use_case)


class TestRegisterToken:
    def test_success_with_user_id(self, controller, register_use_case):
        register_use_case.execute.return_value = {"id": 1}
        data = DeviceTokenCreate(token="tok", device_type="android")

        result = controller.register_token(user_id=1, data=data)

        register_use_case.execute.assert_called_once_with(
            user_id=1, token="tok", device_type="android"
        )
        assert result == {"id": 1}

    def test_success_with_anonymous_user(self, controller, register_use_case):
        # Sin sesión iniciada: user_id llega como None desde el router.
        data = DeviceTokenCreate(token="tok-anon")

        controller.register_token(user_id=None, data=data)

        register_use_case.execute.assert_called_once_with(
            user_id=None, token="tok-anon", device_type="android"
        )

    def test_wraps_unexpected_errors_as_500(self, controller, register_use_case):
        register_use_case.execute.side_effect = RuntimeError("db down")
        data = DeviceTokenCreate(token="tok")

        with pytest.raises(HTTPException) as exc_info:
            controller.register_token(user_id=1, data=data)

        assert exc_info.value.status_code == 500


class TestUnregisterToken:
    def test_success(self, controller, unregister_use_case):
        unregister_use_case.execute.return_value = True
        data = DeviceTokenUnregister(token="tok")

        result = controller.unregister_token(user_id=1, data=data)

        assert result == {"status": "success", "message": "Token unregistered successfully."}

    def test_raises_404_when_not_found(self, controller, unregister_use_case):
        unregister_use_case.execute.return_value = False
        data = DeviceTokenUnregister(token="tok")

        with pytest.raises(HTTPException) as exc_info:
            controller.unregister_token(user_id=1, data=data)

        assert exc_info.value.status_code == 404

    def test_wraps_unexpected_errors_as_500(self, controller, unregister_use_case):
        unregister_use_case.execute.side_effect = RuntimeError("db down")
        data = DeviceTokenUnregister(token="tok")

        with pytest.raises(HTTPException) as exc_info:
            controller.unregister_token(user_id=1, data=data)

        assert exc_info.value.status_code == 500

    def test_does_not_double_wrap_404_as_500(self, controller, unregister_use_case):
        # Regresión: el 404 no debe terminar re-envuelto como 500 por el
        # except genérico.
        unregister_use_case.execute.return_value = False
        data = DeviceTokenUnregister(token="tok")

        with pytest.raises(HTTPException) as exc_info:
            controller.unregister_token(user_id=1, data=data)

        assert exc_info.value.status_code != 500
