from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from salud_prenatal_shared_core.database import Base
from salud_prenatal_shared_core.security import EncryptedString


class Doctor(Base):
    __tablename__ = "doctors"

    doctor_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True, nullable=False)
    professional_license = Column(EncryptedString, unique=True, nullable=True)
    specialty = Column(String(100), nullable=True)
    office = Column(EncryptedString, nullable=True)

    # Relationships (solo dentro del servicio usuarios).
    # appointments vive en transaccional; se lee por read-model sobre la DB compartida.
    user = relationship("Usuario", back_populates="doctor_profile")
    patients = relationship("Patient", back_populates="doctor")