from typing import Optional
from app.features.users.domain.ports import IMedicalRecordLookup
from app.features.medical_record.infrastructure.repositories.medical_record_repository import MedicalRecordRepository

class MedicalRecordLookupAdapter(IMedicalRecordLookup):
    def __init__(self, medical_record_repository: MedicalRecordRepository):
        self.medical_record_repository = medical_record_repository
        
    def get_medical_record_id(self, patient_id: int, doctor_id: int) -> Optional[int]:
        mr = self.medical_record_repository.get_by_patient_and_doctor(patient_id, doctor_id)
        return mr.medical_record_id if mr else None
