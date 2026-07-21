"""E2E del directorio de pacientes (ADR-07): registra doctor + paciente, canjea
código de invitación (fija linked_at) y verifica el filtro por linked_after
a través de la ruta real."""
from datetime import datetime, timedelta


def _register_doctor(client, email):
    payload = {
        "name": "Doc",
        "last_name": "Tor",
        "email": email,
        "phone": "5512345678",
        "password": "secret123",
        "professional_license": "LIC-999",
        "specialty": "Ginecologia",
        "office": "Consultorio 1",
    }
    r = client.post("/api/v1/doctors/register", json=payload)
    assert r.status_code == 201, r.text
    return r.json()["doctor_id"]


def _register_patient(client, email):
    payload = {
        "name": "Pat",
        "last_name": "Ient",
        "email": email,
        "phone": "5512345679",
        "password": "secret123",
        "birthdate": "1995-05-05",
    }
    r = client.post("/api/v1/patients/register", json=payload)
    assert r.status_code == 201, r.text
    return r.json()["patient_id"]


def test_directory_reflects_linked_at_after_redeeming_invitation(client):
    doctor_id = _register_doctor(client, "directory.doc@example.com")
    patient_id = _register_patient(client, "directory.pat@example.com")

    r = client.post(f"/api/v1/doctors/{doctor_id}/invitation-code")
    assert r.status_code == 201, r.text
    code = r.json()["code"]

    r = client.post(f"/api/v1/patients/{patient_id}/redeem-code", json={"code": code})
    assert r.status_code == 200, r.text

    r = client.get(f"/api/v1/doctors/{doctor_id}/patients/directory")
    assert r.status_code == 200, r.text
    entries = r.json()
    assert len(entries) == 1
    assert entries[0]["patient_id"] == patient_id
    assert entries[0]["linked_at"] is not None

    future = (datetime.utcnow() + timedelta(days=1)).isoformat()
    r = client.get(f"/api/v1/doctors/{doctor_id}/patients/directory", params={"linked_after": future})
    assert r.status_code == 200, r.text
    assert r.json() == []
