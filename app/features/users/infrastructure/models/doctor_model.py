from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.security import EncryptedString


class Doctor(Base):
    __tablename__ = "doctors"

    doctor_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True, nullable=False)
    professional_license = Column(EncryptedString, unique=True, nullable=True)
    specialty = Column(String(100), nullable=True)
    office = Column(EncryptedString, nullable=True)

    # Relationships
    user = relationship("Usuario", back_populates="doctor_profile")
    patients = relationship("Patient", back_populates="doctor")
    appointments = relationship("Appointment", back_populates="doctor")