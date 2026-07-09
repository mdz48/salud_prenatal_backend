from datetime import datetime
from unittest.mock import MagicMock

from app.features.medical_record.domain.dtos import LatestDiary
from app.features.medical_record.infrastructure.adapters.latest_diary_adapter import LatestDiaryAdapter
from app.features.patient_diaries.domain.patient_diary_entity import PatientDiaryEntity


def test_mapea_la_bitacora_mas_reciente_a_latest_diary():
    repo = MagicMock()
    repo.get_latest_by_medical_record_id.return_value = PatientDiaryEntity(
        patient_diary_id=9,
        medical_record_id=1,
        created_at=datetime(2026, 7, 5, 8, 0),
        systolic=130,
        diastolic=85,
        weight_kg=63.0,
        weight_gain=3.0,
    )
    adapter = LatestDiaryAdapter(repo)

    result = adapter.get_latest_diary_for_medical_record(1)

    repo.get_latest_by_medical_record_id.assert_called_once_with(1)
    assert isinstance(result, LatestDiary)
    assert result.created_at == datetime(2026, 7, 5, 8, 0)
    assert result.systolic == 130
    assert result.diastolic == 85
    assert result.weight_kg == 63.0
    assert result.weight_gain == 3.0


def test_sin_bitacora_devuelve_none():
    repo = MagicMock()
    repo.get_latest_by_medical_record_id.return_value = None
    adapter = LatestDiaryAdapter(repo)

    assert adapter.get_latest_diary_for_medical_record(1) is None
