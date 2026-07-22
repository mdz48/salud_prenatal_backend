from datetime import date, datetime

from salud_prenatal_shared_core.database import Base, get_engine, get_session_factory
from app.users.infrastructure.models.patient_model import Patient
from app.users.infrastructure.models.user_model import Usuario
from app.users.infrastructure.models import doctor_model, receptionist_model  # noqa: F401
from app.users.infrastructure.repositories.patient_repository import PatientRepository
from salud_prenatal_shared_core.enums import RoleEnum


def setup_test_db():
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    return get_session_factory()()


def _make_user(db, email):
    user = Usuario(name="N", last_name="L", email=email, password="x", role=RoleEnum.patient, is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_update_doctor_sets_linked_at_when_linking():
    db = setup_test_db()
    try:
        user = _make_user(db, "linkme@test.com")
        patient = Patient(user_id=user.user_id, doctor_id=None, birthdate=date(2000, 1, 1))
        db.add(patient)
        db.commit()
        db.refresh(patient)

        repo = PatientRepository(db=db)
        updated = repo.update_doctor(patient.patient_id, 42)

        assert updated.doctor_id == 42
        assert updated.linked_at is not None
    finally:
        db.close()


def test_update_doctor_clears_linked_at_when_unlinking():
    db = setup_test_db()
    try:
        user = _make_user(db, "unlinkme@test.com")
        patient = Patient(user_id=user.user_id, doctor_id=42, birthdate=date(2000, 1, 1), linked_at=datetime(2026, 1, 1))
        db.add(patient)
        db.commit()
        db.refresh(patient)

        repo = PatientRepository(db=db)
        updated = repo.update_doctor(patient.patient_id, None)

        assert updated.doctor_id is None
        assert updated.linked_at is None
    finally:
        db.close()
