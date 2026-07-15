from typing import List

from app.features.patient_diaries.domain.ports import IDiarySymptomRepository
from app.features.patient_diaries.domain.extracted_symptom_entity import ExtractedSymptomEntity


class GetDiarySymptomsUseCase:
    def __init__(self, symptom_repository: IDiarySymptomRepository):
        self.symptom_repository = symptom_repository

    def execute(self, patient_diary_id: int) -> List[ExtractedSymptomEntity]:
        return self.symptom_repository.get_by_diary_id(patient_diary_id)
