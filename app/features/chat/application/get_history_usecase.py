from typing import List
from app.features.chat.domain.ports import IChatRepository
from app.features.chat.domain.chat_message_entity import ChatMessage

class GetHistoryUseCase:
    def __init__(self, chat_repository: IChatRepository):
        self.chat_repository = chat_repository

    def execute(self, user1_id: int, user2_id: int) -> List[ChatMessage]:
        # user1_id es quien consulta: consumir el history marca como leidos
        # los mensajes que le llegaron de user2_id, antes de leerlos, para que
        # la respuesta ya refleje is_read=True.
        self.chat_repository.mark_conversation_read(reader_id=user1_id, other_user_id=user2_id)
        return self.chat_repository.get_conversation(user1_id, user2_id)
