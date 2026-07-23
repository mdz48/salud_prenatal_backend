"""Smoke del servicio usuarios: health, rutas, y flujo real doctor + dashboard
(que ejercita el read-model de appointments sobre la DB compartida)."""


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "service": "usuarios"}


def test_routes_present_and_login_absent(app):
    paths = set(app.openapi()["paths"])
    assert "/api/v1/doctors/register" in paths
    assert "/api/v1/patients/register" in paths
    assert "/api/v1/doctors/{doctor_id}/patients/{patient_id}" in paths
    # El login se movió al servicio auth: NO debe existir aquí.
    assert "/api/v1/users/login" not in paths
    # POST/GET /api/v1/users/ deshabilitada: sin auth, solo era para dev.
    assert "/api/v1/users/" not in paths


def test_register_doctor_and_dashboard(client):
    payload = {
        "name": "Ana",
        "last_name": "Lopez",
        "email": "ana.doc@example.com",
        "phone": "5512345678",
        "password": "secret123",
        "professional_license": "LIC-123",
        "specialty": "Ginecologia",
        "office": "Consultorio 1",
    }
    r = client.post("/api/v1/doctors/register", json=payload)
    assert r.status_code == 201, r.text
    doctor_id = r.json()["doctor_id"]

    doc_headers = {"X-User-Email": "ana.doc@example.com", "X-User-Role": "doctor"}

    # Dashboard del doctor: sin citas -> 0. Ejercita el read-model de appointments
    # (tabla vacía en la DB compartida de test) a través del lookup adapter.
    r2 = client.get(f"/api/v1/doctors/{doctor_id}/dashboard", headers=doc_headers)
    assert r2.status_code == 200, r2.text
    body = r2.json()
    assert body["today_appointments_count"] == 0
    assert body["today_appointments"] == []
