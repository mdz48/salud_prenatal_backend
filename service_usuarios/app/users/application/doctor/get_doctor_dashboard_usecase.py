from datetime import timezone
from salud_prenatal_shared_core.time import today_cdmx, CDMX_TZ
from app.users.domain.ports import (
    IDoctorRepository,
    IUserRepository,
    IPatientRepository,
    IReceptionistRepository,
    IAppointmentLookup,
)


class GetDoctorDashboardUseCase:
    def __init__(
        self,
        doctor_repository: IDoctorRepository,
        user_repository: IUserRepository,
        patient_repository: IPatientRepository,
        receptionist_repository: IReceptionistRepository,
        appointment_lookup: IAppointmentLookup,
    ):
        self.doctor_repository = doctor_repository
        self.user_repository = user_repository
        self.patient_repository = patient_repository
        self.receptionist_repository = receptionist_repository
        self.appointment_lookup = appointment_lookup

    def execute(self, doctor_id: int) -> dict:
        doctor = self.doctor_repository.get_by_id(doctor_id)
        if not doctor:
            raise ValueError("Doctor not found")

        receptionists = self.receptionist_repository.get_by_doctor_id(doctor_id)

        appointments = self.appointment_lookup.get_appointments_by_doctor_id(doctor_id)
        today = today_cdmx()
        today_appointments = []
        for appt in appointments:
            appt_local_date = appt.appointment_date.replace(tzinfo=timezone.utc).astimezone(CDMX_TZ).date()
            if appt_local_date != today:
                continue

            patient_name = "Unknown"
            patient = self.patient_repository.get_by_id(appt.patient_id)
            if patient:
                patient_user = self.user_repository.get_by_id(patient.user_id)
                if patient_user:
                    patient_name = f"{patient_user.name} {patient_user.last_name}"

            today_appointments.append({
                "appointment_id": appt.appointment_id,
                "patient_id": appt.patient_id,
                "patient_name": patient_name,
                "appointment_time": appt.appointment_date,
                "reason": appt.reason,
                "status": appt.status.value if hasattr(appt.status, "value") else str(appt.status),
            })

        today_appointments.sort(key=lambda a: a["appointment_time"])

        return {
            "receptionists": receptionists,
            "today_appointments_count": len(today_appointments),
            "today_appointments": today_appointments,
        }
