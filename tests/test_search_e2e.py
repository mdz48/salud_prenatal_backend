import pytest

# E2E de los endpoints de busqueda por nombre/apellido: ejercita el filtrado
# en Python sobre columnas cifradas (Fernet) y el wiring DI de los use cases.


@pytest.mark.integration
def test_search_patients_and_medical_records_by_name(client):
    doctor_resp = client.post(
        "/api/v1/doctors/register",
        json={
            "name": "Elena",
            "last_name": "Rios",
            "email": "dr.search.e2e@test.com",
            "password": "secret123",
            "role": "doctor",
            "professional_license": "LIC-456",
            "specialty": "Obstetricia",
        },
    )
    assert doctor_resp.status_code == 201, doctor_resp.text
    doctor_id = doctor_resp.json()["doctor_id"]

    patient_resp = client.post(
        "/api/v1/patients/register",
        json={
            "name": "María",
            "last_name": "López",
            "email": "paciente.search.e2e@test.com",
            "password": "secret123",
            "role": "paciente",
            "birthdate": "1995-04-10",
            "residence": "urbana",
            "doctor_id": doctor_id,
        },
    )
    assert patient_resp.status_code == 201, patient_resp.text
    patient_id = patient_resp.json()["patient_id"]

    record_resp = client.post(
        "/api/v1/medical-records/",
        json={"patient_id": patient_id, "doctor_id": doctor_id},
    )
    assert record_resp.status_code == 201, record_resp.text

    # Busqueda parcial ignorando mayusculas y acentos ("maria" encuentra "María")
    search_resp = client.get(
        f"/api/v1/doctors/{doctor_id}/patients/search",
        params={"name": "maria"},
    )
    assert search_resp.status_code == 200, search_resp.text
    results = search_resp.json()
    assert len(results) == 1
    assert results[0]["patient_id"] == patient_id
    assert results[0]["name"] == "María"
    assert results[0]["last_name"] == "López"

    # Sin criterios -> 400
    empty_resp = client.get(f"/api/v1/doctors/{doctor_id}/patients/search")
    assert empty_resp.status_code == 400

    # Expediente por apellido de la paciente
    record_search_resp = client.get(
        "/api/v1/medical-records/search",
        params={"doctor_id": doctor_id, "last_name": "lopez"},
    )
    assert record_search_resp.status_code == 200, record_search_resp.text
    record_results = record_search_resp.json()
    assert len(record_results) == 1
    assert record_results[0]["patient_id"] == patient_id
    assert record_results[0]["name"] == "María"
    assert record_results[0]["medical_record"]["patient_id"] == patient_id

    # Apellido que no coincide -> lista vacia
    no_match_resp = client.get(
        "/api/v1/medical-records/search",
        params={"doctor_id": doctor_id, "last_name": "ramirez"},
    )
    assert no_match_resp.status_code == 200
    assert no_match_resp.json() == []
