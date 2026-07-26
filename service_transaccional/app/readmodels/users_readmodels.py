"""Read-models de solo lectura sobre las tablas de `users` (owned por el servicio
usuarios) en la DB compartida. Transaccional las LEE para resolver identidad de
paciente/doctor/recepcionista en sus adapters cross-servicio, sin importar el ORM
de otro servicio ni hacer HTTP. El schema compartido es el contrato.

`EncryptedString` viene de shared_core → misma PII cifrada que el resto de servicios.
"""
from sqlalchemy import Boolean, Column, Integer, String, Date, Enum as SAEnum

from salud_prenatal_shared_core.database import ReadModelBase as Base
from salud_prenatal_shared_core.security import EncryptedString
from salud_prenatal_shared_core.enums import RoleEnum
from salud_prenatal_shared_core.pregnancy_calculations import age_years


class UserRead(Base):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    user_id = Column(Integer, primary_key=True)
    name = Column(EncryptedString, nullable=False)
    last_name = Column(EncryptedString, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    role = Column(SAEnum(RoleEnum), nullable=False)
    is_active = Column(Boolean, default=True)


class PatientRead(Base):
    __tablename__ = "patients"
    __table_args__ = {"extend_existing": True}

    patient_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    doctor_id = Column(Integer, index=True)
    birthdate = Column(Date, nullable=True)

    @property
    def age(self):
        return age_years(self.birthdate)


class DoctorRead(Base):
    __tablename__ = "doctors"
    __table_args__ = {"extend_existing": True}

    doctor_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)


class ReceptionistRead(Base):
    __tablename__ = "receptionists"
    __table_args__ = {"extend_existing": True}

    receptionist_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    doctor_id = Column(Integer, index=True)
