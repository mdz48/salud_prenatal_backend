from datetime import datetime, timezone
from app.users.domain.ports import IUnlinkRequestRepository
from app.users.domain.unlink_request_entity import UnlinkRequestEntity
from app.users.application.patient.unlink_patient_usecase import UnlinkPatientUseCase


class ResolveUnlinkRequestUseCase:
    """El doctor aprueba o rechaza una solicitud de desvinculacion.

    Solo al APROBAR se ejecuta la desvinculacion real, reutilizando
    UnlinkPatientUseCase (cancela citas futuras + pone doctor_id = NULL). Al
    rechazar solo se marca la solicitud; la paciente sigue vinculada.
    """
    def __init__(self, unlink_request_repository: IUnlinkRequestRepository, unlink_patient_use_case: UnlinkPatientUseCase):
        self.unlink_request_repository = unlink_request_repository
        self.unlink_patient_use_case = unlink_patient_use_case

    def execute(self, doctor_id: int, request_id: int, new_status: str) -> UnlinkRequestEntity:
        if new_status not in ("approved", "rejected"):
            raise ValueError("Invalid status: must be 'approved' or 'rejected'")

        request = self.unlink_request_repository.get_by_id(request_id)
        if not request:
            raise ValueError("Unlink request not found")

        if request.doctor_id != doctor_id:
            raise ValueError("Unlink request does not belong to this doctor")

        if request.status != "pending":
            raise ValueError("Unlink request is already resolved")

        if new_status == "approved":
            # Ejecuta la desvinculacion real. Si el vinculo ya no existe
            # (p. ej. la paciente ya no es de este doctor) UnlinkPatientUseCase
            # lanza ValueError y la solicitud NO se marca como aprobada.
            self.unlink_patient_use_case.execute(doctor_id=doctor_id, patient_id=request.patient_id)

        return self.unlink_request_repository.update_status(
            request_id, new_status, datetime.now(timezone.utc)
        )
