"""IChatUserLookup leyendo `users` directo de la DB compartida (read-model)."""
from typing import List
from sqlalchemy.orm import Session

from app.chat.domain.ports import IChatUserLookup
from app.chat.domain.dtos import ChatUser
from app.readmodels.users_readmodels import UserRead


class ChatUserLookupAdapter(IChatUserLookup):
    def __init__(self, db: Session):
        self.db = db

    def get_users_by_ids(self, user_ids: List[int]) -> List[ChatUser]:
        users = self.db.query(UserRead).filter(UserRead.user_id.in_(user_ids)).all()
        return [
            ChatUser(
                user_id=u.user_id,
                name=u.name,
                last_name=u.last_name,
                role=u.role.value if hasattr(u.role, "value") else str(u.role),
            )
            for u in users
        ]
