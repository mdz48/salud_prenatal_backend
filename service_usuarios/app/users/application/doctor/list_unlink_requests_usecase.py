from typing import List, Optional
from app.users.domain.ports import IUnlinkRequestRepository
from app.users.domain.unlink_request_entity import UnlinkRequestEntity


class ListUnlinkRequestsUseCase:
    """Bandeja del doctor: solicitudes de desvinculacion que le llegaron. Con
    `status` (p. ej. 'pending') se filtra; sin el, devuelve todo el historial.
    Cada solicitud trae `patient_full_name` resuelto para pintarla directo.
    """
    def __init__(self, unlink_request_repository: IUnlinkRequestRepository):
        self.unlink_request_repository = unlink_request_repository

    def execute(self, doctor_id: int, status: Optional[str] = None) -> List[UnlinkRequestEntity]:
        return self.unlink_request_repository.list_by_doctor(doctor_id, status)
