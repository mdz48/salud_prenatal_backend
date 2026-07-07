from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.features.medical_record.application.evaluate_patient_risk_usecase import (
    EvaluatePatientRiskUseCase,
)


def _patient(age=30):
    return SimpleNamespace(age=age)


def _record(medical_record_id=1, patient_id=5, **overrides):
    data = dict(
        medical_record_id=medical_record_id,
        patient_id=patient_id,
        height_cm=160,
        initial_weight=60.0,
        initial_systolic=118,
        initial_diastolic=76,
        patient_diaries=[],
    )
    data.update(overrides)
    return SimpleNamespace(**data)


def _usecase(record, patient, ml_result=None):
    mr_repo = MagicMock()
    mr_repo.get_by_id.return_value = record
    patient_repo = MagicMock()
    patient_repo.get_patient_info.return_value = patient
    ml = MagicMock()
    ml.predict.return_value = ml_result
    risk_repo = MagicMock()
    risk_repo.create.side_effect = lambda entity: entity  # devuelve lo que persiste
    return EvaluatePatientRiskUseCase(mr_repo, patient_repo, ml, risk_repo), ml, risk_repo


def test_evaluacion_ok_persiste_prediccion(monkeypatch):
    monkeypatch.setenv("ML_MODEL_VERSION", "v2.0.0")
    usecase, ml, risk_repo = _usecase(_record(), _patient(), ml_result={"cluster": 1})

    result = usecase.execute(1)

    assert result.status == "ok"
    assert result.prediction == {"cluster": 1}
    assert result.ml_model_version == "v2.0.0"
    assert result.medical_record_id == 1
    risk_repo.create.assert_called_once()


def test_datos_insuficientes_no_llama_al_ml():
    record = _record(initial_systolic=None, initial_diastolic=None)
    usecase, ml, risk_repo = _usecase(record, _patient())

    result = usecase.execute(1)

    assert result.status == "insufficient_data"
    assert result.missing_fields == ["systolic", "diastolic"]
    ml.predict.assert_not_called()
    risk_repo.create.assert_called_once()


def test_ml_caido_persiste_ml_unavailable():
    usecase, ml, risk_repo = _usecase(_record(), _patient(), ml_result=None)

    result = usecase.execute(1)

    assert result.status == "ml_unavailable"
    assert result.prediction is None
    ml.predict.assert_called_once()


def test_expediente_inexistente():
    usecase, _, _ = _usecase(None, _patient())

    with pytest.raises(ValueError, match="Medical record not found"):
        usecase.execute(999)


def test_paciente_inexistente():
    usecase, _, _ = _usecase(_record(), None)

    with pytest.raises(ValueError, match="Patient not found"):
        usecase.execute(1)
