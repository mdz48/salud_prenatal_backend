from app.features.users.domain.ports import IUserRepository, IDoctorRepository, ISubscriptionInitializer
from app.features.users.domain.user_entity import UserEntity
from app.features.users.domain.doctor_entity import DoctorEntity
from app.features.users.application.dtos import DoctorRegistrationDTO
from app.core.security import get_password_hash
from app.core.enums import RoleEnum

class RegisterDoctorUseCase:
    def __init__(self, user_repository: IUserRepository, doctor_repository: IDoctorRepository,
                 subscription_initializer: ISubscriptionInitializer):
        self.user_repository = user_repository
        self.doctor_repository = doctor_repository
        self.subscription_initializer = subscription_initializer

    def execute(self, data: DoctorRegistrationDTO) -> DoctorEntity:
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

        # Suscripcion pendiente: el doctor debe pagar antes de usar el sistema.
        self.subscription_initializer.create_pending(db_user.user_id)

        return db_doctor
