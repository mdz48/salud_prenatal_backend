from typing import List

from app.features.patient_diaries.domain.ports import IDiarySymptomRepository
from app.features.patient_diaries.domain.symptom_aggregation import aggregate_symptoms, AggregatedSymptom


class GetMedicalRecordSymptomHistoryUseCase:
    """Historial completo de sintomas del embarazo (RF-31), sin marca de agua.
    Alimenta el boton de historial del expediente."""

    def __init__(self, symptom_repository: IDiarySymptomRepository):
        self.symptom_repository = symptom_repository

    def execute(self, medical_record_id: int) -> List[AggregatedSymptom]:
        rows = self.symptom_repository.get_by_medical_record_id(medical_record_id)
        return aggregate_symptoms(rows)
