from typing import Optional
from app.users.domain.ports import IPatientRepository, IUnlinkRequestRepository
from app.users.domain.unlink_request_entity import UnlinkRequestEntity


class CreateUnlinkRequestUseCase:
    """La paciente solicita desvincularse de su doctor actual. No desvincula
    nada: solo crea la solicitud en estado 'pending' para que el doctor la
    resuelva. El doctor se toma del vinculo vigente de la paciente, no del
    cliente, para que no pueda pedir desvincularse de un doctor que no es el
    suyo.
    """
    def __init__(self, patient_repository: IPatientRepository, unlink_request_repository: IUnlinkRequestRepository):
        self.patient_repository = patient_repository
        self.unlink_request_repository = unlink_request_repository

    def execute(self, patient_id: int, reason: Optional[str] = None) -> UnlinkRequestEntity:
        patient = self.patient_repository.get_by_id(patient_id)
        if not patient:
            raise ValueError("Patient not found")

        if patient.doctor_id is None:
            raise ValueError("Patient has no assigned doctor")

        existing = self.unlink_request_repository.get_pending_for_pair(patient_id, patient.doctor_id)
        if existing:
            raise ValueError("There is already a pending unlink request")

        return self.unlink_request_repository.create(
            patient_id=patient_id,
            doctor_id=patient.doctor_id,
            reason=reason,
        )
