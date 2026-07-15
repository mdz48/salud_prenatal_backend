import pytest

# Endpoints que no deben responder 500 (aunque respondan 401/404/422 sin datos)
ENDPOINTS = [
    ("POST", "/api/v1/users/login", {"json": {"email": "test@test.com", "password": "password"}}),
    ("GET", "/api/v1/patients/1/dashboard", {}),
    ("GET", "/api/v1/doctors/1/patients", {}),
    ("GET", "/api/v1/doctors/1/receptionists", {}),
    ("GET", "/api/v1/medical-records/patient/1", {}),
    ("GET", "/api/v1/patient-diaries/", {}),
    ("GET", "/api/v1/patient-diaries/medical-record/1", {}),
    ("GET", "/api/v1/patient-diaries/1", {}),
]


@pytest.mark.integration
@pytest.mark.parametrize("method,url,kwargs", ENDPOINTS)
def test_endpoint_no_500(client, method, url, kwargs):
    response = client.request(method, url, **kwargs)
    assert response.status_code != 500, response.text
