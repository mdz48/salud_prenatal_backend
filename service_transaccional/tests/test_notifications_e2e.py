import datetime
from app.readmodels.users_readmodels import PatientRead, DoctorRead, UserRead
from salud_prenatal_shared_core.enums import RoleEnum


def test_e2e_appointment_creation_triggers_observer_and_notifications_api(client, db_session):
    """Prueba E2E completa de notificaciones:
    1. Se siembran los read-models de usuario, médico (doctor_id=50 -> user_id=500) y paciente (patient_id=30 -> user_id=300).
    2. Se realiza una petición HTTP POST /api/v1/appointments/ como doctor activo para agendar una cita.
    3. El caso de uso emite AppointmentCreatedEvent.
    4. El Observer (NotificationLogObserver) intercepta el evento y persiste las notificaciones en la BD.
    5. Se consulta la API GET /api/v1/notifications/ con el header de usuario X-User-Id: 500 y se verifica la recepción.
    6. Se llama al endpoint PATCH /api/v1/notifications/{id}/read para marcar la notificación como leída.
    """
    # 1. Sembrar el estado de la DB compartida
    doc_user = UserRead(user_id=500, name="Dr. Carlos", last_name="Mendoza", email="doc@test.com", role=RoleEnum.doctor, is_active=True)
    pat_user = UserRead(user_id=300, name="Ana", last_name="Gómez", email="ana@test.com", role=RoleEnum.patient, is_active=True)
    doc_profile = DoctorRead(doctor_id=50, user_id=500)
    pat_profile = PatientRead(patient_id=30, user_id=300, doctor_id=50, birthdate=datetime.date(1995, 3, 15))

    db_session.add_all([doc_user, pat_user, doc_profile, pat_profile])
    db_session.commit()

    # 2. Petición HTTP POST para crear la cita por el doctor activo
    payload = {
        "patient_id": 30,
        "doctor_id": 50,
        "appointment_date": "2026-09-15T10:30:00",
        "reason": "Consulta de seguimiento prenatal",
    }
    doc_headers = {
        "X-User-Id": "500",
        "X-User-Email": "doc@test.com",
        "X-User-Role": "doctor",
        "X-Subscription-Status": "active",
    }

    response = client.post("/api/v1/appointments/", json=payload, headers=doc_headers)
    assert response.status_code == 201, f"Error creando cita: {response.text}"
    appointment_data = response.json()
    assert appointment_data["patient_id"] == 30
    assert appointment_data["doctor_id"] == 50

    # 3 & 4. Verificar consulta HTTP GET /api/v1/notifications/ para el doctor (X-User-Id: 500)
    notif_response = client.get("/api/v1/notifications/", headers=doc_headers)
    assert notif_response.status_code == 200
    notifications = notif_response.json()

    assert len(notifications) >= 1
    target_notif = notifications[0]
    assert target_notif["title"] == "Nueva Cita Agendada"
    assert target_notif["type"] == "appointment"
    assert target_notif["is_read"] is False

    # 5. Marcar notificación como leída mediante PATCH /api/v1/notifications/{id}/read
    notif_id = target_notif["id"]
    read_response = client.patch(f"/api/v1/notifications/{notif_id}/read", headers=doc_headers)
    assert read_response.status_code == 200
    assert read_response.json() == {"status": "success", "message": "Notification marked as read"}

    # 6. Re-consultar y confirmar que is_read es True
    updated_notif_response = client.get("/api/v1/notifications/", headers=doc_headers)
    assert updated_notif_response.status_code == 200
    updated_notifications = updated_notif_response.json()
    assert updated_notifications[0]["is_read"] is True


def test_internal_patient_linked_endpoint_requires_valid_token(client, db_session):
    """El endpoint interno /notifications/internal/patient-linked (llamado por
    service_usuarios) rechaza requests sin el X-Internal-Token correcto -- necesario
    porque el catch-all de transaccional en Traefik expone /api/v1 completo con
    jwt-auth (anónimo permitido), así que este endpoint no puede depender solo de
    la red del compose."""
    doc_user = UserRead(user_id=600, name="Dr. Ines", last_name="Ramirez", email="ines@test.com", role=RoleEnum.doctor, is_active=True)
    pat_user = UserRead(user_id=400, name="Lucia", last_name="Diaz", email="lucia@test.com", role=RoleEnum.patient, is_active=True)
    doc_profile = DoctorRead(doctor_id=60, user_id=600)
    pat_profile = PatientRead(patient_id=40, user_id=400, doctor_id=60, birthdate=datetime.date(1998, 1, 1))
    db_session.add_all([doc_user, pat_user, doc_profile, pat_profile])
    db_session.commit()

    payload = {"patient_id": 40, "doctor_id": 60}

    no_token_response = client.post("/api/v1/notifications/internal/patient-linked", json=payload)
    assert no_token_response.status_code == 403

    wrong_token_response = client.post(
        "/api/v1/notifications/internal/patient-linked",
        json=payload,
        headers={"X-Internal-Token": "wrong-token"},
    )
    assert wrong_token_response.status_code == 403

    ok_response = client.post(
        "/api/v1/notifications/internal/patient-linked",
        json=payload,
        headers={"X-Internal-Token": "test-internal-token"},
    )
    assert ok_response.status_code == 200

    doc_headers = {"X-User-Id": "600", "X-User-Email": "ines@test.com", "X-User-Role": "doctor", "X-Subscription-Status": "active"}
    notif_response = client.get("/api/v1/notifications/", headers=doc_headers)
    assert notif_response.status_code == 200
    titles = [n["title"] for n in notif_response.json()]
    assert "Nuevo Paciente Vinculado" in titles
