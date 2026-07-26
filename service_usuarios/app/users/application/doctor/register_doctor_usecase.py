from app.users.domain.ports import IUserRepository, IDoctorRepository
from app.users.domain.user_entity import UserEntity
from app.users.domain.doctor_entity import DoctorEntity
from app.users.application.dtos import DoctorRegistrationDTO
from salud_prenatal_shared_core.security import get_password_hash
from salud_prenatal_shared_core.enums import RoleEnum

class RegisterDoctorUseCase:
    def __init__(self, user_repository: IUserRepository, doctor_repository: IDoctorRepository):
        self.user_repository = user_repository
        self.doctor_repository = doctor_repository

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

        # La fila de suscripcion la crea el servicio pagos on-demand (get-or-create
        # en el primer checkout). "Sin fila" = pending, asi que no hace falta
        # inicializarla aqui ni acoplar usuarios con el servicio pagos.

        return db_doctor
