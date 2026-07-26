from datetime import datetime, timezone
from salud_prenatal_shared_core.enums import AppointmentStatusEnum
from app.users.domain.ports import (
    IReceptionistRepository,
    IUserRepository,
    IPatientRepository,
    IAppointmentLookup,
)


class GetReceptionistDashboardUseCase:
    def __init__(
        self,
        receptionist_repository: IReceptionistRepository,
        user_repository: IUserRepository,
        patient_repository: IPatientRepository,
        appointment_lookup: IAppointmentLookup,
    ):
        self.receptionist_repository = receptionist_repository
        self.user_repository = user_repository
        self.patient_repository = patient_repository
        self.appointment_lookup = appointment_lookup

    def execute(self, receptionist_id: int) -> dict:
        receptionist = self.receptionist_repository.get_by_id(receptionist_id)
        if not receptionist:
            raise ValueError("Receptionist not found")

        user = self.user_repository.get_by_id(receptionist.user_id)
        if not user:
            raise ValueError("User associated with receptionist not found")

        now = datetime.now(timezone.utc)
        appointments = self.appointment_lookup.get_appointments_by_doctor_id(receptionist.doctor_id)

        upcoming = [a for a in appointments if a.appointment_date.replace(tzinfo=timezone.utc) >= now]
        upcoming.sort(key=lambda a: a.appointment_date)

        upcoming_appointments = [self._to_detail(a) for a in upcoming]
        pending_appointments = [d for d in upcoming_appointments if d["status"] == AppointmentStatusEnum.pending.value]
        confirmed_appointments = [d for d in upcoming_appointments if d["status"] == AppointmentStatusEnum.confirmed.value]

        return {
            "full_name": f"{user.name} {user.last_name}",
            "upcoming_appointments": upcoming_appointments,
            "pending_appointments": pending_appointments,
            "confirmed_appointments": confirmed_appointments,
        }

    def _to_detail(self, appt) -> dict:
        patient_name = "Unknown"
        patient = self.patient_repository.get_by_id(appt.patient_id)
        if patient:
            patient_user = self.user_repository.get_by_id(patient.user_id)
            if patient_user:
                patient_name = f"{patient_user.name} {patient_user.last_name}"

        return {
            "appointment_id": appt.appointment_id,
            "patient_id": appt.patient_id,
            "patient_name": patient_name,
            "appointment_time": appt.appointment_date,
            "reason": appt.reason,
            "status": appt.status.value if hasattr(appt.status, "value") else str(appt.status),
        }
