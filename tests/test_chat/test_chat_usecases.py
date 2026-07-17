from datetime import datetime
from unittest.mock import MagicMock
from app.features.chat.application.get_history_usecase import GetHistoryUseCase
from app.features.chat.application.save_message_usecase import SaveMessageUseCase
from app.features.chat.application.get_chat_inbox_usecase import GetChatInboxUseCase
from app.features.chat.application.get_chat_contacts_usecase import GetChatContactsUseCase
from app.features.chat.domain.chat_message_entity import ChatMessage
from app.features.chat.domain.dtos import ChatUser, InboxSummary

def test_get_history_usecase():
    # Arrange
    mock_repo = MagicMock()
    mock_message = ChatMessage(
        message_id=1,
        sender_id=1,
        receiver_id=2,
        content="Hello",
        is_read=False
    )
    mock_repo.get_conversation.return_value = [mock_message]
    
    usecase = GetHistoryUseCase(mock_repo)
    
    # Act
    result = usecase.execute(1, 2)
    
    # Assert
    mock_repo.mark_conversation_read.assert_called_once_with(reader_id=1, other_user_id=2)
    mock_repo.get_conversation.assert_called_once_with(1, 2)
    assert len(result) == 1
    assert result[0].content == "Hello"


def test_get_history_usecase_marca_leido_antes_de_leer():
    mock_repo = MagicMock()
    mock_repo.get_conversation.return_value = []

    GetHistoryUseCase(mock_repo).execute(1, 2)

    # El mark debe ocurrir antes del fetch para que la respuesta ya venga con is_read=True
    metodos_llamados = [name for name, _, _ in mock_repo.mock_calls]
    assert metodos_llamados.index("mark_conversation_read") < metodos_llamados.index("get_conversation")

def test_save_message_usecase():
    # Arrange
    mock_repo = MagicMock()
    mock_message = ChatMessage(
        message_id=1,
        sender_id=1,
        receiver_id=2,
        content="Hi there",
        is_read=False
    )
    mock_repo.save_message.return_value = mock_message
    
    usecase = SaveMessageUseCase(mock_repo)
    
    # Act
    result = usecase.execute(sender_id=1, receiver_id=2, content="Hi there")
    
    # Assert
    mock_repo.save_message.assert_called_once_with(1, 2, "Hi there")
    assert result.message_id == 1
    assert result.content == "Hi there"


def _summary(other_id: int, content: str, when: datetime, unread: int = 0) -> InboxSummary:
    return InboxSummary(
        other_user_id=other_id,
        last_message=ChatMessage(
            message_id=other_id, sender_id=other_id, receiver_id=1,
            content=content, created_at=when, is_read=False,
        ),
        unread_count=unread,
    )


def test_get_chat_inbox_usecase_compone_summaries_con_usuarios():
    mock_repo = MagicMock()
    mock_lookup = MagicMock()
    mock_repo.get_inbox.return_value = [
        _summary(2, "viejo", datetime(2026, 7, 1, 10, 0), unread=1),
        _summary(3, "reciente", datetime(2026, 7, 3, 10, 0)),
    ]
    mock_lookup.get_users_by_ids.return_value = [
        ChatUser(user_id=2, name="Ana", last_name="Ruiz", role="paciente"),
        ChatUser(user_id=3, name="Luis", last_name="Paz", role="doctor"),
    ]

    result = GetChatInboxUseCase(mock_repo, mock_lookup).execute(current_user_id=1)

    mock_lookup.get_users_by_ids.assert_called_once_with([2, 3])
    assert [item.other_user_id for item in result] == [3, 2]  # ordenado por mensaje mas reciente
    assert result[1].other_user_name == "Ana"
    assert result[1].unread_count == 1
    assert result[0].other_user_role == "doctor"


def test_get_chat_inbox_usecase_omite_usuarios_no_encontrados():
    mock_repo = MagicMock()
    mock_lookup = MagicMock()
    mock_repo.get_inbox.return_value = [_summary(2, "hola", datetime(2026, 7, 1))]
    mock_lookup.get_users_by_ids.return_value = []

    assert GetChatInboxUseCase(mock_repo, mock_lookup).execute(current_user_id=1) == []


