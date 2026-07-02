from app.features.appointments.domain.ports import IAppointmentRepository
from app.features.appointments.domain.entities import AppointmentEntity

class GetAppointmentUseCase:
    def __init__(self, appointment_repo: IAppointmentRepository):
        self.appointment_repo = appointment_repo

    def execute(self, appointment_id: int) -> AppointmentEntity:
        appointment = self.appointment_repo.get_by_id(appointment_id)
        if not appointment:
            raise ValueError("Appointment not found")
        return appointment
