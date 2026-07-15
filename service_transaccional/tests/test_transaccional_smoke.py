"""Smoke + verificación de adapters cross-servicio (Sesión 6).

Lo central del corte: los adapters que antes llamaban a repos del servicio users/
subscriptions ahora LEEN la DB compartida vía read-models. Se prueban directo,
sembrando filas en las tablas `users`/`patients`/`subscriptions`.
"""
import datetime

from salud_prenatal_shared_core.enums import RoleEnum, PlanTypeEnum, SubscriptionStatusEnum


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "service": "transaccional"}


def test_key_routes_present(app):
    paths = app.openapi()["paths"]
    joined = "\n".join(paths.keys())
    for frag in ["/api/v1/appointments", "/api/v1/chat", "/api/v1/medical-record",
                 "/api/v1/notifications"]:
        assert any(p.startswith(frag) for p in paths), f"falta ruta {frag} en:\n{joined}"


def test_patient_info_adapter_reads_shared_db(db_session):
    """PatientInfoAdapter resuelve nombre/edad cruzando users+patients de la DB
    compartida (antes: repo del servicio usuarios)."""
    from app.readmodels.users_readmodels import UserRead, PatientRead
    from app.medical_record.infrastructure.adapters.patient_info_adapter import PatientInfoAdapter

    user = UserRead(name="María", last_name="Pérez", email="maria@example.com",
                    role=RoleEnum.patient, is_active=True)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    patient = PatientRead(user_id=user.user_id, doctor_id=7,
                          birthdate=datetime.date(1995, 5, 20))
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)

    info = PatientInfoAdapter(db_session).get_patient_info(patient.patient_id)
    assert info is not None
    assert info.name == "María"
    assert info.last_name == "Pérez"
    assert info.doctor_id == 7
    assert info.age is not None  # derivada de birthdate


def test_ad_eligibility_reads_subscription(db_session):
    """AdEligibilityAdapter lee plan_type+status de `subscriptions` (el claim no
    trae plan_type). Premium+active -> elegible; basic -> no."""
    from app.readmodels.subscriptions_readmodels import SubscriptionRead
    from app.forums.infrastructure.adapters.ad_eligibility_adapter import AdEligibilityAdapter

    db_session.add(SubscriptionRead(user_id=101, plan_type=PlanTypeEnum.premium,
                                    status=SubscriptionStatusEnum.active))
    db_session.add(SubscriptionRead(user_id=102, plan_type=PlanTypeEnum.basic,
                                    status=SubscriptionStatusEnum.active))
    db_session.commit()

    adapter = AdEligibilityAdapter(db_session)
    assert adapter.is_premium_active(101) is True
    assert adapter.is_premium_active(102) is False
    assert adapter.is_premium_active(999) is False  # sin fila


def test_appointment_patient_doctor_lookup(db_session):
    """Los lookups de appointments verifican existencia de paciente/doctor sobre
    la DB compartida."""
    from app.readmodels.users_readmodels import PatientRead, DoctorRead
    from app.appointments.infrastructure.adapters.patient_doctor_lookup_adapter import (
        PatientLookupAdapter,
        DoctorLookupAdapter,
    )

    db_session.add(PatientRead(user_id=1, doctor_id=1, birthdate=datetime.date(1990, 1, 1)))
    db_session.add(DoctorRead(user_id=2))
    db_session.commit()

    assert PatientLookupAdapter(db_session).get_by_id(1) is not None
    assert PatientLookupAdapter(db_session).get_by_id(999) is None
    assert DoctorLookupAdapter(db_session).get_by_id(1) is not None
