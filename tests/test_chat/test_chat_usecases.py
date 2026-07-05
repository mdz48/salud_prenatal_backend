from datetime import datetime
from unittest.mock import MagicMock
from app.features.chat.application.get_history_usecase import GetHistoryUseCase
from app.features.chat.application.save_message_usecase import SaveMessageUseCase
from app.features.chat.application.get_chat_inbox_usecase import GetChatInboxUseCase
from app.features.chat.domain.chat_message_entity import ChatMessage
from app.features.chat.domain.ports import ChatUser, InboxSummary

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
    mock_repo.get_conversation.assert_called_once_with(1, 2)
    assert len(result) == 1
    assert result[0].content == "Hello"

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
