from sqlalchemy.orm import Session
from app.features.users.repositories.patient_repository import patient_repository

class MedicalRecordService:
    def get_patient_medical_record(self, db: Session, patient_id: int):
        patient = patient_repository.get_by_id(db, patient_id)
        if not patient:
            raise ValueError("Patient not found")
        
        consultations_list = []
        if patient.consultations:
            for consultation in patient.consultations:
                consultations_list.append({
                    "consultation_id": consultation.consultation_id,
                    "created_at": consultation.created_at
                })
        
        return {
            "user_id": patient.user_id,
            "name": patient.user.name,
            "last_name": patient.user.last_name,
            "current_gestational_weeks": patient.current_gestational_weeks,
            "age": patient.age,
            "medical_record": patient.medical_record,
            "consultations": consultations_list
        }

medical_record_service = MedicalRecordService()
