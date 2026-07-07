from app.features.users.domain.ports import IUserRepository, IPatientRepository, IDoctorRepository, IReceptionistRepository, IMedicalRecordLookup
from app.core.security import verify_password, create_access_token

class AuthenticateUserUseCase:
    def __init__(self, 
                 user_repository: IUserRepository,
                 patient_repository: IPatientRepository,
                 doctor_repository: IDoctorRepository,
                 receptionist_repository: IReceptionistRepository,
                 medical_record_lookup: IMedicalRecordLookup):
        self.user_repository = user_repository
        self.patient_repository = patient_repository
        self.doctor_repository = doctor_repository
        self.receptionist_repository = receptionist_repository
        self.medical_record_lookup = medical_record_lookup

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
        receptionist_info = None

        if user.role.value == "paciente":
            patient = self.patient_repository.get_by_user_id(user.user_id)
            if patient:
                patient_id = patient.patient_id
                doctor_id = patient.doctor_id
                medical_record_id = self.medical_record_lookup.get_medical_record_id(patient.patient_id, patient.doctor_id)
        elif user.role.value == "doctor":
            doctor = self.doctor_repository.get_by_user_id(user.user_id)
            if doctor:
                doctor_id = doctor.doctor_id
        elif user.role.value == "recepcionista":
            receptionist = self.receptionist_repository.get_by_user_id(user.user_id)
            if receptionist:
                doctor_id = receptionist.doctor_id

        if doctor_id:
            receptionists = self.receptionist_repository.get_by_doctor_id(doctor_id)
            if receptionists:
                first_receptionist = receptionists[0]
                receptionist_info = {
                    "user_id": first_receptionist.user_id,
                    "name": first_receptionist.name,
                    "last_name": first_receptionist.last_name
                }

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.user_id,
            "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "medical_record_id": medical_record_id,
            "receptionist": receptionist_info
        }
