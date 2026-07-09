from typing import List

from app.features.chat.domain.dtos import ChatUser
from app.features.chat.domain.ports import IChatContactsLookup


class GetChatContactsUseCase:
    def __init__(self, contacts_lookup: IChatContactsLookup):
        self.contacts_lookup = contacts_lookup

    def execute(self, current_user_id: int, role: str) -> List[ChatUser]:
        if role == "doctor":
            doctor_id = self.contacts_lookup.get_doctor_id_for_doctor(current_user_id)
            if not doctor_id:
                return []
            contacts = self.contacts_lookup.get_patients_of_doctor(doctor_id)
            contacts += self.contacts_lookup.get_receptionists_of_doctor(doctor_id)
            return self._exclude_current_user(contacts, current_user_id)

        if role == "recepcionista":
            doctor_id = self.contacts_lookup.get_doctor_id_for_receptionist(current_user_id)
            if not doctor_id:
                return []

            contacts = self.contacts_lookup.get_patients_of_doctor(doctor_id)
            doctor_contact = self.contacts_lookup.get_doctor_contact(doctor_id)
            if doctor_contact:
                contacts.append(doctor_contact)
            return self._exclude_current_user(contacts, current_user_id)

        if role == "paciente":
            doctor_id = self.contacts_lookup.get_doctor_id_for_patient(current_user_id)
            if not doctor_id:
                return []

            contacts = []
            doctor_contact = self.contacts_lookup.get_doctor_contact(doctor_id)
            if doctor_contact:
                contacts.append(doctor_contact)
            contacts += self.contacts_lookup.get_receptionists_of_doctor(doctor_id)
            return self._exclude_current_user(contacts, current_user_id)

        return []

    def _exclude_current_user(
        self, contacts: List[ChatUser], current_user_id: int
    ) -> List[ChatUser]:
        return [contact for contact in contacts if contact.user_id != current_user_id]
