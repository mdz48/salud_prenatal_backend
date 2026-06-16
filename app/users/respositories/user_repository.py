from sqlalchemy.orm import Session
from app.users.models.user_model import Usuario
from app.users.schemas.user_schema import UserCreate, UserUpdate

class UserRepository:
    def get_by_id(self, db: Session, user_id: int):
        return db.query(Usuario).filter(Usuario.user_id == user_id).first()

    def get_by_email(self, db: Session, email: str):
        return db.query(Usuario).filter(Usuario.email == email).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(Usuario).offset(skip).limit(limit).all()

    def create(self, db: Session, user_in: UserCreate):
        user_data = user_in.model_dump()
        db_user = Usuario(**user_data)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def create_from_dict(self, db: Session, user_data: dict, commit: bool = True):
        db_user = Usuario(**user_data)
        db.add(db_user)
        if commit:
            db.commit()
            db.refresh(db_user)
        else:
            db.flush()
        return db_user

    def update(self, db: Session, user_id: int, user_in: UserUpdate):
        db_user = self.get_by_id(db, user_id)
        if not db_user:
            return None
        
        update_data = user_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)
            
        db.commit()
        db.refresh(db_user)
        return db_user

    def delete(self, db: Session, user_id: int):
        db_user = self.get_by_id(db, user_id)
        if db_user:
            db_user.is_active = False
            db.commit()
            db.refresh(db_user)
        return db_user

user_repository = UserRepository()
