"""Implementan IPatientLookup / IDoctorLookup de appointments leyendo `patients` y
`doctors` de la DB compartida (read-models). appointments solo verifica EXISTENCIA
(truth-test), por eso basta devolver la fila o None.
"""
from typing import Optional
from sqlalchemy.orm import Session

from app.appointments.domain.ports import IPatientLookup, IDoctorLookup
from app.readmodels.users_readmodels import PatientRead, DoctorRead


class PatientLookupAdapter(IPatientLookup):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, patient_id: int) -> Optional[object]:
        return self.db.query(PatientRead).filter(PatientRead.patient_id == patient_id).first()


class DoctorLookupAdapter(IDoctorLookup):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, doctor_id: int) -> Optional[object]:
        return self.db.query(DoctorRead).filter(DoctorRead.doctor_id == doctor_id).first()
