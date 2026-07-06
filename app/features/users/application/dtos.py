from dataclasses import dataclass
from typing import Optional
from datetime import date
from app.core.enums import RoleEnum

@dataclass
class ReceptionistCreateDTO:
    name: str
    last_name: str
    email: str
    password: str
    phone: Optional[str] = None

@dataclass
class DoctorRegistrationDTO:
    name: str
    last_name: str
    email: str
    password: str
    phone: Optional[str] = None
    role: RoleEnum = RoleEnum.doctor
    is_active: bool = True
    image_url: Optional[str] = None
    professional_license: Optional[str] = None
    specialty: Optional[str] = None
    office: Optional[str] = None

@dataclass
class PatientRegistrationDTO:
    name: str
    last_name: str
    email: str
    password: str
    birthdate: date
    phone: Optional[str] = None
    role: RoleEnum = RoleEnum.patient
    is_active: bool = True
    image_url: Optional[str] = None
    doctor_id: Optional[int] = None

@dataclass
class UserUpdateDTO:
    name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    role: Optional[RoleEnum] = None
    is_active: Optional[bool] = None
    image_url: Optional[str] = None
