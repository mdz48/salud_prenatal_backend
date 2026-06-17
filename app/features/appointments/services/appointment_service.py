from sqlalchemy.orm import Session
from app.features.appointments.repositories.appointment_repository import appointment_repository
from app.features.appointments.schemas.appointment_schema import AppointmentCreate, AppointmentUpdate
from app.features.appointments.models.appointment_model import Appointment

class AppointmentService:
    def create_appointment(self, db: Session, data: AppointmentCreate):
        appointment_data = data.model_dump()
        return appointment_repository.create(db, appointment_data)

    def get_appointment(self, db: Session, appointment_id: int):
        appointment = appointment_repository.get_by_id(db, appointment_id)
        if not appointment:
            raise ValueError("Appointment not found")
        return appointment

    def get_appointments_by_patient(self, db: Session, patient_id: int):
        return appointment_repository.get_by_patient_id(db, patient_id)

    def get_appointments_by_doctor(self, db: Session, doctor_id: int):
        return appointment_repository.get_by_doctor_id(db, doctor_id)

    def update_appointment(self, db: Session, appointment_id: int, data: AppointmentUpdate):
        appointment = self.get_appointment(db, appointment_id)
        update_data = data.model_dump(exclude_unset=True)
        return appointment_repository.update(db, appointment, update_data)

    def delete_appointment(self, db: Session, appointment_id: int):
        appointment = self.get_appointment(db, appointment_id)
        return appointment_repository.delete(db, appointment)

appointment_service = AppointmentService()
