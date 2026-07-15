from app.patient_diaries.domain.ports import IPatientDiaryRepository
from typing import List
from app.patient_diaries.domain.patient_diary_entity import PatientDiaryEntity

class GetAllPatientDiariesUseCase:
    def __init__(self, repository: IPatientDiaryRepository):
        self.repository = repository
        
    def execute(self, skip: int = 0, limit: int = 100) -> List[PatientDiaryEntity]:
        return self.repository.get_all(skip=skip, limit=limit)
