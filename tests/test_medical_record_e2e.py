import time

import pytest

# E2E del flujo medical_record: ejercita PatientInfoAdapter contra la BD de test
# (registro real -> expediente real -> GET que cruza users via el port),
# mas el flujo de evaluacion de riesgo (boton del doctor -> historial persistido).


@pytest.mark.integration
def test_medical_record_flow_exercises_patient_info_adapter(client, monkeypatch):
    # Sin ML_SERVICE_URL la evaluacion es determinista: persiste ml_unavailable.
    # setenv("") y no delenv: load_dotenv() corre en request-time (get_secret_key)
    # y repondria la variable del .env local; una var existente no la sobreescribe.
    monkeypatch.setenv("ML_SERVICE_URL", "")
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
            "initial_systolic": 118,
            "initial_diastolic": 76,
        },
    )
    assert record_resp.status_code == 201, record_resp.text
    medical_record_id = record_resp.json()["medical_record_id"]

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
    assert body["medical_record"]["initial_systolic"] == 118
    assert body["medical_record"]["initial_diastolic"] == 76
    # Sin evaluacion todavia -> null (estado "sin evaluar" para el front)
    assert body["risk_prediction"] is None

    # --- Evaluacion de riesgo (boton del doctor, requiere Bearer de doctor) ---
    login_resp = client.post(
        "/api/v1/users/login",
        json={"email": "dr.e2e@test.com", "password": "secret123"},
    )
    assert login_resp.status_code == 200, login_resp.text
    headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    # Sin token -> 401 (endpoint protegido)
    assert client.post(f"/api/v1/medical-records/{medical_record_id}/risk-evaluation").status_code == 401

    eval_resp = client.post(
        f"/api/v1/medical-records/{medical_record_id}/risk-evaluation", headers=headers
    )
    assert eval_resp.status_code == 201, eval_resp.text
    eval_body = eval_resp.json()
    # Datos completos (presion basal presente) pero sin servicio ML -> ml_unavailable
    assert eval_body["status"] == "ml_unavailable"
    assert eval_body["predicted_at"] is not None

    # El GET ahora refleja la ultima evaluacion persistida, sin llamar al ML
    get2 = client.get(
        f"/api/v1/medical-records/patient/{patient_id}", params={"doctor_id": doctor_id}
    )
    rp = get2.json()["risk_prediction"]
    assert rp["status"] == "ml_unavailable"
    assert rp["stale"] is False

    # Una bitacora posterior marca la evaluacion como vieja (stale)
    time.sleep(1.1)  # timestamps de SQLite tienen precision de segundo
    diary_resp = client.post(
        "/api/v1/patient-diaries/",
        json={"medical_record_id": medical_record_id, "weight_kg": 62.0, "systolic": 120, "diastolic": 80},
    )
    assert diary_resp.status_code == 201, diary_resp.text

    get3 = client.get(
        f"/api/v1/medical-records/patient/{patient_id}", params={"doctor_id": doctor_id}
    )
    assert get3.json()["risk_prediction"]["stale"] is True

    # Expediente inexistente -> 404
    assert client.post("/api/v1/medical-records/99999/risk-evaluation", headers=headers).status_code == 404
