from app.patient_diaries.domain.ports import IPatientDiaryRepository
from typing import List
from app.patient_diaries.domain.patient_diary_entity import PatientDiaryEntity

class GetDiariesByMedicalRecordUseCase:
    def __init__(self, repository: IPatientDiaryRepository):
        self.repository = repository
        
    def execute(self, medical_record_id: int) -> List[PatientDiaryEntity]:
        return self.repository.get_by_medical_record_id(medical_record_id)
