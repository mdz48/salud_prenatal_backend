from sqlalchemy.orm import Session
from app.features.appointments.models.appointment_model import Appointment

class AppointmentRepository:
    def get_by_id(self, db: Session, appointment_id: int):
        return db.query(Appointment).filter(Appointment.id == appointment_id).first()

    def get_by_patient_id(self, db: Session, patient_id: int):
        return db.query(Appointment).filter(Appointment.patient_id == patient_id).all()

    def get_by_doctor_id(self, db: Session, doctor_id: int):
        return db.query(Appointment).filter(Appointment.doctor_id == doctor_id).all()

    def create(self, db: Session, appointment_data: dict, commit: bool = True):
        db_appointment = Appointment(**appointment_data)
        db.add(db_appointment)
        if commit:
            db.commit()
            db.refresh(db_appointment)
        else:
            db.flush()
        return db_appointment

    def update(self, db: Session, db_appointment: Appointment, appointment_data: dict, commit: bool = True):
        for key, value in appointment_data.items():
            setattr(db_appointment, key, value)
        if commit:
            db.commit()
            db.refresh(db_appointment)
        else:
            db.flush()
        return db_appointment

    def delete(self, db: Session, db_appointment: Appointment, commit: bool = True):
        db.delete(db_appointment)
        if commit:
            db.commit()
        else:
            db.flush()
        return db_appointment

appointment_repository = AppointmentRepository()
