"""Flujo de solicitud de desvinculación paciente -> doctor.

Cubre el camino feliz (solicitar -> el doctor la ve -> aprobar -> la paciente
queda sin doctor) más los rechazos esperados: duplicado (409), aprobar dos
veces (409) y solicitar sin doctor asignado (400)."""


def _register_doctor(client, email="doc.unlink@example.com"):
    payload = {
        "name": "Ana", "last_name": "Lopez", "email": email,
        "phone": "5512345678", "password": "secret123",
        "professional_license": "LIC-UNLINK", "specialty": "Ginecologia",
        "office": "Consultorio 1",
    }
    r = client.post("/api/v1/doctors/register", json=payload)
    assert r.status_code == 201, r.text
    return r.json()["doctor_id"]


def _register_patient(client, doctor_id=None, email="pac.unlink@example.com"):
    payload = {
        "name": "Lau", "last_name": "Vel", "email": email,
        "phone": "5599998888", "password": "secret123",
        "birthdate": "1998-05-20",
    }
    if doctor_id is not None:
        payload["doctor_id"] = doctor_id
    r = client.post("/api/v1/patients/register", json=payload)
    assert r.status_code == 201, r.text
    return r.json()["patient_id"]


def test_full_unlink_request_flow(client):
    doctor_id = _register_doctor(client)
    patient_id = _register_patient(client, doctor_id=doctor_id)

    # 1. La paciente solicita la desvinculación.
    r = client.post(f"/api/v1/patients/{patient_id}/unlink-requests", json={"reason": "Cambio de ciudad"})
    assert r.status_code == 201, r.text
    req = r.json()
    assert req["status"] == "pending"
    assert req["doctor_id"] == doctor_id
    request_id = req["unlink_request_id"]

    # 2. No se permite una segunda solicitud pendiente para el mismo par.
    r_dup = client.post(f"/api/v1/patients/{patient_id}/unlink-requests", json={})
    assert r_dup.status_code == 409, r_dup.text

    # 3. El doctor la ve en su bandeja pendiente, con el nombre resuelto.
    r_list = client.get(f"/api/v1/doctors/{doctor_id}/unlink-requests?status=pending")
    assert r_list.status_code == 200, r_list.text
    listed = r_list.json()
    assert len(listed) == 1
    assert listed[0]["unlink_request_id"] == request_id
    assert listed[0]["patient_full_name"] == "Lau Vel"

    # 4. El doctor aprueba -> se ejecuta la desvinculación real.
    r_res = client.patch(
        f"/api/v1/doctors/{doctor_id}/unlink-requests/{request_id}",
        json={"status": "approved"},
    )
    assert r_res.status_code == 200, r_res.text
    assert r_res.json()["status"] == "approved"
    assert r_res.json()["resolved_at"] is not None

    # 5. La paciente ya no aparece en la lista del doctor.
    r_patients = client.get(f"/api/v1/doctors/{doctor_id}/patients")
    assert r_patients.status_code == 200, r_patients.text
    assert all(p["patient_id"] != patient_id for p in r_patients.json())

    # 6. Resolver otra vez la misma solicitud -> 409.
    r_again = client.patch(
        f"/api/v1/doctors/{doctor_id}/unlink-requests/{request_id}",
        json={"status": "rejected"},
    )
    assert r_again.status_code == 409, r_again.text


def test_request_without_doctor_is_rejected(client):
    # Paciente sin doctor asignado no puede solicitar desvinculación.
    patient_id = _register_patient(client, doctor_id=None, email="pac.nodoc@example.com")
    r = client.post(f"/api/v1/patients/{patient_id}/unlink-requests", json={})
    assert r.status_code == 400, r.text
