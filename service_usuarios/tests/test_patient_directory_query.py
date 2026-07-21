from datetime import date, datetime, timedelta

from salud_prenatal_shared_core.database import Base, get_engine, get_session_factory
from app.users.infrastructure.models.patient_model import Patient
from app.users.infrastructure.models.user_model import Usuario
from app.users.infrastructure.models import doctor_model, receptionist_model  # noqa: F401 registra relaciones de Usuario
from app.users.infrastructure.repositories.patient_repository import PatientRepository
from app.users.domain.patient_directory_query import PatientDirectoryQuery
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


def test_search_directory_filters_by_doctor_id():
    db = setup_test_db()
    try:
        user_a = _make_user(db, "a@test.com")
        user_b = _make_user(db, "b@test.com")
        db.add_all([
            Patient(user_id=user_a.user_id, doctor_id=900001, birthdate=date(2000, 1, 1)),
            Patient(user_id=user_b.user_id, doctor_id=900002, birthdate=date(2000, 1, 1)),
        ])
        db.commit()

        repo = PatientRepository(db=db)
        result = repo.search_directory(PatientDirectoryQuery(doctor_id=900001))

        assert len(result) == 1
        assert result[0].doctor_id == 900001
    finally:
        db.close()


def test_search_directory_filters_by_patient_ids_subset():
    db = setup_test_db()
    try:
        u1 = _make_user(db, "c@test.com")
        u2 = _make_user(db, "d@test.com")
        p1 = Patient(user_id=u1.user_id, doctor_id=900005, birthdate=date(2000, 1, 1))
        p2 = Patient(user_id=u2.user_id, doctor_id=900005, birthdate=date(2000, 1, 1))
        db.add_all([p1, p2])
        db.commit()
        db.refresh(p1)
        db.refresh(p2)

        repo = PatientRepository(db=db)
        result = repo.search_directory(PatientDirectoryQuery(doctor_id=900005, patient_ids_filter=[p1.patient_id]))

        assert len(result) == 1
        assert result[0].patient_id == p1.patient_id
    finally:
        db.close()


def test_search_directory_empty_patient_ids_filter_yields_no_results():
    db = setup_test_db()
    try:
        u1 = _make_user(db, "e@test.com")
        db.add(Patient(user_id=u1.user_id, doctor_id=900007, birthdate=date(2000, 1, 1)))
        db.commit()

        repo = PatientRepository(db=db)
        result = repo.search_directory(PatientDirectoryQuery(doctor_id=900007, patient_ids_filter=[]))

        assert result == []
    finally:
        db.close()


def test_search_directory_filters_by_linked_at_range():
    db = setup_test_db()
    try:
        u1 = _make_user(db, "f@test.com")
        u2 = _make_user(db, "g@test.com")
        now = datetime(2026, 7, 1, 12, 0)
        old = now - timedelta(days=60)
        db.add_all([
            Patient(user_id=u1.user_id, doctor_id=900009, birthdate=date(2000, 1, 1), linked_at=now),
            Patient(user_id=u2.user_id, doctor_id=900009, birthdate=date(2000, 1, 1), linked_at=old),
        ])
        db.commit()

        repo = PatientRepository(db=db)
        result = repo.search_directory(
            PatientDirectoryQuery(doctor_id=900009, linked_after=now - timedelta(days=1))
        )

        assert len(result) == 1
        assert result[0].user_id == u1.user_id
    finally:
        db.close()
