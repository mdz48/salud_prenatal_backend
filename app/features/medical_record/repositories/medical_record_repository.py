from sqlalchemy.orm import Session
from app.features.medical_record.models.medical_record_model import MedicalRecord

class MedicalRecordRepository:
    def get_by_patient_and_doctor(self, db: Session, patient_id: int, doctor_id: int):
        return db.query(MedicalRecord).filter(
            MedicalRecord.patient_id == patient_id,
            MedicalRecord.doctor_id == doctor_id
        ).first()

    def create(self, db: Session, data: dict, commit: bool = True):
        db_obj = MedicalRecord(**data)
        db.add(db_obj)
        if commit:
            db.commit()
            db.refresh(db_obj)
        else:
            db.flush()
        return db_obj

medical_record_repository = MedicalRecordRepository()
