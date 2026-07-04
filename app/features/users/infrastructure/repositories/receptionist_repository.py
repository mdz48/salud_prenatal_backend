from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from app.features.users.infrastructure.models.receptionist_model import Receptionist
from app.features.users.infrastructure.models.user_model import Usuario
from app.features.users.domain.ports import IReceptionistRepository
from app.features.users.domain.receptionist_entity import ReceptionistEntity
from app.features.users.domain.user_entity import UserEntity
from typing import Optional

class ReceptionistRepository(IReceptionistRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: int) -> Optional[ReceptionistEntity]:
        db_rec = self.db.query(Receptionist).filter(Receptionist.user_id == user_id).first()
        return ReceptionistEntity.model_validate(db_rec) if db_rec else None

    def create(self, receptionist: ReceptionistEntity) -> ReceptionistEntity:
        rec_data = receptionist.model_dump(exclude={'receptionist_id'}, exclude_unset=True)
        db_receptionist = Receptionist(**rec_data)
        self.db.add(db_receptionist)
        self.db.commit()
        self.db.refresh(db_receptionist)
        return ReceptionistEntity.model_validate(db_receptionist)

    def get_by_doctor_id(self, doctor_id: int) -> List[UserEntity]:
        db_users = self.db.query(Usuario).join(Receptionist).filter(Receptionist.doctor_id == doctor_id).all()
        return [UserEntity.model_validate(u) for u in db_users]
