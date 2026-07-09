from types import SimpleNamespace
from unittest.mock import MagicMock

from app.features.forums.infrastructure.adapters.patient_cluster_adapter import PatientClusterAdapter


def _adapter(patient=None, record=None, prediction=None):
    patient_repo = MagicMock()
    patient_repo.get_by_user_id.return_value = patient
    mr_repo = MagicMock()
    mr_repo.get_by_patient_id.return_value = record
    risk_repo = MagicMock()
    risk_repo.get_latest_ok_for_medical_record.return_value = prediction
    return PatientClusterAdapter(patient_repo, mr_repo, risk_repo)


def test_devuelve_cluster_de_ultima_prediccion_ok():
    adapter = _adapter(
        patient=SimpleNamespace(patient_id=5),
        record=SimpleNamespace(medical_record_id=9),
        prediction=SimpleNamespace(prediction={"risk_cluster": 3}),
    )

    assert adapter.get_cluster_by_user_id(1) == "3"


def test_sin_paciente_devuelve_none():
    assert _adapter(patient=None).get_cluster_by_user_id(1) is None


def test_sin_expediente_devuelve_none():
    adapter = _adapter(patient=SimpleNamespace(patient_id=5), record=None)
    assert adapter.get_cluster_by_user_id(1) is None


def test_sin_prediccion_ok_devuelve_none():
    adapter = _adapter(
        patient=SimpleNamespace(patient_id=5),
        record=SimpleNamespace(medical_record_id=9),
        prediction=None,
    )
    assert adapter.get_cluster_by_user_id(1) is None


def test_prediccion_sin_risk_cluster_devuelve_none():
    adapter = _adapter(
        patient=SimpleNamespace(patient_id=5),
        record=SimpleNamespace(medical_record_id=9),
        prediction=SimpleNamespace(prediction={"otro": 1}),
    )
    assert adapter.get_cluster_by_user_id(1) is None
