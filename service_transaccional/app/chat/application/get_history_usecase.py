from typing import List
from app.chat.domain.ports import IChatRepository
from app.chat.domain.chat_message_entity import ChatMessage

class GetHistoryUseCase:
    def __init__(self, chat_repository: IChatRepository):
        self.chat_repository = chat_repository

    def execute(self, user1_id: int, user2_id: int) -> List[ChatMessage]:
        return self.chat_repository.get_conversation(user1_id, user2_id)
