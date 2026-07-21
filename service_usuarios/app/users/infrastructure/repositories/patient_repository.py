from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.users.infrastructure.models.patient_model import Patient
from app.users.infrastructure.models.user_model import Usuario
from app.users.domain.ports import IPatientRepository
from app.users.domain.patient_entity import PatientEntity
from app.users.domain.patient_directory_query import PatientDirectoryQuery
from salud_prenatal_shared_core.time import now_cdmx
from typing import Optional

class PatientRepository(IPatientRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, patient_id: int) -> Optional[PatientEntity]:
        db_patient = self.db.query(Patient).filter(Patient.patient_id == patient_id).first()
        return PatientEntity.model_validate(db_patient) if db_patient else None

    def get_by_user_id(self, user_id: int) -> Optional[PatientEntity]:
        db_patient = self.db.query(Patient).filter(Patient.user_id == user_id).first()
        return PatientEntity.model_validate(db_patient) if db_patient else None

    def get_patients_by_doctor(self, doctor_id: int) -> List[PatientEntity]:
        db_patients = (
            self.db.query(Patient)
            .options(joinedload(Patient.user))
            .join(Usuario, Patient.user_id == Usuario.user_id)
            .filter(Patient.doctor_id == doctor_id, Usuario.is_active == True)
            .all()
        )
        return [PatientEntity.model_validate(p) for p in db_patients]

    def create(self, patient: PatientEntity) -> PatientEntity:
        patient_data = patient.model_dump(exclude={'patient_id'}, exclude_unset=True)
        db_patient = Patient(**patient_data)
        self.db.add(db_patient)
        self.db.commit()
        self.db.refresh(db_patient)
        return PatientEntity.model_validate(db_patient)

    def update(self, patient_id: int, patient_data: PatientEntity) -> Optional[PatientEntity]:
        db_patient = self.db.query(Patient).filter(Patient.patient_id == patient_id).first()
        if not db_patient:
            return None

        update_data = patient_data.model_dump(exclude={'patient_id'}, exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_patient, key, value)

        self.db.commit()
        self.db.refresh(db_patient)
        return PatientEntity.model_validate(db_patient)

    def search_directory(self, query: PatientDirectoryQuery) -> List[PatientEntity]:
        if query.patient_ids_filter is not None and not query.patient_ids_filter:
            return []

        q = self.db.query(Patient).filter(Patient.doctor_id == query.doctor_id)
        if query.patient_ids_filter is not None:
            q = q.filter(Patient.patient_id.in_(query.patient_ids_filter))
        if query.linked_after:
            q = q.filter(Patient.linked_at >= query.linked_after)
        if query.linked_before:
            q = q.filter(Patient.linked_at <= query.linked_before)

        return [PatientEntity.model_validate(p) for p in q.all()]

    def update_doctor(self, patient_id: int, doctor_id: Optional[int]) -> Optional[PatientEntity]:
        db_patient = self.db.query(Patient).filter(Patient.patient_id == patient_id).first()
        if db_patient:
            db_patient.doctor_id = doctor_id
            db_patient.linked_at = now_cdmx() if doctor_id is not None else None
            self.db.commit()
            self.db.refresh(db_patient)
            return PatientEntity.model_validate(db_patient)
        return None
