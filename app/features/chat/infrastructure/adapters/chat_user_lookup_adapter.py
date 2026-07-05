from typing import List
from app.features.chat.domain.ports import IChatUserLookup, ChatUser
from app.features.users.infrastructure.repositories.user_repository import UserRepository


class ChatUserLookupAdapter(IChatUserLookup):
    """Traduce UserEntity (users) -> ChatUser (chat). Unico punto de contacto entre features."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def get_users_by_ids(self, user_ids: List[int]) -> List[ChatUser]:
        return [
            ChatUser(
                user_id=u.user_id,
                name=u.name,
                last_name=u.last_name,
                role=u.role.value if hasattr(u.role, "value") else str(u.role),
            )
            for u in self.user_repository.get_by_ids(user_ids)
        ]
