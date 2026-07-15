"""Lecturas de solo lectura para el login, contra la DB compartida.

Reemplaza a los repos/adapters que en el monolito vivían en la feature `users`
(user/patient/doctor/receptionist repositories + medical_record & subscription
lookups). Aquí es UN solo repositorio de lectura sobre los read-models de auth.
"""
from typing import Optional, List
from sqlalchemy.orm import Session

from app.auth.domain.ports import IAuthReadPort
from app.auth.infrastructure.models.auth_readmodels import (
    UserAuth,
    PatientAuth,
    DoctorAuth,
    ReceptionistAuth,
    MedicalRecordAuth,
    SubscriptionAuth,
)


class AuthReadRepository(IAuthReadPort):
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str) -> Optional[UserAuth]:
        return self.db.query(UserAuth).filter(UserAuth.email == email).first()

    def get_user_by_id(self, user_id: int) -> Optional[UserAuth]:
        return self.db.query(UserAuth).filter(UserAuth.user_id == user_id).first()

    def get_patient_by_user_id(self, user_id: int) -> Optional[PatientAuth]:
        return self.db.query(PatientAuth).filter(PatientAuth.user_id == user_id).first()

    def get_doctor_by_user_id(self, user_id: int) -> Optional[DoctorAuth]:
        return self.db.query(DoctorAuth).filter(DoctorAuth.user_id == user_id).first()

    def get_receptionist_by_user_id(self, user_id: int) -> Optional[ReceptionistAuth]:
        return (
            self.db.query(ReceptionistAuth)
            .filter(ReceptionistAuth.user_id == user_id)
            .first()
        )

    def get_receptionists_by_doctor_id(self, doctor_id: int) -> List[ReceptionistAuth]:
        return (
            self.db.query(ReceptionistAuth)
            .filter(ReceptionistAuth.doctor_id == doctor_id)
            .all()
        )

    def get_medical_record_id(self, patient_id: int, doctor_id: int) -> Optional[int]:
        mr = (
            self.db.query(MedicalRecordAuth)
            .filter(
                MedicalRecordAuth.patient_id == patient_id,
                MedicalRecordAuth.doctor_id == doctor_id,
            )
            .first()
        )
        return mr.medical_record_id if mr else None

    def get_subscription_status(self, user_id: int) -> Optional[str]:
        sub = (
            self.db.query(SubscriptionAuth)
            .filter(SubscriptionAuth.user_id == user_id)
            .first()
        )
        return sub.status.value if sub else None
