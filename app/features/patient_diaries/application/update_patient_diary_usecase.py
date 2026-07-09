from app.features.patient_diaries.application.patient_diary_validator import PatientDiaryValidator
from app.features.patient_diaries.domain.ports import IPatientDiaryRepository
from app.features.patient_diaries.domain.patient_diary_entity import PatientDiaryEntity

class UpdatePatientDiaryUseCase:
    def __init__(self, repository: IPatientDiaryRepository):
        self.repository = repository
        self.validator = PatientDiaryValidator()

    def execute(self, patient_diary_id: int, data: PatientDiaryEntity) -> PatientDiaryEntity:
        self.validator.validate(data).raise_if_errors()
        updated_diary = self.repository.update(patient_diary_id, data)
        if not updated_diary:
            raise ValueError("Patient diary not found")
        return updated_diary
