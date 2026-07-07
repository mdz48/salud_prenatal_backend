from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import main  # noqa: F401  # registra todos los modelos en Base (mappers y create_all)
from app.core.database import Base
from app.core.enums import RoleEnum
from app.features.users.infrastructure.models.patient_model import Patient
from app.features.users.infrastructure.models.receptionist_model import Receptionist
from app.features.users.infrastructure.models.user_model import Usuario
from app.features.users.infrastructure.repositories.patient_repository import PatientRepository
from app.features.users.infrastructure.repositories.receptionist_repository import ReceptionistRepository


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


def _make_user(session, email, role=RoleEnum.patient, is_active=True):
    user = Usuario(
        name="Nombre", last_name="Apellido", email=email,
        password="hash", role=role, is_active=is_active,
    )
    session.add(user)
    session.commit()
    return user


def test_get_patients_by_doctor_excludes_inactive_users(db_session):
    active = _make_user(db_session, "activa@example.com")
    inactive = _make_user(db_session, "inactiva@example.com", is_active=False)
    for user in (active, inactive):
        db_session.add(
            Patient(user_id=user.user_id, doctor_id=77, birthdate=date(1995, 5, 4))
        )
    db_session.commit()

    patients = PatientRepository(db_session).get_patients_by_doctor(77)

    assert [p.user_id for p in patients] == [active.user_id]


def test_get_receptionists_by_doctor_excludes_inactive_users(db_session):
    active = _make_user(db_session, "recep-a@example.com", role=RoleEnum.recepcionist)
    inactive = _make_user(db_session, "recep-b@example.com", role=RoleEnum.recepcionist, is_active=False)
    for user in (active, inactive):
        db_session.add(Receptionist(user_id=user.user_id, doctor_id=77))
    db_session.commit()

    users = ReceptionistRepository(db_session).get_by_doctor_id(77)

    assert [u.user_id for u in users] == [active.user_id]


def test_verify_password_invalid_hash_returns_false():
    # Las cuentas anonimizadas por la admin API guardan "deleted::<token>" como password;
    # passlib lanza UnknownHashError con hashes irreconocibles y el login daria 500.
    from app.core.security import verify_password

    assert verify_password("cualquiera", "deleted::no-es-un-hash") is False
