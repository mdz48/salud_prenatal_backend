from typing import Optional

from app.features.forums.domain.ports import IAuthorRoleLookup
from app.features.users.infrastructure.repositories.user_repository import UserRepository

class AuthorRoleAdapter(IAuthorRoleLookup):
    """Resuelve el rol del autor de un post (forums -> users) para gatear la
    publicidad: solo los doctores pueden marcar un post como anuncio."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def get_role(self, user_id: int) -> Optional[str]:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            return None
        role = user.role
        return role.value if hasattr(role, "value") else str(role)
