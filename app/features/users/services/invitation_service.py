from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.features.users.repositories.invitation_code_repository import invitation_code_repository
from app.features.users.repositories.patient_repository import patient_repository

class InvitationService:
    def redeem_code(self, db: Session, code: str, patient_id: int):
        code_obj = invitation_code_repository.get_by_code(db, code)
        if not code_obj:
            raise ValueError("Invalid invitation code")
        if code_obj.is_used:
            raise ValueError("Invitation code already used")
        if code_obj.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            raise ValueError("Invitation code expired")
        
        patient = patient_repository.update_doctor(db, patient_id, code_obj.doctor_id)
        if not patient:
            raise ValueError("Patient not found")
            
        invitation_code_repository.mark_used(db, code_obj, patient_id)
        return patient

invitation_service = InvitationService()
