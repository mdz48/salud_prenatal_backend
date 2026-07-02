from app.features.appointments.domain.ports import IAppointmentRepository
from app.features.appointments.domain.entities import AppointmentEntity

class UpdateAppointmentUseCase:
    def __init__(self, appointment_repo: IAppointmentRepository):
        self.appointment_repo = appointment_repo

    def execute(self, entity: AppointmentEntity) -> AppointmentEntity:
        appointment = self.appointment_repo.get_by_id(entity.appointment_id)
        if not appointment:
            raise ValueError("Appointment not found")
        
        return self.appointment_repo.update(entity)
