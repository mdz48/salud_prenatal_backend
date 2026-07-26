from app.appointments.domain.ports import IAppointmentRepository
from app.appointments.domain.appointment_entity import AppointmentEntity

class UpdateAppointmentUseCase:
    def __init__(self, appointment_repo: IAppointmentRepository):
        self.appointment_repo = appointment_repo

    def execute(self, appointment_id_or_entity, update_data: dict = None) -> AppointmentEntity:
        if isinstance(appointment_id_or_entity, AppointmentEntity):
            entity = appointment_id_or_entity
        else:
            appointment_id = appointment_id_or_entity
            existing = self.appointment_repo.get_by_id(appointment_id)
            if not existing:
                raise ValueError("Appointment not found")
            current_dict = existing.model_dump()
            if update_data:
                current_dict.update(update_data)
            entity = AppointmentEntity(**current_dict)

        return self.appointment_repo.update(entity)
