from unittest.mock import MagicMock

import pytest
from dependency_injector import providers
from fastapi import HTTPException
from fastapi.testclient import TestClient

from main import app, container
from app.core.dependencies import get_current_user, get_current_user_optional


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def fake_controller():
    controller = MagicMock()
    with container.notification_controller.override(providers.Object(controller)):
        yield controller


@pytest.fixture(autouse=True)
def _clear_dependency_overrides():
    yield
    app.dependency_overrides.clear()


class TestRegisterEndpoint:
    def test_register_without_auth_header_succeeds(self, client, fake_controller):
        fake_controller.register_token.return_value = {"status": "ok"}

        response = client.post("/api/v1/notifications/register", json={"token": "tok-1"})

        assert response.status_code == 201
        _, kwargs = fake_controller.register_token.call_args
        assert kwargs["user_id"] is None

    def test_register_with_auth_header_forwards_user_id(self, client, fake_controller):
        # get_current_user_optional en sí ya se prueba end-to-end (JWT real)
        # en test_get_current_user_optional.py; acá solo se valida el wiring
        # del router: si la dependencia resuelve un usuario, se lo pasa al
        # controller como user_id.
        fake_controller.register_token.return_value = {"status": "ok"}
        fake_user = MagicMock(user_id=42)
        app.dependency_overrides[get_current_user_optional] = lambda: fake_user

        response = client.post(
            "/api/v1/notifications/register",
            json={"token": "tok-1"},
            headers={"Authorization": "Bearer irrelevant-porque-esta-overrideado"},
        )

        assert response.status_code == 201
        _, kwargs = fake_controller.register_token.call_args
        assert kwargs["user_id"] == 42

    def test_register_missing_token_field_returns_422(self, client, fake_controller):
        response = client.post("/api/v1/notifications/register", json={})
        assert response.status_code == 422
        fake_controller.register_token.assert_not_called()

    def test_register_defaults_device_type_to_android(self, client, fake_controller):
        fake_controller.register_token.return_value = {"status": "ok"}

        client.post("/api/v1/notifications/register", json={"token": "tok-1"})

        _, kwargs = fake_controller.register_token.call_args
        assert kwargs["data"].device_type == "android"

    def test_register_propagates_controller_error_status(self, client, fake_controller):
        fake_controller.register_token.side_effect = HTTPException(status_code=500, detail="boom")

        response = client.post("/api/v1/notifications/register", json={"token": "tok-1"})

        assert response.status_code == 500


class TestUnregisterEndpoint:
    def test_unregister_without_auth_header_returns_401(self, client, fake_controller):
        response = client.post("/api/v1/notifications/unregister", json={"token": "tok-1"})
        assert response.status_code == 401
        fake_controller.unregister_token.assert_not_called()

    def test_unregister_with_auth_succeeds(self, client, fake_controller):
        fake_controller.unregister_token.return_value = {"status": "success"}
        fake_user = MagicMock(user_id=1)
        app.dependency_overrides[get_current_user] = lambda: fake_user

        response = client.post("/api/v1/notifications/unregister", json={"token": "tok-1"})

        assert response.status_code == 200
        _, kwargs = fake_controller.unregister_token.call_args
        assert kwargs["user_id"] == 1

    def test_unregister_not_found_returns_404(self, client, fake_controller):
        fake_controller.unregister_token.side_effect = HTTPException(status_code=404, detail="not found")
        app.dependency_overrides[get_current_user] = lambda: MagicMock(user_id=1)

        response = client.post("/api/v1/notifications/unregister", json={"token": "tok-1"})

        assert response.status_code == 404

    def test_unregister_missing_token_field_returns_422(self, client, fake_controller):
        app.dependency_overrides[get_current_user] = lambda: MagicMock(user_id=1)

        response = client.post("/api/v1/notifications/unregister", json={})

        assert response.status_code == 422
