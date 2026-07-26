from typing import List, Optional
from app.users.domain.ports import IUnlinkRequestRepository
from app.users.domain.unlink_request_entity import UnlinkRequestEntity


class ListPatientUnlinkRequestsUseCase:
    """Lista las solicitudes de desvinculacion de una paciente (para que la app
    de la paciente pueda mostrar el estado: pendiente / aprobada / rechazada).
    """
    def __init__(self, unlink_request_repository: IUnlinkRequestRepository):
        self.unlink_request_repository = unlink_request_repository

    def execute(self, patient_id: int, status: Optional[str] = None) -> List[UnlinkRequestEntity]:
        return self.unlink_request_repository.list_by_patient(patient_id, status)
