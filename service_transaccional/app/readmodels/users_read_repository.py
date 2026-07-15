"""Repositorio de solo lectura sobre `users` (DB compartida) para consumidores de
transaccional que solo necesitan datos básicos del usuario (p. ej. el nombre del
remitente para una push de chat). No escribe: el ciclo de vida de `users` es del
servicio usuarios.
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.readmodels.users_readmodels import UserRead


class UsersReadRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[UserRead]:
        return self.db.query(UserRead).filter(UserRead.user_id == user_id).first()

    def get_by_ids(self, user_ids: List[int]) -> List[UserRead]:
        return self.db.query(UserRead).filter(UserRead.user_id.in_(user_ids)).all()
