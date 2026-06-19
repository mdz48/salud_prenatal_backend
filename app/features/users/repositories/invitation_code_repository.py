import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.features.users.models.invitation_code_model import InvitationCode

class InvitationCodeRepository:
    def create(self, db: Session, doctor_id: int, commit: bool = True):
        # Generate an 8-character UUID-based code
        code = str(uuid.uuid4())[:8]
        expires_at = datetime.utcnow() + timedelta(hours=72)
        
        db_invitation_code = InvitationCode(
            code=code,
            doctor_id=doctor_id,
            expires_at=expires_at
        )
        db.add(db_invitation_code)
        if commit:
            db.commit()
            db.refresh(db_invitation_code)
        else:
            db.flush()
        return db_invitation_code

    def get_by_code(self, db: Session, code: str):
        return db.query(InvitationCode).filter(InvitationCode.code == code).first()

    def mark_used(self, db: Session, code_obj: InvitationCode, patient_id: int, commit: bool = True):
        code_obj.is_used = True
        code_obj.used_by_patient_id = patient_id
        if commit:
            db.commit()
            db.refresh(code_obj)
        else:
            db.flush()
        return code_obj

invitation_code_repository = InvitationCodeRepository()
