from datetime import datetime, timezone
from app.users.domain.ports import IUnlinkRequestRepository
from app.users.domain.unlink_request_entity import UnlinkRequestEntity


class CancelUnlinkRequestUseCase:
    """La paciente cancela su propia solicitud mientras siga pendiente."""
    def __init__(self, unlink_request_repository: IUnlinkRequestRepository):
        self.unlink_request_repository = unlink_request_repository

    def execute(self, patient_id: int, request_id: int) -> UnlinkRequestEntity:
        request = self.unlink_request_repository.get_by_id(request_id)
        if not request:
            raise ValueError("Unlink request not found")

        if request.patient_id != patient_id:
            raise ValueError("Unlink request does not belong to this patient")

        if request.status != "pending":
            raise ValueError("Unlink request is already resolved")

        return self.unlink_request_repository.update_status(
            request_id, "cancelled", datetime.now(timezone.utc)
        )
