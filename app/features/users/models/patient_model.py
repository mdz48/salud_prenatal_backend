from datetime import date
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, Boolean, Float
from sqlalchemy.orm import relationship
from app.core.enums import BloodTypeEnum
from app.core.database import Base


class Patient(Base):
    __tablename__ = "patients"

    patient_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True, nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.doctor_id"), nullable=True)
    birthdate = Column(Date, nullable=False)
    blood_type = Column(Enum(BloodTypeEnum), nullable=True) # Tipo de sangre
    weeks_at_registration = Column(Integer, nullable=True) # Semana de gestación al registrarse
    last_menstrual_period = Column(Date, nullable=True) # Fecha del ultimo periodo menstrual
    residence = Column(String(100), nullable=False) # Residencia
    education_level = Column(String(50), nullable=True) # Nivel educativo
    marital_status = Column(String(50), nullable=True) # Estado civil
    height_cm = Column(Integer, nullable=True) # Altura en centimetros
    initial_weight = Column(Float, nullable=True) # Peso inicial en kilogramos

    # Relationships
    user = relationship("Usuario", back_populates="patient_profile")
    doctor = relationship("Doctor", back_populates="patients")
    appointments = relationship("Appointment", back_populates="patient")
    medical_records = relationship("MedicalRecord", back_populates="patient", uselist=True)
    consultations = relationship("Consultation", back_populates="patient")

    @property
    def current_gestational_weeks(self) -> int | None:
        """Calcula las semanas de gestación actuales basándose en la fecha del último periodo."""
        if self.last_menstrual_period:
            delta = date.today() - self.last_menstrual_period
            return delta.days // 7
        return self.weeks_at_registration

    @property
    def age(self) -> int | None:
        if self.birthdate:
            today = date.today()
            return today.year - self.birthdate.year - ((today.month, today.day) < (self.birthdate.month, self.birthdate.day))
        return None