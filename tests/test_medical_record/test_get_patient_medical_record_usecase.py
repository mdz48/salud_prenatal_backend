from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.features.medical_record.application.get_patient_medical_record_usecase import GetPatientMedicalRecordUseCase


def _make_usecase(medical_record, latest_eval=None, latest_diary=None):
    mr_repo = MagicMock()
    mr_repo.get_by_patient_and_doctor.return_value = medical_record

    patient_repo = MagicMock()
    patient_mock = MagicMock()
    patient_mock.user_id = 1
    patient_mock.name = "Test"
    patient_mock.last_name = "User"
    patient_mock.age = 30
    patient_mock.doctor_id = 2
    patient_repo.get_patient_info.return_value = patient_mock

    risk_repo = MagicMock()
    risk_repo.get_latest_for_medical_record.return_value = latest_eval

    latest_diary_repo = MagicMock()
    latest_diary_repo.get_latest_diary_for_medical_record.return_value = latest_diary

    return GetPatientMedicalRecordUseCase(mr_repo, patient_repo, risk_repo, latest_diary_repo), mr_repo, risk_repo, latest_diary_repo


def _record():
    mr = MagicMock()
    mr.medical_record_id = 7
    mr.current_gestational_weeks = 20  # vive en el expediente
    mr.consultations = [MagicMock(consultation_id=1, created_at="2023-01-01")]
    return mr


def _eval(status="ok", predicted_at=None):
    return SimpleNamespace(
        status=status,
        prediction={"cluster": 1} if status == "ok" else None,
        missing_fields=None,
        predicted_at=predicted_at or datetime(2026, 7, 1, 10, 0),
        ml_model_version="v2.0.0",
    )


def test_get_devuelve_ultima_evaluacion_sin_llamar_al_ml():
    usecase, mr_repo, risk_repo, latest_diary_repo = _make_usecase(_record(), latest_eval=_eval())

    result = usecase.execute(patient_id=1, doctor_id=2)

    assert result["user_id"] == 1
    assert result["current_gestational_weeks"] == 20
    assert result["age"] == 30
    assert len(result["consultations"]) == 1
    rp = result["risk_prediction"]
    assert rp["status"] == "ok"
    assert rp["prediction"] == {"cluster": 1}
    assert rp["model_version"] == "v2.0.0"
    assert rp["stale"] is False  # sin bitacoras posteriores
    mr_repo.get_by_patient_and_doctor.assert_called_once_with(1, 2)
    risk_repo.get_latest_for_medical_record.assert_called_once_with(7)
    # La bitacora mas reciente se obtiene con una consulta dedicada, no cargando toda la coleccion
    latest_diary_repo.get_latest_diary_for_medical_record.assert_called_once_with(7)


def test_stale_true_si_hay_bitacora_posterior_a_la_evaluacion():
    diary = SimpleNamespace(created_at=datetime(2026, 7, 2, 9, 0))
    usecase, _, _, _ = _make_usecase(
        _record(),
        latest_eval=_eval(predicted_at=datetime(2026, 7, 1, 10, 0)),
        latest_diary=diary,
    )

    result = usecase.execute(patient_id=1, doctor_id=2)

    assert result["risk_prediction"]["stale"] is True


def test_sin_evaluacion_previa_risk_prediction_es_none():
    usecase, _, _, _ = _make_usecase(_record(), latest_eval=None)

    result = usecase.execute(patient_id=1, doctor_id=2)

    assert result["risk_prediction"] is None


def test_get_patient_medical_record_patient_not_found():
    usecase, _, _, _ = _make_usecase(_record())
    usecase.patient_repository.get_patient_info.return_value = None

    with pytest.raises(ValueError, match="Patient not found"):
        usecase.execute(patient_id=1, doctor_id=2)


def test_patient_sin_relacion_con_el_doctor():
    usecase, _, _, _ = _make_usecase(_record())
    usecase.patient_repository.get_patient_info.return_value.doctor_id = 99

    with pytest.raises(ValueError, match="no tiene una relaci"):
        usecase.execute(patient_id=1, doctor_id=2)


def test_relacion_existe_pero_expediente_no_ha_sido_creado():
    usecase, mr_repo, _, _ = _make_usecase(_record())
    mr_repo.get_by_patient_and_doctor.return_value = None

    with pytest.raises(ValueError, match="expediente"):
        usecase.execute(patient_id=1, doctor_id=2)
