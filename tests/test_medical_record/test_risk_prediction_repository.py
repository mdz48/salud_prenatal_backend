import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import main  # noqa: F401  # registra todos los modelos en Base (mappers y create_all)
from app.core.database import Base
from app.features.medical_record.domain.risk_prediction_entity import RiskPredictionEntity
from app.features.medical_record.infrastructure.repositories.risk_prediction_repository import (
    RiskPredictionRepository,
)


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


def test_create_y_get_latest(db_session):
    repo = RiskPredictionRepository(db_session)

    primera = repo.create(RiskPredictionEntity(medical_record_id=1, status="insufficient_data", missing_fields=["systolic"]))
    segunda = repo.create(RiskPredictionEntity(medical_record_id=1, status="ok", prediction={"cluster": 1}, ml_model_version="v2.0.0"))
    repo.create(RiskPredictionEntity(medical_record_id=2, status="ml_unavailable"))

    assert primera.risk_prediction_id is not None
    assert primera.predicted_at is not None

    # La ultima del expediente 1 es la segunda (desempate por id ante timestamps iguales)
    latest = repo.get_latest_for_medical_record(1)
    assert latest.risk_prediction_id == segunda.risk_prediction_id
    assert latest.status == "ok"
    assert latest.prediction == {"cluster": 1}
    assert latest.ml_model_version == "v2.0.0"


def test_get_latest_sin_filas_devuelve_none(db_session):
    assert RiskPredictionRepository(db_session).get_latest_for_medical_record(999) is None


def test_get_latest_ok_ignora_fallos_posteriores(db_session):
    repo = RiskPredictionRepository(db_session)
    ok = repo.create(RiskPredictionEntity(medical_record_id=1, status="ok", prediction={"risk_cluster": 3}))
    repo.create(RiskPredictionEntity(medical_record_id=1, status="ml_unavailable"))

    latest_ok = repo.get_latest_ok_for_medical_record(1)

    assert latest_ok.risk_prediction_id == ok.risk_prediction_id
    assert latest_ok.prediction == {"risk_cluster": 3}


def test_get_latest_ok_sin_exitosas_devuelve_none(db_session):
    repo = RiskPredictionRepository(db_session)
    repo.create(RiskPredictionEntity(medical_record_id=1, status="insufficient_data", missing_fields=["systolic"]))

    assert repo.get_latest_ok_for_medical_record(1) is None
