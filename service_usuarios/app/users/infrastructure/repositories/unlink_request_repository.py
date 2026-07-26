from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.users.infrastructure.models.unlink_request_model import UnlinkRequest
from app.users.infrastructure.models.patient_model import Patient
from app.users.domain.ports import IUnlinkRequestRepository
from app.users.domain.unlink_request_entity import UnlinkRequestEntity


class UnlinkRequestRepository(IUnlinkRequestRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, patient_id: int, doctor_id: int, reason: Optional[str]) -> UnlinkRequestEntity:
        db_request = UnlinkRequest(
            patient_id=patient_id,
            doctor_id=doctor_id,
            reason=reason,
            status="pending",
        )
        self.db.add(db_request)
        self.db.commit()
        self.db.refresh(db_request)
        return UnlinkRequestEntity.model_validate(db_request)

    def get_by_id(self, request_id: int) -> Optional[UnlinkRequestEntity]:
        db_request = (
            self.db.query(UnlinkRequest)
            .filter(UnlinkRequest.unlink_request_id == request_id)
            .first()
        )
        return UnlinkRequestEntity.model_validate(db_request) if db_request else None

    def get_pending_for_pair(self, patient_id: int, doctor_id: int) -> Optional[UnlinkRequestEntity]:
        db_request = (
            self.db.query(UnlinkRequest)
            .filter(
                UnlinkRequest.patient_id == patient_id,
                UnlinkRequest.doctor_id == doctor_id,
                UnlinkRequest.status == "pending",
            )
            .first()
        )
        return UnlinkRequestEntity.model_validate(db_request) if db_request else None

    def list_by_doctor(self, doctor_id: int, status: Optional[str] = None) -> List[UnlinkRequestEntity]:
        query = (
            self.db.query(UnlinkRequest)
            .options(joinedload(UnlinkRequest.patient).joinedload(Patient.user))
            .filter(UnlinkRequest.doctor_id == doctor_id)
        )
        if status:
            query = query.filter(UnlinkRequest.status == status)
        db_requests = query.order_by(UnlinkRequest.created_at.desc()).all()
        return [self._to_entity_with_name(r) for r in db_requests]

    def list_by_patient(self, patient_id: int, status: Optional[str] = None) -> List[UnlinkRequestEntity]:
        query = self.db.query(UnlinkRequest).filter(UnlinkRequest.patient_id == patient_id)
        if status:
            query = query.filter(UnlinkRequest.status == status)
        db_requests = query.order_by(UnlinkRequest.created_at.desc()).all()
        return [UnlinkRequestEntity.model_validate(r) for r in db_requests]

    def update_status(self, request_id: int, status: str, resolved_at: Optional[datetime]) -> Optional[UnlinkRequestEntity]:
        db_request = (
            self.db.query(UnlinkRequest)
            .filter(UnlinkRequest.unlink_request_id == request_id)
            .first()
        )
        if not db_request:
            return None
        db_request.status = status
        db_request.resolved_at = resolved_at
        self.db.commit()
        self.db.refresh(db_request)
        return UnlinkRequestEntity.model_validate(db_request)

    def _to_entity_with_name(self, db_request: UnlinkRequest) -> UnlinkRequestEntity:
        entity = UnlinkRequestEntity.model_validate(db_request)
        patient = db_request.patient
        if patient is not None and patient.user is not None:
            entity.patient_full_name = f"{patient.user.name} {patient.user.last_name}"
        return entity
