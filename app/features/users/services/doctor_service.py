from sqlalchemy.orm import Session
from app.features.users.schemas.doctor_schema import DoctorRegistration
from app.core.security import get_password_hash
from app.core.enums import RoleEnum
from app.features.users.repositories.user_repository import user_repository
from app.features.users.repositories.doctor_repository import doctor_repository
from app.features.users.repositories.invitation_code_repository import invitation_code_repository
from app.features.users.schemas.receptionist_schema import ReceptionistCreate

from app.features.users.models.receptionist_model import Receptionist

class DoctorService:
    def create_receptionist(self, db: Session, doctor_id: int, data: ReceptionistCreate):
        doctor = doctor_repository.get_by_id(db, doctor_id)
        if not doctor:
            raise ValueError("Doctor not found")
            
        existing_user = user_repository.get_by_email(db, data.email)
        if existing_user:
            raise ValueError("Email already registered")
            
        user_data = {
            "name": data.name,
            "last_name": data.last_name,
            "email": data.email,
            "phone": data.phone,
            "role": RoleEnum.recepcionist,
            "is_active": True,
            "password": get_password_hash(data.password)
        }
        
        try:
            db_user = user_repository.create_from_dict(db, user_data, commit=False)
            
            db_receptionist = Receptionist(
                user_id=db_user.user_id,
                doctor_id=doctor_id
            )
            db.add(db_receptionist)
            
            db.commit()
            db.refresh(db_user)
            return db_user
        except Exception as e:
            db.rollback()
            raise e

    def get_receptionists_by_doctor(self, db: Session, doctor_id: int):
        from app.features.users.models.user_model import Usuario
        
        doctor = doctor_repository.get_by_id(db, doctor_id)
        if not doctor:
            raise ValueError("Doctor not found")
            
        return db.query(Usuario).join(Receptionist).filter(Receptionist.doctor_id == doctor_id).all()

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

    def generate_invitation_code(self, db: Session, doctor_id: int):
        doctor = doctor_repository.get_by_id(db, doctor_id)
        if not doctor:
            raise ValueError("Doctor not found")
        return invitation_code_repository.create(db, doctor_id)

doctor_service = DoctorService()
