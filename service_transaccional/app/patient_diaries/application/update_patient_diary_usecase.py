from app.patient_diaries.domain.ports import IPatientDiaryRepository
from app.patient_diaries.domain.patient_diary_entity import PatientDiaryEntity

class UpdatePatientDiaryUseCase:
    def __init__(self, repository: IPatientDiaryRepository):
        self.repository = repository
        
    def execute(self, patient_diary_id: int, data: PatientDiaryEntity) -> PatientDiaryEntity:
        updated_diary = self.repository.update(patient_diary_id, data)
        if not updated_diary:
            raise ValueError("Patient diary not found")
        return updated_diary
