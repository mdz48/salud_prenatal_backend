from sqlalchemy.orm import Session
from app.features.users.schemas.patient_schema import PatientRegistration
from app.core.security import get_password_hash
from app.core.enums import RoleEnum
from app.features.users.repositories.user_repository import user_repository
from app.features.users.repositories.patient_repository import patient_repository

class PatientService:
    def register_patient(self, db: Session, data: PatientRegistration):
        existing_user = user_repository.get_by_email(db, data.email)
        if existing_user:
            raise ValueError("Email already registered")
        
        user_data = {
            "name": data.name,
            "last_name": data.last_name,
            "email": data.email,
            "phone": data.phone,
            "role": RoleEnum.patient,
            "is_active": True,
            "password": get_password_hash(data.password)
        }
        
        try:
            db_user = user_repository.create_from_dict(db, user_data, commit=False)
            
            patient_data_dict = data.model_dump(exclude={"name", "last_name", "email", "phone", "password", "role", "is_active", "image_url"})
            patient_data_dict["user_id"] = db_user.user_id
            
            db_patient = patient_repository.create(db, patient_data_dict, commit=False)
            
            db.commit()
            db.refresh(db_user)
            db.refresh(db_patient)
            
            return db_patient
        except Exception as e:
            db.rollback()
            raise e

patient_service = PatientService()
