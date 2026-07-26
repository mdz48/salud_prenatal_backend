"""Read-models propios del servicio auth sobre la DB compartida.

El login necesita leer varias tablas (users para la contraseña; patients/doctors/
receptionists/medical_records/subscriptions para armar la respuesta rica). Con DB
compartida, auth mapea SOLO las columnas que consume — sin FK ni relaciones ORM,
sin importar los modelos de otros servicios. El *schema* es el contrato.

`EncryptedString` viene de shared_core: garantiza que auth lea la PII (name/last_name)
con exactamente el mismo cifrado Fernet que el resto de servicios.
"""
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum as SAEnum

from salud_prenatal_shared_core.database import ReadModelBase as Base
from salud_prenatal_shared_core.security import EncryptedString
from salud_prenatal_shared_core.enums import RoleEnum, SubscriptionStatusEnum


class UserAuth(Base):
    """Tabla `users` — credenciales + datos base para el login."""
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    user_id = Column(Integer, primary_key=True)
    name = Column(EncryptedString, nullable=False)
    last_name = Column(EncryptedString, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(SAEnum(RoleEnum), nullable=False)
    is_active = Column(Boolean, default=True)


class PatientAuth(Base):
    __tablename__ = "patients"
    __table_args__ = {"extend_existing": True}

    patient_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    doctor_id = Column(Integer, index=True)


class DoctorAuth(Base):
    __tablename__ = "doctors"
    __table_args__ = {"extend_existing": True}

    doctor_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)


class ReceptionistAuth(Base):
    __tablename__ = "receptionists"
    __table_args__ = {"extend_existing": True}

    receptionist_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    doctor_id = Column(Integer, index=True)


class MedicalRecordAuth(Base):
    __tablename__ = "medical_records"
    __table_args__ = {"extend_existing": True}

    medical_record_id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, index=True)
    doctor_id = Column(Integer, index=True)


class SubscriptionAuth(Base):
    __tablename__ = "subscriptions"
    __table_args__ = {"extend_existing": True}

    subscription_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, index=True)
    status = Column(SAEnum(SubscriptionStatusEnum), nullable=False)
    current_period_end = Column(DateTime, nullable=True)
