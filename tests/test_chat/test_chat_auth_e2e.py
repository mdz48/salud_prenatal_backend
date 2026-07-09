import pytest
from starlette.websockets import WebSocketDisconnect

from app.features.chat.infrastructure.websocket_manager import manager

# E2E: el chat (WS + REST) deja de confiar en un user_id provisto por el cliente;
# el usuario se deriva siempre del JWT.


def _register_two_patients(client, suffix):
    a = client.post(
        "/api/v1/patients/register",
        json={
            "name": "Ana",
            "last_name": "Ruiz",
            "email": f"ana.chat.{suffix}@test.com",
            "password": "secret123",
            "role": "paciente",
            "birthdate": "1995-04-10",
        },
    )
    assert a.status_code == 201, a.text
    b = client.post(
        "/api/v1/patients/register",
        json={
            "name": "Luis",
            "last_name": "Paz",
            "email": f"luis.chat.{suffix}@test.com",
            "password": "secret123",
            "role": "paciente",
            "birthdate": "1993-01-01",
        },
    )
    assert b.status_code == 201, b.text
    return a.json()["patient_id"], b.json()["patient_id"]


def _login(client, email, password="secret123"):
    resp = client.post("/api/v1/users/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest.mark.integration
def test_inbox_requires_auth(client):
    assert client.get("/api/v1/chat/inbox").status_code == 401


@pytest.mark.integration
def test_inbox_uses_user_from_token(client):
    _register_two_patients(client, "inbox")
    token = _login(client, "ana.chat.inbox@test.com")
    resp = client.get("/api/v1/chat/inbox", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.integration
def test_ws_rejects_missing_token(client):
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/api/v1/chat/ws"):
            pass


@pytest.mark.integration
def test_ws_rejects_invalid_token(client):
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/api/v1/chat/ws?token=not-a-real-token"):
            pass


@pytest.mark.integration
def test_ws_connects_and_derives_user_from_token(client):
    id_a, _ = _register_two_patients(client, "ws")
    token_a = _login(client, "ana.chat.ws@test.com")

    # Conecta con un token valido y verifica que el manager registra el user_id
    # derivado del token, no uno que el cliente pudiera inventar.
    with client.websocket_connect(f"/api/v1/chat/ws?token={token_a}"):
        assert id_a in manager.active_connections
