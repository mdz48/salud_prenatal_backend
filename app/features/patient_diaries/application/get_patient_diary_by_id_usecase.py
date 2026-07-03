from app.features.patient_diaries.domain.ports import IPatientDiaryRepository
from app.features.patient_diaries.domain.patient_diary_entity import PatientDiaryEntity

class GetPatientDiaryByIdUseCase:
    def __init__(self, repository: IPatientDiaryRepository):
        self.repository = repository
        
    def execute(self, patient_diary_id: int) -> PatientDiaryEntity:
        diary = self.repository.get_by_id(patient_diary_id)
        if not diary:
            raise ValueError("Patient diary not found")
        return diary
