from app.features.patient_diaries.domain.ports import IPatientDiaryRepository
from app.features.patient_diaries.domain.entities import PatientDiaryEntity

class CreatePatientDiaryUseCase:
    def __init__(self, repository: IPatientDiaryRepository):
        self.repository = repository
        
    def execute(self, data: PatientDiaryEntity) -> PatientDiaryEntity:
        return self.repository.create(data)
