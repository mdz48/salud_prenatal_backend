from typing import List, Optional

from app.features.chat.domain.dtos import ChatUser
from app.features.chat.domain.ports import IChatContactsLookup
from app.features.users.domain.user_entity import UserEntity
from app.features.users.infrastructure.repositories.doctor_repository import DoctorRepository
from app.features.users.infrastructure.repositories.patient_repository import PatientRepository
from app.features.users.infrastructure.repositories.receptionist_repository import ReceptionistRepository
from app.features.users.infrastructure.repositories.user_repository import UserRepository


class ChatContactsLookupAdapter(IChatContactsLookup):
    """Traduce repositorios de users a contactos del modulo chat."""

    def __init__(
        self,
        doctor_repository: DoctorRepository,
        receptionist_repository: ReceptionistRepository,
        patient_repository: PatientRepository,
        user_repository: UserRepository,
    ):
        self.doctor_repository = doctor_repository
        self.receptionist_repository = receptionist_repository
        self.patient_repository = patient_repository
        self.user_repository = user_repository

    def get_doctor_id_for_doctor(self, user_id: int) -> Optional[int]:
        doctor = self.doctor_repository.get_by_user_id(user_id)
        return doctor.doctor_id if doctor else None

    def get_doctor_id_for_receptionist(self, user_id: int) -> Optional[int]:
        receptionist = self.receptionist_repository.get_by_user_id(user_id)
        return receptionist.doctor_id if receptionist else None

    def get_doctor_id_for_patient(self, user_id: int) -> Optional[int]:
        patient = self.patient_repository.get_by_user_id(user_id)
        return patient.doctor_id if patient else None

    def get_patients_of_doctor(self, doctor_id: int) -> List[ChatUser]:
        return [
            self._to_chat_user(patient.user, role="paciente")
            for patient in self.patient_repository.get_patients_by_doctor(doctor_id)
            if patient.user
        ]

    def get_receptionists_of_doctor(self, doctor_id: int) -> List[ChatUser]:
        return [
            self._to_chat_user(user, role="recepcionista")
            for user in self.receptionist_repository.get_by_doctor_id(doctor_id)
        ]

    def get_doctor_contact(self, doctor_id: int) -> Optional[ChatUser]:
        doctor = self.doctor_repository.get_by_id(doctor_id)
        if not doctor:
            return None

        user = self.user_repository.get_by_id(doctor.user_id)
        if not user or not user.is_active:
            return None

        return self._to_chat_user(user, role="doctor")

    def _to_chat_user(self, user: UserEntity, role: str) -> ChatUser:
        return ChatUser(
            user_id=user.user_id,
            name=user.name,
            last_name=user.last_name,
            role=role,
        )
