from app.medical_record.domain.ports import IMedicalRecordRepository, IPatientInfoPort
from app.medical_record.domain.medical_record_entity import MedicalRecordEntity

class CreateMedicalRecordUseCase:
    def __init__(self, medical_record_repository: IMedicalRecordRepository, patient_repository: IPatientInfoPort):
        self.medical_record_repository = medical_record_repository
        self.patient_repository = patient_repository

    def execute(self, data: MedicalRecordEntity) -> MedicalRecordEntity:
        patient = self.patient_repository.get_patient_info(data.patient_id)
        if not patient:
            raise ValueError("Patient not found")
        if not patient.doctor_id:
            raise ValueError("Patient is not linked to a doctor")
        if patient.doctor_id != data.doctor_id:
            raise ValueError("Patient is not linked to this doctor")
            
        existing = self.medical_record_repository.get_by_patient_and_doctor(data.patient_id, data.doctor_id)
        if existing:
            raise ValueError("A medical record already exists for this patient with this doctor")
            
        return self.medical_record_repository.create(data)
