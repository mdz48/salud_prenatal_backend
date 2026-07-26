"""IChatContactsLookup leyendo users/patients/doctors/receptionists directo de la
DB compartida (read-models). Reemplaza los 4 repositorios del servicio usuarios."""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.chat.domain.dtos import ChatUser
from app.chat.domain.ports import IChatContactsLookup
from app.readmodels.users_readmodels import UserRead, PatientRead, DoctorRead, ReceptionistRead


class ChatContactsLookupAdapter(IChatContactsLookup):
    def __init__(self, db: Session):
        self.db = db

    def get_doctor_id_for_doctor(self, user_id: int) -> Optional[int]:
        d = self.db.query(DoctorRead).filter(DoctorRead.user_id == user_id).first()
        return d.doctor_id if d else None

    def get_doctor_id_for_receptionist(self, user_id: int) -> Optional[int]:
        r = self.db.query(ReceptionistRead).filter(ReceptionistRead.user_id == user_id).first()
        return r.doctor_id if r else None

    def get_doctor_id_for_patient(self, user_id: int) -> Optional[int]:
        p = self.db.query(PatientRead).filter(PatientRead.user_id == user_id).first()
        return p.doctor_id if p else None

    def get_patients_of_doctor(self, doctor_id: int) -> List[ChatUser]:
        patients = self.db.query(PatientRead).filter(PatientRead.doctor_id == doctor_id).all()
        out = []
        for p in patients:
            user = self.db.query(UserRead).filter(UserRead.user_id == p.user_id).first()
            if user:
                out.append(self._to_chat_user(user, role="paciente"))
        return out

    def get_receptionists_of_doctor(self, doctor_id: int) -> List[ChatUser]:
        recs = self.db.query(ReceptionistRead).filter(ReceptionistRead.doctor_id == doctor_id).all()
        out = []
        for r in recs:
            user = self.db.query(UserRead).filter(UserRead.user_id == r.user_id).first()
            if user:
                out.append(self._to_chat_user(user, role="recepcionista"))
        return out

    def get_doctor_contact(self, doctor_id: int) -> Optional[ChatUser]:
        doctor = self.db.query(DoctorRead).filter(DoctorRead.doctor_id == doctor_id).first()
        if not doctor:
            return None
        user = self.db.query(UserRead).filter(UserRead.user_id == doctor.user_id).first()
        if not user or not user.is_active:
            return None
        return self._to_chat_user(user, role="doctor")

    def _to_chat_user(self, user, role: str) -> ChatUser:
        return ChatUser(user_id=user.user_id, name=user.name, last_name=user.last_name, role=role)
