from sqlalchemy.orm import Session
from app.features.users.repositories.patient_repository import patient_repository
from app.features.medical_record.repositories.medical_record_repository import medical_record_repository
from app.features.medical_record.schemas.medical_record_schema import MedicalRecordCreate

class MedicalRecordService:
    def create_medical_record(self, db: Session, data: MedicalRecordCreate):
        patient = patient_repository.get_by_id(db, data.patient_id)
        if not patient:
            raise ValueError("Patient not found")
        if not patient.doctor_id:
            raise ValueError("Patient is not linked to a doctor")
        if patient.doctor_id != data.doctor_id:
            raise ValueError("Patient is not linked to this doctor")
        existing = medical_record_repository.get_by_patient_and_doctor(db, data.patient_id, data.doctor_id)
        if existing:
            raise ValueError("A medical record already exists for this patient with this doctor")
        mr_data = data.model_dump()
        return medical_record_repository.create(db, mr_data)

    def get_patient_medical_record(self, db: Session, patient_id: int, doctor_id: int):
        patient = patient_repository.get_by_id(db, patient_id)
        if not patient:
            raise ValueError("Patient not found")

        medical_record = medical_record_repository.get_by_patient_and_doctor(db, patient_id, doctor_id)

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
            "medical_record": medical_record,
            "consultations": consultations_list
        }

medical_record_service = MedicalRecordService()
