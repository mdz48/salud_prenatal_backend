from datetime import datetime
from typing import List, Optional

from app.features.medical_record.domain.ports import IDiarySymptomSummaryPort
from app.features.medical_record.domain.dtos import SymptomSummary
from app.features.patient_diaries.infrastructure.repositories.diary_symptom_extraction_repository import (
    DiarySymptomExtractionRepository,
)
from app.features.patient_diaries.domain.symptom_aggregation import aggregate_symptoms


class DiarySymptomSummaryAdapter(IDiarySymptomSummaryPort):
    """Cruza los sintomas extraidos desde `patient_diaries` hacia el expediente,
    agregados y acotados por marca de agua. Unico punto que toca el otro feature."""

    def __init__(self, diary_symptom_repository: DiarySymptomExtractionRepository):
        self.diary_symptom_repository = diary_symptom_repository

    def get_symptom_summary(self, medical_record_id: int, since: Optional[datetime]) -> List[SymptomSummary]:
        rows = self.diary_symptom_repository.get_by_medical_record_id(medical_record_id, since=since)
        return [SymptomSummary.model_validate(a, from_attributes=True) for a in aggregate_symptoms(rows)]
