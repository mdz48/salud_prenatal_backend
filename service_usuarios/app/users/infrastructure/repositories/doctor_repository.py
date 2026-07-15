from sqlalchemy.orm import Session
from app.users.infrastructure.models.doctor_model import Doctor
from app.users.domain.ports import IDoctorRepository
from app.users.domain.doctor_entity import DoctorEntity
from typing import Optional

class DoctorRepository(IDoctorRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, doctor_id: int) -> Optional[DoctorEntity]:
        db_doctor = self.db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
        return DoctorEntity.model_validate(db_doctor) if db_doctor else None

    def get_by_user_id(self, user_id: int) -> Optional[DoctorEntity]:
        db_doctor = self.db.query(Doctor).filter(Doctor.user_id == user_id).first()
        return DoctorEntity.model_validate(db_doctor) if db_doctor else None

    def create(self, doctor: DoctorEntity) -> DoctorEntity:
        doctor_data = doctor.model_dump(exclude={'doctor_id'}, exclude_unset=True)
        db_doctor = Doctor(**doctor_data)
        self.db.add(db_doctor)
        self.db.commit()
        self.db.refresh(db_doctor)
        return DoctorEntity.model_validate(db_doctor)

    def update(self, doctor_id: int, doctor_data: DoctorEntity) -> Optional[DoctorEntity]:
        db_doctor = self.db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
        if not db_doctor:
            return None
        
        update_data = doctor_data.model_dump(exclude={'doctor_id'}, exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_doctor, key, value)
            
        self.db.commit()
        self.db.refresh(db_doctor)
        return DoctorEntity.model_validate(db_doctor)
