from app.features.users.domain.ports import IUserRepository, IPatientRepository
from app.features.users.domain.user_entity import UserEntity
from app.features.users.domain.patient_entity import PatientEntity
from app.features.users.infrastructure.schemas.patient_schema import PatientRegistration
from app.core.security import get_password_hash
from app.core.enums import RoleEnum

class RegisterPatientUseCase:
    def __init__(self, user_repository: IUserRepository, patient_repository: IPatientRepository):
        self.user_repository = user_repository
        self.patient_repository = patient_repository

    def execute(self, data: PatientRegistration) -> PatientEntity:
        existing_user = self.user_repository.get_by_email(data.email)
        if existing_user:
            raise ValueError("Email already registered")
        
        user_entity = UserEntity(
            name=data.name,
            last_name=data.last_name,
            email=data.email,
            phone=data.phone,
            role=RoleEnum.patient,
            is_active=True,
            password=get_password_hash(data.password)
        )
        
        db_user = self.user_repository.create(user_entity)
        
        patient_data_dict = data.model_dump(exclude={"name", "last_name", "email", "phone", "password", "role", "is_active", "image_url"})
        patient_data_dict["user_id"] = db_user.user_id
        
        patient_entity = PatientEntity(**patient_data_dict)
        db_patient = self.patient_repository.create(patient_entity)
        return db_patient
