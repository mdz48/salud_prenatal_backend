from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from app.core.enums import BloodTypeEnum
from app.core.database import Base
from app.features.users.domain.pregnancy_calculations import age_years, gestational_weeks


class Patient(Base):
    __tablename__ = "patients"

    patient_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True, nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.doctor_id"), nullable=True, index=True)
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

    @property
    def current_gestational_weeks(self) -> int | None:
        return gestational_weeks(self.last_menstrual_period, self.weeks_at_registration)

    @property
    def age(self) -> int | None:
        return age_years(self.birthdate)