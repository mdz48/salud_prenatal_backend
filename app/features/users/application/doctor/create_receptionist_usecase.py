from app.features.users.domain.ports import IUserRepository, IDoctorRepository, IReceptionistRepository
from app.features.users.domain.user_entity import UserEntity
from app.features.users.domain.receptionist_entity import ReceptionistEntity
from app.features.users.application.dtos import ReceptionistCreateDTO
from app.core.security import get_password_hash
from app.core.enums import RoleEnum

class CreateReceptionistUseCase:
    def __init__(self, user_repository: IUserRepository, doctor_repository: IDoctorRepository, receptionist_repository: IReceptionistRepository):
        self.user_repository = user_repository
        self.doctor_repository = doctor_repository
        self.receptionist_repository = receptionist_repository

    def execute(self, doctor_id: int, data: ReceptionistCreateDTO) -> UserEntity:
        doctor = self.doctor_repository.get_by_id(doctor_id)
        if not doctor:
            raise ValueError("Doctor not found")
            
        existing_user = self.user_repository.get_by_email(data.email)
        if existing_user:
            raise ValueError("Email already registered")
            
        user_entity = UserEntity(
            name=data.name,
            last_name=data.last_name,
            email=data.email,
            phone=data.phone,
            role=RoleEnum.recepcionist,
            is_active=True,
            password=get_password_hash(data.password)
        )
        
        db_user = self.user_repository.create(user_entity)
        receptionist_entity = ReceptionistEntity(
            user_id=db_user.user_id,
            doctor_id=doctor_id
        )
        self.receptionist_repository.create(receptionist_entity)
        return db_user
