from datetime import datetime, timezone
from app.features.users.domain.ports import IUserRepository, IPatientRepository, IDoctorRepository
from app.features.users.domain.entities import UserEntity, PatientEntity
from app.features.users.infrastructure.schemas.patient_schema import PatientRegistration
from app.features.appointments.domain.ports import IAppointmentRepository
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

class GetPatientsByDoctorUseCase:
    def __init__(self, patient_repository: IPatientRepository):
        self.patient_repository = patient_repository

    def execute(self, doctor_id: int):
        return self.patient_repository.get_patients_by_doctor(doctor_id)

class GetPatientDashboardUseCase:
    def __init__(self, 
                 patient_repository: IPatientRepository,
                 user_repository: IUserRepository,
                 doctor_repository: IDoctorRepository,
                 appointment_repository: IAppointmentRepository):
        self.patient_repository = patient_repository
        self.user_repository = user_repository
        self.doctor_repository = doctor_repository
        self.appointment_repository = appointment_repository

    def execute(self, patient_id: int):
        patient = self.patient_repository.get_by_id(patient_id)
        if not patient:
            raise ValueError("Patient not found")
            
        user = self.user_repository.get_by_id(patient.user_id)
        if not user:
            raise ValueError("User associated with patient not found")

        full_name = f"{user.name} {user.last_name}"
        gestational_weeks = patient.current_gestational_weeks

        current_doctor = None
        current_doctor_image = None
        current_doctor_specialty = None
        
        if patient.doctor_id:
            doctor = self.doctor_repository.get_by_id(patient.doctor_id)
            if doctor:
                doctor_user = self.user_repository.get_by_id(doctor.user_id)
                if doctor_user:
                    current_doctor = f"{doctor_user.name} {doctor_user.last_name}"
                    current_doctor_image = doctor_user.image_url
                    current_doctor_specialty = doctor.specialty

        now = datetime.now(timezone.utc)
        appointments = self.appointment_repository.get_by_patient_id(patient_id)
        upcoming_appointments = []
        for appt in appointments:
            if appt.appointment_date.replace(tzinfo=timezone.utc) >= now:
                doctor_name = "Unknown"
                if appt.doctor_id:
                    appt_doctor = self.doctor_repository.get_by_id(appt.doctor_id)
                    if appt_doctor:
                        appt_doctor_user = self.user_repository.get_by_id(appt_doctor.user_id)
                        if appt_doctor_user:
                            doctor_name = f"{appt_doctor_user.name} {appt_doctor_user.last_name}"
                            
                upcoming_appointments.append({
                    "appointment_id": appt.appointment_id,
                    "appointment_date": appt.appointment_date,
                    "status": appt.status.value if hasattr(appt.status, 'value') else str(appt.status),
                    "reason": appt.reason,
                    "doctor_name": doctor_name
                })

        upcoming_appointments.sort(key=lambda x: x["appointment_date"])

        return {
            "full_name": full_name,
            "current_gestational_weeks": gestational_weeks,
            "current_doctor": current_doctor,
            "current_doctor_image": current_doctor_image,
            "current_doctor_specialty": current_doctor_specialty,
            "upcoming_appointments": upcoming_appointments
        }
