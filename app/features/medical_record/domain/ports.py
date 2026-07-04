from typing import Protocol, Optional
from .medical_record_entity import MedicalRecordEntity

class IMedicalRecordRepository(Protocol):
    def get_by_patient_and_doctor(self, patient_id: int, doctor_id: int) -> Optional[MedicalRecordEntity]:
        ...
        
    def get_by_id(self, medical_record_id: int) -> Optional[MedicalRecordEntity]:
        ...

    def create(self, data: MedicalRecordEntity) -> MedicalRecordEntity:
        ...

    def update(self, medical_record_id: int, data: MedicalRecordEntity) -> Optional[MedicalRecordEntity]:
        ...

class IPatientRepository(Protocol):
    # Depending on how Patient is implemented in its own domain.
    # We might just return a dict or a generic object here for cross-domain since Patient domain may not be refactored by us.
    # Actually, we can assume it returns an object that has necessary attributes.
    def get_by_id(self, patient_id: int) -> Optional[object]:
        ...

class IMLPredictionService(Protocol):
    def predict(self, patient: object, medical_record: MedicalRecordEntity, latest_diary: Optional[object]) -> Optional[dict]:
        ...
