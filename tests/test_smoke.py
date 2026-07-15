def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_route_snapshot(app):
    # Guardian de la migracion: la API publica /api/v1/... no debe cambiar.
    # Se usa openapi() porque FastAPI difiere la resolucion de routers incluidos
    # (_IncludedRouter) hasta que se construye el schema; app.routes no expone .path aun.
    actual = sorted(p for p in app.openapi()["paths"] if p.startswith("/api"))
    assert actual == EXPECTED_ROUTES


EXPECTED_ROUTES = [
    "/api/v1/appointments/",
    "/api/v1/appointments/doctor/{doctor_id}",
    "/api/v1/appointments/patient/{patient_id}",
    "/api/v1/appointments/{appointment_id}",
    "/api/v1/chat/contacts",
    "/api/v1/chat/history/{other_user_id}",
    "/api/v1/chat/inbox",
    "/api/v1/consultations/",
    "/api/v1/consultations/medical-record/{medical_record_id}",
    "/api/v1/doctors/receptionists/{receptionist_id}",
    "/api/v1/doctors/receptionists/{receptionist_id}/dashboard",
    "/api/v1/doctors/register",
    "/api/v1/doctors/{doctor_id}",
    "/api/v1/doctors/{doctor_id}/dashboard",
    "/api/v1/doctors/{doctor_id}/invitation-code",
    "/api/v1/doctors/{doctor_id}/patients",
    "/api/v1/doctors/{doctor_id}/patients/search",
    "/api/v1/doctors/{doctor_id}/receptionists",
    "/api/v1/forums/comments",
    "/api/v1/forums/groups",
    "/api/v1/forums/groups/recommended",
    "/api/v1/forums/groups/{group_id}/posts",
    "/api/v1/forums/posts",
    "/api/v1/forums/posts/global",
    "/api/v1/forums/posts/recommended",
    "/api/v1/forums/posts/{post_id}/comments",
    "/api/v1/forums/profiles",
    "/api/v1/forums/profiles/me",
    "/api/v1/forums/profiles/{user_id}",
    "/api/v1/forums/profiles/{user_id}/timeline",
    "/api/v1/forums/reports",
    "/api/v1/medical-records/",
    "/api/v1/medical-records/patient/{patient_id}",
    "/api/v1/medical-records/search",
    "/api/v1/medical-records/{medical_record_id}",
    "/api/v1/medical-records/{medical_record_id}/risk-evaluation",
    "/api/v1/notifications/register",
    "/api/v1/notifications/unregister",
    "/api/v1/patient-diaries/",
    "/api/v1/patient-diaries/medical-record/{medical_record_id}",
    "/api/v1/patient-diaries/medical-record/{medical_record_id}/symptoms",
    "/api/v1/patient-diaries/{patient_diary_id}",
    "/api/v1/patient-diaries/{patient_diary_id}/symptoms",
    "/api/v1/patients/register",
    "/api/v1/patients/{patient_id}/dashboard",
    "/api/v1/patients/{patient_id}/redeem-code",
    "/api/v1/subscriptions/checkout-session",
    "/api/v1/subscriptions/me",
    "/api/v1/subscriptions/portal-session",
    "/api/v1/subscriptions/webhook",
    "/api/v1/users/",
    "/api/v1/users/login",
    "/api/v1/users/{user_id}",
]
