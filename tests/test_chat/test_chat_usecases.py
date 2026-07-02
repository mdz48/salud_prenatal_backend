from unittest.mock import MagicMock
from app.features.chat.application.get_history_usecase import GetHistoryUseCase
from app.features.chat.application.save_message_usecase import SaveMessageUseCase
from app.features.chat.domain.entities import ChatMessage

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
