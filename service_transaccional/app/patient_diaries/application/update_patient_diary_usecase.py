from app.patient_diaries.domain.ports import IPatientDiaryRepository
from app.patient_diaries.domain.patient_diary_entity import PatientDiaryEntity
from app.patient_diaries.domain.diary_validation import validate_diary_measurements, PatientDiaryValidationError

class UpdatePatientDiaryUseCase:
    def __init__(self, repository: IPatientDiaryRepository):
        self.repository = repository

    def execute(self, patient_diary_id: int, data: PatientDiaryEntity) -> PatientDiaryEntity:
        notification = validate_diary_measurements(data)
        if notification.has_errors():
            raise PatientDiaryValidationError(notification.errors)

        updated_diary = self.repository.update(patient_diary_id, data)
        if not updated_diary:
            raise ValueError("Patient diary not found")
        return updated_diary
