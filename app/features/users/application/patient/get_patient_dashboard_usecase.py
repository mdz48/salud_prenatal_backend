from datetime import datetime, timezone
from app.features.users.domain.ports import IPatientRepository, IUserRepository, IDoctorRepository
from app.features.appointments.domain.ports import IAppointmentRepository

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
