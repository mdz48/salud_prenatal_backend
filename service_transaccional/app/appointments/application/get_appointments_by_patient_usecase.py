from typing import List
from app.appointments.domain.ports import IAppointmentRepository
from app.appointments.domain.appointment_entity import AppointmentEntity

class GetAppointmentsByPatientUseCase:
    def __init__(self, appointment_repo: IAppointmentRepository):
        self.appointment_repo = appointment_repo

    def execute(self, patient_id: int) -> List[AppointmentEntity]:
        return self.appointment_repo.get_by_patient_id(patient_id)
