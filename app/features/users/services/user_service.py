from sqlalchemy.orm import Session
from app.features.users.repositories.user_repository import user_repository
from app.features.users.schemas.user_schema import UserCreate, UserUpdate
from app.core.security import get_password_hash

class UserService:
    def get_user(self, db: Session, user_id: int):
        return user_repository.get_by_id(db, user_id)

    def get_user_by_email(self, db: Session, email: str):
        return user_repository.get_by_email(db, email)

    def get_users(self, db: Session, skip: int = 0, limit: int = 100):
        return user_repository.get_all(db, skip=skip, limit=limit)

    def create_user(self, db: Session, user: UserCreate):
        existing_user = user_repository.get_by_email(db, user.email)
        if existing_user:
            raise ValueError("Email already registered")
        user.password = get_password_hash(user.password)
        return user_repository.create(db, user)

    def update_user(self, db: Session, user_id: int, user: UserUpdate):
        if user.password:
            user.password = get_password_hash(user.password)
        return user_repository.update(db, user_id, user)

    def delete_user(self, db: Session, user_id: int):
        return user_repository.delete(db, user_id)

user_service = UserService()
