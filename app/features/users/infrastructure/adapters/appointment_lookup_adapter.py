from typing import List
from app.features.users.domain.ports import IAppointmentLookup
from app.features.appointments.infrastructure.repositories.appointment_repository import AppointmentRepository

class AppointmentLookupAdapter(IAppointmentLookup):
    def __init__(self, appointment_repository: AppointmentRepository):
        self.appointment_repository = appointment_repository
        
    def get_appointments_by_patient_id(self, patient_id: int) -> List[object]:
        return self.appointment_repository.get_by_patient_id(patient_id)
