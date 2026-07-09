from datetime import date
from unittest.mock import MagicMock

from app.core.enums import RoleEnum
from app.features.chat.infrastructure.adapters.chat_contacts_lookup_adapter import (
    ChatContactsLookupAdapter,
)
from app.features.users.domain.doctor_entity import DoctorEntity
from app.features.users.domain.patient_entity import PatientEntity
from app.features.users.domain.receptionist_entity import ReceptionistEntity
from app.features.users.domain.user_entity import UserEntity


def _user(user_id: int, role: RoleEnum = RoleEnum.patient) -> UserEntity:
    return UserEntity(
        user_id=user_id,
        name=f"Nombre{user_id}",
        last_name=f"Apellido{user_id}",
        email=f"user{user_id}@test.com",
        password="hash",
        role=role,
    )


def _adapter():
    return ChatContactsLookupAdapter(
        doctor_repository=MagicMock(),
        receptionist_repository=MagicMock(),
        patient_repository=MagicMock(),
        user_repository=MagicMock(),
    )


def test_chat_contacts_lookup_resuelve_ids_por_perfil():
    adapter = _adapter()
    adapter.doctor_repository.get_by_user_id.return_value = DoctorEntity(
        doctor_id=10, user_id=1
    )
    adapter.receptionist_repository.get_by_user_id.return_value = ReceptionistEntity(
        receptionist_id=20, user_id=2, doctor_id=10
    )
    adapter.patient_repository.get_by_user_id.return_value = PatientEntity(
        patient_id=30, user_id=3, doctor_id=10, birthdate=date(1995, 1, 1)
    )

    assert adapter.get_doctor_id_for_doctor(1) == 10
    assert adapter.get_doctor_id_for_receptionist(2) == 10
    assert adapter.get_doctor_id_for_patient(3) == 10


def test_chat_contacts_lookup_mapea_pacientes_recepcionistas_y_doctor():
    adapter = _adapter()
    adapter.patient_repository.get_patients_by_doctor.return_value = [
        PatientEntity(
            patient_id=30,
            user_id=3,
            doctor_id=10,
            birthdate=date(1995, 1, 1),
            user=_user(3),
        )
    ]
    adapter.receptionist_repository.get_by_doctor_id.return_value = [
        _user(4, RoleEnum.recepcionist)
    ]
    adapter.doctor_repository.get_by_id.return_value = DoctorEntity(doctor_id=10, user_id=5)
    adapter.user_repository.get_by_id.return_value = _user(5, RoleEnum.doctor)

    patients = adapter.get_patients_of_doctor(10)
    receptionists = adapter.get_receptionists_of_doctor(10)
    doctor = adapter.get_doctor_contact(10)

    assert patients[0].model_dump() == {
        "user_id": 3,
        "name": "Nombre3",
        "last_name": "Apellido3",
        "role": "paciente",
    }
    assert receptionists[0].role == "recepcionista"
    assert doctor.user_id == 5
    assert doctor.role == "doctor"


def test_chat_contacts_lookup_get_all_doctors_usa_solo_rol_doctor():
    adapter = _adapter()
    adapter.user_repository.get_by_role.return_value = [_user(5, RoleEnum.doctor)]

    doctors = adapter.get_all_doctors()

    adapter.user_repository.get_by_role.assert_called_once_with(RoleEnum.doctor)
    assert [doctor.role for doctor in doctors] == ["doctor"]


def test_chat_contacts_lookup_omite_doctor_inactivo():
    adapter = _adapter()
    adapter.doctor_repository.get_by_id.return_value = DoctorEntity(doctor_id=10, user_id=5)
    inactive_doctor = _user(5, RoleEnum.doctor)
    inactive_doctor.is_active = False
    adapter.user_repository.get_by_id.return_value = inactive_doctor

    assert adapter.get_doctor_contact(10) is None
