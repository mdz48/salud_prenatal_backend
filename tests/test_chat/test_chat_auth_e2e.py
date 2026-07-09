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
    return a.json()["user_id"], b.json()["user_id"]


def _login(client, email, password="secret123"):
    resp = client.post("/api/v1/users/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def _register_chat_contacts_fixture(client, suffix):
    doctor_email = f"doctor.contacts.{suffix}@test.com"
    receptionist_email = f"recep.contacts.{suffix}@test.com"
    patient_email = f"patient.contacts.{suffix}@test.com"

    doctor_resp = client.post(
        "/api/v1/doctors/register",
        json={
            "name": "Dra",
            "last_name": "Lopez",
            "email": doctor_email,
            "password": "secret123",
            "role": "doctor",
            "professional_license": f"LIC-{suffix}",
            "specialty": "Ginecologia",
            "office": "A1",
        },
    )
    assert doctor_resp.status_code == 201, doctor_resp.text
    doctor_id = doctor_resp.json()["doctor_id"]
    doctor_user_id = doctor_resp.json()["user_id"]

    receptionist_resp = client.post(
        f"/api/v1/doctors/{doctor_id}/receptionists",
        json={
            "name": "Rosa",
            "last_name": "Marin",
            "email": receptionist_email,
            "password": "secret123",
        },
    )
    assert receptionist_resp.status_code == 201, receptionist_resp.text
    receptionist_user_id = receptionist_resp.json()["user_id"]

    patient_resp = client.post(
        "/api/v1/patients/register",
        json={
            "name": "Ana",
            "last_name": "Ruiz",
            "email": patient_email,
            "password": "secret123",
            "role": "paciente",
            "birthdate": "1995-04-10",
            "doctor_id": doctor_id,
        },
    )
    assert patient_resp.status_code == 201, patient_resp.text
    patient_user_id = patient_resp.json()["user_id"]

    return {
        "doctor_email": doctor_email,
        "doctor_user_id": doctor_user_id,
        "receptionist_email": receptionist_email,
        "receptionist_user_id": receptionist_user_id,
        "patient_email": patient_email,
        "patient_user_id": patient_user_id,
    }


@pytest.mark.integration
def test_inbox_requires_auth(client):
    assert client.get("/api/v1/chat/inbox").status_code == 401


@pytest.mark.integration
def test_contacts_requires_auth(client):
    assert client.get("/api/v1/chat/contacts").status_code == 401


@pytest.mark.integration
def test_inbox_uses_user_from_token(client):
    _register_two_patients(client, "inbox")
    token = _login(client, "ana.chat.inbox@test.com")
    resp = client.get("/api/v1/chat/inbox", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.integration
def test_contacts_uses_authenticated_role_and_profile(client):
    data = _register_chat_contacts_fixture(client, "roles")

    doctor_token = _login(client, data["doctor_email"])
    doctor_resp = client.get(
        "/api/v1/chat/contacts", headers={"Authorization": f"Bearer {doctor_token}"}
    )
    assert doctor_resp.status_code == 200, doctor_resp.text
    doctor_contacts = sorted(doctor_resp.json(), key=lambda contact: contact["role"])
    assert doctor_contacts == [
        {
            "user_id": data["patient_user_id"],
            "name": "Ana",
            "last_name": "Ruiz",
            "role": "paciente",
        },
        {
            "user_id": data["receptionist_user_id"],
            "name": "Rosa",
            "last_name": "Marin",
            "role": "recepcionista",
        },
    ]

    receptionist_token = _login(client, data["receptionist_email"])
    receptionist_resp = client.get(
        "/api/v1/chat/contacts",
        headers={"Authorization": f"Bearer {receptionist_token}"},
    )
    assert receptionist_resp.status_code == 200, receptionist_resp.text
    receptionist_contacts = sorted(
        receptionist_resp.json(), key=lambda contact: contact["role"]
    )
    assert receptionist_contacts == [
        {
            "user_id": data["doctor_user_id"],
            "name": "Dra",
            "last_name": "Lopez",
            "role": "doctor",
        },
        {
            "user_id": data["patient_user_id"],
            "name": "Ana",
            "last_name": "Ruiz",
            "role": "paciente",
        },
    ]

    patient_token = _login(client, data["patient_email"])
    patient_resp = client.get(
        "/api/v1/chat/contacts", headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert patient_resp.status_code == 200, patient_resp.text
    assert patient_resp.json() == [
        {
            "user_id": data["doctor_user_id"],
            "name": "Dra",
            "last_name": "Lopez",
            "role": "doctor",
        },
        {
            "user_id": data["receptionist_user_id"],
            "name": "Rosa",
            "last_name": "Marin",
            "role": "recepcionista",
        },
    ]


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
