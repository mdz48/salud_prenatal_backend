from app.appointments.domain.ports import IAppointmentRepository

class DeleteAppointmentUseCase:
    def __init__(self, appointment_repo: IAppointmentRepository):
        self.appointment_repo = appointment_repo

    def execute(self, appointment_id: int) -> None:
        appointment = self.appointment_repo.get_by_id(appointment_id)
        if not appointment:
            raise ValueError("Appointment not found")
        
        self.appointment_repo.delete(appointment_id)
