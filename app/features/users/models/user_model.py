from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.enums import RoleEnum
from app.core.database import Base
from app.core.security import EncryptedString
from app.features.users.models.doctor_model import Doctor
from app.features.users.models.patient_model import Patient


class Usuario(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(EncryptedString, nullable=False)
    last_name = Column(EncryptedString, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(EncryptedString, nullable=True)
    password = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.patient)
    is_active = Column(Boolean, default=True)
    image_url = Column(String(255), nullable=True, default=None)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    doctor_profile = relationship("Doctor", back_populates="user", uselist=False, foreign_keys="Doctor.user_id")
    patient_profile = relationship("Patient", back_populates="user", uselist=False, foreign_keys="Patient.user_id")
    receptionist_profile = relationship("Receptionist", back_populates="user", uselist=False, foreign_keys="Receptionist.user_id")