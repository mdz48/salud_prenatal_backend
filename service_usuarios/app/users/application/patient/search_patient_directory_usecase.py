from datetime import datetime
from typing import List, Optional

from app.users.domain.ports import IPatientRepository, IPatientClinicalFilterPort
from app.users.domain.patient_entity import PatientEntity
from app.users.domain.patient_directory_query import PatientDirectoryQuery


class SearchPatientDirectoryUseCase:
    def __init__(
        self,
        patient_repository: IPatientRepository,
        clinical_filter_port: Optional[IPatientClinicalFilterPort] = None,
    ):
        self.patient_repository = patient_repository
        self.clinical_filter_port = clinical_filter_port

    def execute(
        self,
        doctor_id: int,
        risk_cluster: Optional[str] = None,
        linked_after: Optional[datetime] = None,
        linked_before: Optional[datetime] = None,
    ) -> List[PatientEntity]:
        patient_ids_filter = None
        if risk_cluster:
            patient_ids_filter = self.clinical_filter_port.get_patient_ids_by_risk_cluster(
                doctor_id=doctor_id, risk_cluster=risk_cluster
            )
            if not patient_ids_filter:
                return []

        query = PatientDirectoryQuery(
            doctor_id=doctor_id,
            patient_ids_filter=patient_ids_filter,
            linked_after=linked_after,
            linked_before=linked_before,
        )
        return self.patient_repository.search_directory(query)