def test_get_chat_inbox_usecase_inbox_vacio_no_consulta_usuarios():
    mock_repo = MagicMock()
    mock_lookup = MagicMock()
    mock_repo.get_inbox.return_value = []

    assert GetChatInboxUseCase(mock_repo, mock_lookup).execute(current_user_id=1) == []
    mock_lookup.get_users_by_ids.assert_not_called()


def test_get_chat_contacts_doctor_devuelve_sus_pacientes_y_recepcionista():
    lookup = MagicMock()
    lookup.get_doctor_id_for_doctor.return_value = 10
    lookup.get_patients_of_doctor.return_value = [
        ChatUser(user_id=2, name="Ana", last_name="Ruiz", role="paciente")
    ]
    lookup.get_receptionists_of_doctor.return_value = [
        ChatUser(user_id=3, name="Rosa", last_name="Marin", role="recepcionista")
    ]

    result = GetChatContactsUseCase(lookup).execute(current_user_id=1, role="doctor")

    lookup.get_doctor_id_for_doctor.assert_called_once_with(1)
    lookup.get_patients_of_doctor.assert_called_once_with(10)
    lookup.get_receptionists_of_doctor.assert_called_once_with(10)
    assert [contact.user_id for contact in result] == [2, 3]


def test_get_chat_contacts_doctor_sin_perfil_devuelve_lista_vacia():
    lookup = MagicMock()
    lookup.get_doctor_id_for_doctor.return_value = None

    assert GetChatContactsUseCase(lookup).execute(current_user_id=1, role="doctor") == []
    lookup.get_patients_of_doctor.assert_not_called()
    lookup.get_receptionists_of_doctor.assert_not_called()


def test_get_chat_contacts_recepcionista_devuelve_pacientes_y_su_doctor():
    lookup = MagicMock()
    lookup.get_doctor_id_for_receptionist.return_value = 10
    lookup.get_patients_of_doctor.return_value = [
        ChatUser(user_id=2, name="Ana", last_name="Ruiz", role="paciente"),
        ChatUser(user_id=3, name="Luis", last_name="Paz", role="paciente"),
    ]
    lookup.get_doctor_contact.return_value = ChatUser(
        user_id=4, name="Dra", last_name="Lopez", role="doctor"
    )

    result = GetChatContactsUseCase(lookup).execute(
        current_user_id=1, role="recepcionista"
    )

    lookup.get_doctor_id_for_receptionist.assert_called_once_with(1)
    lookup.get_patients_of_doctor.assert_called_once_with(10)
    lookup.get_doctor_contact.assert_called_once_with(10)
    assert [contact.user_id for contact in result] == [2, 3, 4]


def test_get_chat_contacts_recepcionista_sin_perfil_devuelve_lista_vacia():
    lookup = MagicMock()
    lookup.get_doctor_id_for_receptionist.return_value = None

    assert GetChatContactsUseCase(lookup).execute(current_user_id=1, role="recepcionista") == []
    lookup.get_patients_of_doctor.assert_not_called()
    lookup.get_doctor_contact.assert_not_called()


def test_get_chat_contacts_paciente_devuelve_doctor_y_recepcionistas():
    lookup = MagicMock()
    lookup.get_doctor_id_for_patient.return_value = 10
    lookup.get_doctor_contact.return_value = ChatUser(
        user_id=5, name="Dra", last_name="Lopez", role="doctor"
    )
    lookup.get_receptionists_of_doctor.return_value = [
        ChatUser(user_id=6, name="Rosa", last_name="Marin", role="recepcionista")
    ]

    result = GetChatContactsUseCase(lookup).execute(current_user_id=1, role="paciente")

    lookup.get_doctor_contact.assert_called_once_with(10)
    lookup.get_receptionists_of_doctor.assert_called_once_with(10)
    assert [contact.role for contact in result] == ["doctor", "recepcionista"]


def test_get_chat_contacts_rol_no_contemplado_devuelve_lista_vacia():
    lookup = MagicMock()

    assert GetChatContactsUseCase(lookup).execute(current_user_id=1, role="admin") == []
