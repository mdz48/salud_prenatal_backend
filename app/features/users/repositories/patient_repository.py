from sqlalchemy.orm import Session
from app.features.users.models.patient_model import Patient

class PatientRepository:
    def get_by_id(self, db: Session, patient_id: int):
        return db.query(Patient).filter(Patient.patient_id == patient_id).first()

    def get_by_user_id(self, db: Session, user_id: int):
        return db.query(Patient).filter(Patient.user_id == user_id).first()

    def get_by_doctor_id(self, db: Session, doctor_id: int):
        return db.query(Patient).filter(Patient.doctor_id == doctor_id).all()

    def create(self, db: Session, patient_data: dict, commit: bool = True):
        db_patient = Patient(**patient_data)
        db.add(db_patient)
        if commit:
            db.commit()
            db.refresh(db_patient)
        else:
            db.flush()
        return db_patient

patient_repository = PatientRepository()
