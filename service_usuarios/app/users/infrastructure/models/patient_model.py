from sqlalchemy import Column, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from salud_prenatal_shared_core.database import Base
from salud_prenatal_shared_core.pregnancy_calculations import age_years


class Patient(Base):
    __tablename__ = "patients"

    patient_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True, nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.doctor_id"), nullable=True, index=True)
    birthdate = Column(Date, nullable=False)

    # Relationships (solo dentro del servicio usuarios).
    # appointments/medical_records viven en el servicio transaccional: se leen por
    # read-model sobre la DB compartida (ver infrastructure/readmodels), no por relación ORM.
    user = relationship("Usuario", back_populates="patient_profile")
    doctor = relationship("Doctor", back_populates="patients")

    @property
    def age(self) -> int | None:
        return age_years(self.birthdate)
