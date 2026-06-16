from sqlalchemy.orm import Session
from app.users.schemas.doctor_schema import DoctorRegistration
from app.core.security import get_password_hash
from app.core.enums import RoleEnum
from app.users.respositories.user_repository import user_repository
from app.users.respositories.doctor_repository import doctor_repository

class DoctorService:
    def register_doctor(self, db: Session, data: DoctorRegistration):
        existing_user = user_repository.get_by_email(db, data.email)
        if existing_user:
            raise ValueError("Email already registered")
        
        user_data = {
            "name": data.name,
            "last_name": data.last_name,
            "email": data.email,
            "phone": data.phone,
            "role": RoleEnum.doctor,
            "is_active": True,
            "password": get_password_hash(data.password)
        }
        
        try:
            db_user = user_repository.create_from_dict(db, user_data, commit=False)
            
            doctor_data_dict = data.model_dump(exclude={"name", "last_name", "email", "phone", "password", "role", "is_active", "image_url"})
            doctor_data_dict["user_id"] = db_user.user_id
            
            db_doctor = doctor_repository.create(db, doctor_data_dict, commit=False)
            
            db.commit()
            db.refresh(db_user)
            db.refresh(db_doctor)
            
            return db_doctor
        except Exception as e:
            db.rollback()
            raise e

doctor_service = DoctorService()
