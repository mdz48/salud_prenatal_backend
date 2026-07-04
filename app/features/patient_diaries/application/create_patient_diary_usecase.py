from app.features.patient_diaries.domain.ports import IPatientDiaryRepository
from app.features.patient_diaries.domain.patient_diary_entity import PatientDiaryEntity

class CreatePatientDiaryUseCase:
    def __init__(self, repository: IPatientDiaryRepository):
        self.repository = repository
        
    def execute(self, data: PatientDiaryEntity) -> PatientDiaryEntity:
        return self.repository.create(data)
