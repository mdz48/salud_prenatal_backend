from sqlalchemy import Column, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.pregnancy_calculations import age_years


class Patient(Base):
    __tablename__ = "patients"

    patient_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True, nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.doctor_id"), nullable=True, index=True)
    birthdate = Column(Date, nullable=False)

    # Relationships
    user = relationship("Usuario", back_populates="patient_profile")
    doctor = relationship("Doctor", back_populates="patients")
    appointments = relationship("Appointment", back_populates="patient")
    medical_records = relationship("MedicalRecord", back_populates="patient", uselist=True)

    @property
    def age(self) -> int | None:
        return age_years(self.birthdate)
