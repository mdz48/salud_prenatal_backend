from typing import List
from app.chat.domain.ports import IChatRepository, IChatUserLookup
from app.chat.domain.inbox_item_response import InboxItemResponse

class GetChatInboxUseCase:
    def __init__(self, chat_repository: IChatRepository, user_lookup: IChatUserLookup):
        self.chat_repository = chat_repository
        self.user_lookup = user_lookup

    def execute(self, current_user_id: int) -> List[InboxItemResponse]:
        summaries = self.chat_repository.get_inbox(current_user_id)
        if not summaries:
            return []

        users = self.user_lookup.get_users_by_ids([s.other_user_id for s in summaries])
        user_map = {u.user_id: u for u in users}

        result = [
            InboxItemResponse(
                other_user_id=user.user_id,
                other_user_name=user.name,
                other_user_lastname=user.last_name,
                other_user_role=user.role,
                last_message=summary.last_message,
                unread_count=summary.unread_count,
            )
            for summary in summaries
            if (user := user_map.get(summary.other_user_id))
        ]
        result.sort(key=lambda item: item.last_message.created_at, reverse=True)
        return result
