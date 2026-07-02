from app.features.users.domain.ports import IUserRepository, IDoctorRepository, IInvitationCodeRepository, IReceptionistRepository
from app.features.users.domain.entities import UserEntity, DoctorEntity, ReceptionistEntity
from app.features.users.infrastructure.schemas.doctor_schema import DoctorRegistration
from app.features.users.infrastructure.schemas.receptionist_schema import ReceptionistCreate
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

class CreateReceptionistUseCase:
    def __init__(self, user_repository: IUserRepository, doctor_repository: IDoctorRepository, receptionist_repository: IReceptionistRepository):
        self.user_repository = user_repository
        self.doctor_repository = doctor_repository
        self.receptionist_repository = receptionist_repository

    def execute(self, doctor_id: int, data: ReceptionistCreate) -> UserEntity:
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

class GetReceptionistsByDoctorUseCase:
    def __init__(self, doctor_repository: IDoctorRepository, receptionist_repository: IReceptionistRepository):
        self.doctor_repository = doctor_repository
        self.receptionist_repository = receptionist_repository

    def execute(self, doctor_id: int):
        doctor = self.doctor_repository.get_by_id(doctor_id)
        if not doctor:
            raise ValueError("Doctor not found")
        return self.receptionist_repository.get_by_doctor_id(doctor_id)

class GenerateInvitationCodeUseCase:
    def __init__(self, doctor_repository: IDoctorRepository, invitation_code_repository: IInvitationCodeRepository):
        self.doctor_repository = doctor_repository
        self.invitation_code_repository = invitation_code_repository

    def execute(self, doctor_id: int):
        doctor = self.doctor_repository.get_by_id(doctor_id)
        if not doctor:
            raise ValueError("Doctor not found")
        return self.invitation_code_repository.create(doctor_id)
