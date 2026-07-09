from app.features.patient_diaries.application.patient_diary_validator import PatientDiaryValidator
from app.features.patient_diaries.domain.ports import IPatientDiaryRepository
from app.features.patient_diaries.domain.patient_diary_entity import PatientDiaryEntity

class CreatePatientDiaryUseCase:
    def __init__(self, repository: IPatientDiaryRepository):
        self.repository = repository
        self.validator = PatientDiaryValidator()

    def execute(self, data: PatientDiaryEntity) -> PatientDiaryEntity:
        self.validator.validate(data).raise_if_errors()
        return self.repository.create(data)
