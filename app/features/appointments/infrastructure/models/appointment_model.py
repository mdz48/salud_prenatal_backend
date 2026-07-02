from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from app.core.database import Base
from sqlalchemy.orm import relationship
from app.core.enums import AppointmentStatusEnum
from sqlalchemy.sql import func

class Appointment(Base):
    __tablename__ = "appointments"

    appointment_id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.doctor_id"), nullable=False)
    appointment_date = Column(DateTime, nullable=False)
    status = Column(Enum(AppointmentStatusEnum), nullable=False, default=AppointmentStatusEnum.pending)
    reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
