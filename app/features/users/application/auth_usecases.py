from app.features.users.domain.ports import IUserRepository, IPatientRepository, IDoctorRepository, IReceptionistRepository
from app.core.security import verify_password, create_access_token

class AuthenticateUserUseCase:
    def __init__(self, 
                 user_repository: IUserRepository,
                 patient_repository: IPatientRepository,
                 doctor_repository: IDoctorRepository,
                 receptionist_repository: IReceptionistRepository):
        self.user_repository = user_repository
        self.patient_repository = patient_repository
        self.doctor_repository = doctor_repository
        self.receptionist_repository = receptionist_repository

    def execute(self, email: str, password: str):
        user = self.user_repository.get_by_email(email)
        if not user:
            raise ValueError("Incorrect email or password")
        if not verify_password(password, user.password):
            raise ValueError("Incorrect email or password")
        if not user.is_active:
            raise ValueError("Inactive user")

        role_str = user.role.value if hasattr(user.role, 'value') else str(user.role)
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.user_id, "role": role_str}
        )
        
        patient_id = None
        doctor_id = None
        medical_record_id = None
        
        patient = self.patient_repository.get_by_user_id(user.user_id)
        if patient:
            patient_id = patient.patient_id
            doctor_id = patient.doctor_id
            # Omitted medical_record_id as we decouple domain
        else:
            doctor = self.doctor_repository.get_by_user_id(user.user_id)
            if doctor:
                doctor_id = doctor.doctor_id
            else:
                receptionist = self.receptionist_repository.get_by_user_id(user.user_id)
                if receptionist:
                    doctor_id = receptionist.doctor_id

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.user_id,
            "role": role_str,
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "medical_record_id": medical_record_id
        }
