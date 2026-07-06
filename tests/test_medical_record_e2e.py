import pytest

# E2E del flujo medical_record: ejercita PatientInfoAdapter contra la BD de test
# (registro real -> expediente real -> GET que cruza users via el port).


@pytest.mark.integration
def test_medical_record_flow_exercises_patient_info_adapter(client):
    doctor_resp = client.post(
        "/api/v1/doctors/register",
        json={
            "name": "Gregorio",
            "last_name": "Casas",
            "email": "dr.e2e@test.com",
            "password": "secret123",
            "role": "doctor",
            "professional_license": "LIC-123",
            "specialty": "Obstetricia",
        },
    )
    assert doctor_resp.status_code == 201, doctor_resp.text
    doctor_id = doctor_resp.json()["doctor_id"]

    # Registro de paciente: solo identidad + birthdate + liga (lo clinico ya no va aqui).
    patient_resp = client.post(
        "/api/v1/patients/register",
        json={
            "name": "Maria",
            "last_name": "Lopez",
            "email": "paciente.e2e@test.com",
            "password": "secret123",
            "role": "paciente",
            "birthdate": "1995-04-10",
            "doctor_id": doctor_id,
        },
    )
    assert patient_resp.status_code == 201, patient_resp.text
    patient_id = patient_resp.json()["patient_id"]

    # El clinico se captura al CREAR el expediente (lo hace el doctor).
    record_resp = client.post(
        "/api/v1/medical-records/",
        json={
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "residence": "urbana",
            "height_cm": 160,
            "initial_weight": 60.5,
            "weeks_at_registration": 12,
        },
    )
    assert record_resp.status_code == 201, record_resp.text

    # GET cruza a users via IPatientInfoPort/PatientInfoAdapter (nombre desde patient.user);
    # lo clinico + semanas de gestacion salen del expediente.
    get_resp = client.get(
        f"/api/v1/medical-records/patient/{patient_id}",
        params={"doctor_id": doctor_id},
    )
    assert get_resp.status_code == 200, get_resp.text
    body = get_resp.json()
    assert body["name"] == "Maria"
    assert body["last_name"] == "Lopez"
    assert body["age"] is not None
    assert body["current_gestational_weeks"] == 12
    assert body["medical_record"]["residence"] == "urbana"
    assert body["medical_record"]["height_cm"] == 160
