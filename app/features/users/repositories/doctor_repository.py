from sqlalchemy.orm import Session
from app.features.users.models.doctor_model import Doctor

class DoctorRepository:
    def get_by_id(self, db: Session, doctor_id: int):
        return db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()

    def get_by_user_id(self, db: Session, user_id: int):
        return db.query(Doctor).filter(Doctor.user_id == user_id).first()

    def create(self, db: Session, doctor_data: dict, commit: bool = True):
        db_doctor = Doctor(**doctor_data)
        db.add(db_doctor)
        if commit:
            db.commit()
            db.refresh(db_doctor)
        else:
            db.flush()
        return db_doctor

doctor_repository = DoctorRepository()
