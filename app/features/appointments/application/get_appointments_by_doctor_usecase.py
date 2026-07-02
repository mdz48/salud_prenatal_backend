from typing import List
from app.features.appointments.domain.ports import IAppointmentRepository
from app.features.appointments.domain.entities import AppointmentEntity

class GetAppointmentsByDoctorUseCase:
    def __init__(self, appointment_repo: IAppointmentRepository):
        self.appointment_repo = appointment_repo

    def execute(self, doctor_id: int) -> List[AppointmentEntity]:
        return self.appointment_repo.get_by_doctor_id(doctor_id)
