from app.features.chat.domain.ports import IChatRepository
from app.features.chat.domain.chat_message_entity import ChatMessage

class SaveMessageUseCase:
    def __init__(self, chat_repository: IChatRepository):
        self.chat_repository = chat_repository

    def execute(self, sender_id: int, receiver_id: int, content: str) -> ChatMessage:
        return self.chat_repository.save_message(sender_id, receiver_id, content)
