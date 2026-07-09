from datetime import datetime, timezone
from typing import Optional

from app.core.events.event_bus import EventBus
from app.core.events.events import PatientLinkedToDoctorEvent
from app.features.users.domain.ports import IPatientRepository, IInvitationCodeRepository

class RedeemInvitationCodeUseCase:
    def __init__(
        self,
        patient_repository: IPatientRepository,
        invitation_code_repository: IInvitationCodeRepository,
        event_bus: Optional[EventBus] = None,
    ):
        self.patient_repository = patient_repository
        self.invitation_code_repository = invitation_code_repository
        self.event_bus = event_bus

    def execute(self, patient_id: int, code: str):
        code_obj = self.invitation_code_repository.get_by_code(code)
        if not code_obj:
            raise ValueError("Invalid invitation code")
        if code_obj.is_used:
            raise ValueError("Invitation code already used")
        if code_obj.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            raise ValueError("Invitation code expired")

        patient = self.patient_repository.update_doctor(patient_id, code_obj.doctor_id)
        if not patient:
            raise ValueError("Patient not found")

        self.invitation_code_repository.mark_used(code_obj.invitation_code_id, patient_id)

        if self.event_bus:
            self.event_bus.publish(
                PatientLinkedToDoctorEvent(patient_id=patient_id, doctor_id=code_obj.doctor_id)
            )

        return patient
