from sqlalchemy.orm import Session
from app.users.respositories.user_repository import user_repository
from app.core.security import verify_password, create_access_token

class AuthService:
    def authenticate_user(self, db: Session, email: str, password: str):
        user = user_repository.get_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    def login(self, db: Session, email: str, password: str):
        user = self.authenticate_user(db, email, password)
        if not user:
            raise ValueError("Incorrect email or password")
        
        if not user.is_active:
            raise ValueError("Inactive user")

        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.user_id, "role": user.role}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.user_id,
            "role": user.role.value if hasattr(user.role, 'value') else str(user.role)
        }

auth_service = AuthService()
