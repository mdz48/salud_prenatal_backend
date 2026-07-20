from typing import List
from app.features.users.domain.ports import IAppointmentLookup
from app.features.appointments.infrastructure.repositories.appointment_repository import AppointmentRepository

class AppointmentLookupAdapter(IAppointmentLookup):
    def __init__(self, appointment_repository: AppointmentRepository):
        self.appointment_repository = appointment_repository
        
    def get_appointments_by_patient_id(self, patient_id: int) -> List[object]:
        return self.appointment_repository.get_by_patient_id(patient_id)

    def get_appointments_by_doctor_id(self, doctor_id: int) -> List[object]:
        return self.appointment_repository.get_by_doctor_id(doctor_id)

    def cancel_future_appointments(self, patient_id: int, doctor_id: int) -> None:
        from app.features.appointments.infrastructure.models.appointment_model import Appointment
        from app.core.enums import AppointmentStatusEnum
        from app.core.time import now_cdmx
        
        now = now_cdmx().replace(tzinfo=None)
        self.appointment_repository.db.query(Appointment).filter(
            Appointment.patient_id == patient_id,
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date >= now,
            Appointment.status.in_([AppointmentStatusEnum.pending, AppointmentStatusEnum.confirmed])
        ).update({Appointment.status: AppointmentStatusEnum.cancelled}, synchronize_session=False)
        self.appointment_repository.db.commit()
