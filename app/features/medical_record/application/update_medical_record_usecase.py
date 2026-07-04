from app.features.medical_record.domain.ports import IMedicalRecordRepository
from app.features.medical_record.domain.medical_record_entity import MedicalRecordEntity

class UpdateMedicalRecordUseCase:
    def __init__(self, medical_record_repository: IMedicalRecordRepository):
        self.medical_record_repository = medical_record_repository

    def execute(self, medical_record_id: int, data: MedicalRecordEntity) -> MedicalRecordEntity:
        existing = self.medical_record_repository.get_by_id(medical_record_id)
        if not existing:
            raise ValueError("Medical record not found")

        updated_record = self.medical_record_repository.update(medical_record_id, data)
        if not updated_record:
            raise ValueError("Failed to update medical record")

        return updated_record
