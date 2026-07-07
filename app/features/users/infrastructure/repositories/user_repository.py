from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from app.features.users.infrastructure.models.user_model import Usuario
from app.features.users.domain.ports import IUserRepository
from app.features.users.domain.user_entity import UserEntity
from typing import Optional

class UserRepository(IUserRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[UserEntity]:
        user_db = self.db.query(Usuario).filter(Usuario.user_id == user_id).first()
        return UserEntity.model_validate(user_db) if user_db else None

    def get_by_email(self, email: str) -> Optional[UserEntity]:
        user_db = self.db.query(Usuario).filter(Usuario.email == email).first()
        return UserEntity.model_validate(user_db) if user_db else None

    def get_by_ids(self, user_ids: List[int]) -> List[UserEntity]:
        users_db = self.db.query(Usuario).filter(Usuario.user_id.in_(user_ids)).all()
        return [UserEntity.model_validate(u) for u in users_db]

    def get_all(self, skip: int = 0, limit: int = 100) -> List[UserEntity]:
        users_db = self.db.query(Usuario).offset(skip).limit(limit).all()
        return [UserEntity.model_validate(u) for u in users_db]

    def create(self, user: UserEntity) -> UserEntity:
        user_data = user.model_dump(exclude={'user_id', 'created_at', 'updated_at'}, exclude_unset=True)
        db_user = Usuario(**user_data)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return UserEntity.model_validate(db_user)

    def update(self, user_id: int, user_data: UserEntity) -> Optional[UserEntity]:
        db_user = self.db.query(Usuario).filter(Usuario.user_id == user_id).first()
        if not db_user:
            return None
        
        update_data = user_data.model_dump(exclude={'user_id', 'created_at', 'updated_at'}, exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)
            
        self.db.commit()
        self.db.refresh(db_user)
        return UserEntity.model_validate(db_user)

    def delete(self, user_id: int):
        db_user = self.db.query(Usuario).filter(Usuario.user_id == user_id).first()
        if db_user:
            db_user.is_active = False
            self.db.commit()
            self.db.refresh(db_user)
            return UserEntity.model_validate(db_user)
        return None
