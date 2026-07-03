from typing import List, Optional
from sqlalchemy.orm import Session
from app.features.appointments.infrastructure.models.appointment_model import Appointment
from app.features.appointments.domain.ports import IAppointmentRepository
from app.features.appointments.domain.appointment_entity import AppointmentEntity

class AppointmentRepository(IAppointmentRepository):
    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: Appointment) -> AppointmentEntity:
        return AppointmentEntity(
            appointment_id=model.appointment_id,
            patient_id=model.patient_id,
            doctor_id=model.doctor_id,
            appointment_date=model.appointment_date,
            status=model.status,
            reason=model.reason,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def get_by_id(self, appointment_id: int) -> Optional[AppointmentEntity]:
        model = self.db.query(Appointment).filter(Appointment.appointment_id == appointment_id).first()
        return self._to_entity(model) if model else None

    def get_by_patient_id(self, patient_id: int) -> List[AppointmentEntity]:
        models = self.db.query(Appointment).filter(Appointment.patient_id == patient_id).all()
        return [self._to_entity(m) for m in models]

    def get_by_doctor_id(self, doctor_id: int) -> List[AppointmentEntity]:
        models = self.db.query(Appointment).filter(Appointment.doctor_id == doctor_id).all()
        return [self._to_entity(m) for m in models]

    def create(self, appointment_entity: AppointmentEntity) -> AppointmentEntity:
        data = appointment_entity.model_dump(exclude={"appointment_id", "created_at", "updated_at"}, exclude_unset=True)
        db_appointment = Appointment(**data)
        self.db.add(db_appointment)
        self.db.commit()
        self.db.refresh(db_appointment)
        return self._to_entity(db_appointment)

    def update(self, appointment_entity: AppointmentEntity) -> AppointmentEntity:
        db_appointment = self.db.query(Appointment).filter(Appointment.appointment_id == appointment_entity.appointment_id).first()
        if not db_appointment:
            raise ValueError("Appointment not found")
            
        data = appointment_entity.model_dump(exclude={"appointment_id", "created_at", "updated_at"}, exclude_unset=True)
        for key, value in data.items():
            setattr(db_appointment, key, value)
            
        self.db.commit()
        self.db.refresh(db_appointment)
        return self._to_entity(db_appointment)

    def delete(self, appointment_id: int) -> None:
        db_appointment = self.db.query(Appointment).filter(Appointment.appointment_id == appointment_id).first()
        if db_appointment:
            self.db.delete(db_appointment)
            self.db.commit()
