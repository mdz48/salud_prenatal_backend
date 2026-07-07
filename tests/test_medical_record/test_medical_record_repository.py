import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import main  # noqa: F401  # registra todos los modelos en Base
from app.core.database import Base
from app.features.medical_record.infrastructure.models.medical_record_model import MedicalRecord
from app.features.medical_record.infrastructure.repositories.medical_record_repository import (
    MedicalRecordRepository,
)


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


def test_get_by_patient_id(db_session):
    db_session.add(MedicalRecord(patient_id=5, doctor_id=2))
    db_session.commit()
    repo = MedicalRecordRepository(db_session)

    record = repo.get_by_patient_id(5)

    assert record is not None
    assert record.patient_id == 5


def test_get_by_patient_id_inexistente(db_session):
    assert MedicalRecordRepository(db_session).get_by_patient_id(404) is None
