from app.features.users.domain.ports import IUserRepository, IDoctorRepository
from app.features.users.domain.user_entity import UserEntity
from app.features.users.domain.doctor_entity import DoctorEntity
from app.features.users.infrastructure.schemas.doctor_schema import DoctorRegistration
from app.core.security import get_password_hash
from app.core.enums import RoleEnum

class RegisterDoctorUseCase:
    def __init__(self, user_repository: IUserRepository, doctor_repository: IDoctorRepository):
        self.user_repository = user_repository
        self.doctor_repository = doctor_repository

    def execute(self, data: DoctorRegistration) -> DoctorEntity:
        existing_user = self.user_repository.get_by_email(data.email)
        if existing_user:
            raise ValueError("Email already registered")
        
        user_entity = UserEntity(
            name=data.name,
            last_name=data.last_name,
            email=data.email,
            phone=data.phone,
            role=RoleEnum.doctor,
            is_active=True,
            password=get_password_hash(data.password)
        )
        
        db_user = self.user_repository.create(user_entity)
        
        doctor_entity = DoctorEntity(
            user_id=db_user.user_id,
            professional_license=data.professional_license,
            specialty=data.specialty,
            office=data.office
        )
        
        db_doctor = self.doctor_repository.create(doctor_entity)
        return db_doctor
