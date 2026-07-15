from datetime import datetime
from unittest.mock import MagicMock

from app.features.patient_diaries.domain.extracted_symptom_entity import ExtractedSymptomEntity
from app.features.medical_record.infrastructure.adapters.diary_symptom_summary_adapter import (
    DiarySymptomSummaryAdapter,
)
from app.features.medical_record.domain.dtos import SymptomSummary


def test_adapter_pasa_el_since_y_mapea_al_dto():
    repo = MagicMock()
    repo.get_by_medical_record_id.return_value = [
        ExtractedSymptomEntity(code="CEFALEA", alarm=True, created_at=datetime(2026, 6, 25, 8, 0)),
    ]
    adapter = DiarySymptomSummaryAdapter(repo)

    corte = datetime(2026, 6, 20, 8, 0)
    result = adapter.get_symptom_summary(medical_record_id=10, since=corte)

    repo.get_by_medical_record_id.assert_called_once_with(10, since=corte)
    assert len(result) == 1
    assert isinstance(result[0], SymptomSummary)
    assert result[0].code == "CEFALEA"
    assert result[0].occurrences == 1
    assert result[0].alarm is True


def test_adapter_con_since_none_devuelve_todo():
    repo = MagicMock()
    repo.get_by_medical_record_id.return_value = []
    adapter = DiarySymptomSummaryAdapter(repo)

    result = adapter.get_symptom_summary(medical_record_id=10, since=None)

    repo.get_by_medical_record_id.assert_called_once_with(10, since=None)
    assert result == []
