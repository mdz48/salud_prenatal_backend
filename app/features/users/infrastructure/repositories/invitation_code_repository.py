from sqlalchemy.orm import Session
from app.features.users.infrastructure.models.invitation_code_model import InvitationCode
from app.features.users.domain.ports import IInvitationCodeRepository
from app.features.users.domain.invitation_code_entity import InvitationCodeEntity
from app.features.users.domain.invitation_code_factory import (
    InvitationCodeFactory,
    UuidInvitationCodeFactory,
)
from typing import Optional

class InvitationCodeRepository(IInvitationCodeRepository):
    def __init__(self, db: Session, code_factory: Optional[InvitationCodeFactory] = None):
        self.db = db
        # Factory Method: la generación del código/expiración se delega a la fábrica.
        self.code_factory = code_factory or UuidInvitationCodeFactory()

    def create(self, doctor_id: int) -> InvitationCodeEntity:
        db_invitation_code = InvitationCode(**self.code_factory.build(doctor_id))
        self.db.add(db_invitation_code)
        self.db.commit()
        self.db.refresh(db_invitation_code)
        return InvitationCodeEntity.model_validate(db_invitation_code)

    def get_by_code(self, code: str) -> Optional[InvitationCodeEntity]:
        db_code = self.db.query(InvitationCode).filter(InvitationCode.code == code).first()
        return InvitationCodeEntity.model_validate(db_code) if db_code else None

    def mark_used(self, code_id: int, patient_id: int) -> Optional[InvitationCodeEntity]:
        db_code = self.db.query(InvitationCode).filter(InvitationCode.invitation_code_id == code_id).first()
        if db_code:
            db_code.is_used = True
            db_code.used_by_patient_id = patient_id
            self.db.commit()
            self.db.refresh(db_code)
            return InvitationCodeEntity.model_validate(db_code)
        return None
