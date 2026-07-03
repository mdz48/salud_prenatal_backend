from typing import List
from app.features.chat.domain.ports import IChatRepository
from app.features.chat.domain.inbox_item_response import InboxItemResponse

class GetChatInboxUseCase:
    def __init__(self, chat_repository: IChatRepository):
        self.chat_repository = chat_repository

    def execute(self, current_user_id: int) -> List[InboxItemResponse]:
        return self.chat_repository.get_inbox(current_user_id)
