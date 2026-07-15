from fastapi import HTTPException, status
from app.features.medical_record.infrastructure.schemas.medical_record_schema import MedicalRecordCreate, MedicalRecordUpdate
from app.features.medical_record.application.create_medical_record_usecase import CreateMedicalRecordUseCase
from app.features.medical_record.application.get_patient_medical_record_usecase import GetPatientMedicalRecordUseCase
from app.features.medical_record.application.update_medical_record_usecase import UpdateMedicalRecordUseCase
from app.features.medical_record.application.search_medical_records_by_patient_name_usecase import SearchMedicalRecordsByPatientNameUseCase
from app.features.medical_record.application.evaluate_patient_risk_usecase import EvaluatePatientRiskUseCase
from app.features.medical_record.domain.medical_record_entity import MedicalRecordEntity

class MedicalRecordController:
    def __init__(
        self,
        create_medical_record_use_case: CreateMedicalRecordUseCase,
        get_patient_medical_record_use_case: GetPatientMedicalRecordUseCase,
        update_medical_record_use_case: UpdateMedicalRecordUseCase,
        search_medical_records_by_patient_name_use_case: SearchMedicalRecordsByPatientNameUseCase,
        evaluate_patient_risk_use_case: EvaluatePatientRiskUseCase
    ):
        self.create_medical_record_use_case = create_medical_record_use_case
        self.get_patient_medical_record_use_case = get_patient_medical_record_use_case
        self.update_medical_record_use_case = update_medical_record_use_case
        self.search_medical_records_by_patient_name_use_case = search_medical_records_by_patient_name_use_case
        self.evaluate_patient_risk_use_case = evaluate_patient_risk_use_case

    def create_medical_record(self, data: MedicalRecordCreate):
        try:
            entity_data = MedicalRecordEntity(**data.model_dump())
            result_entity = self.create_medical_record_use_case.execute(data=entity_data)
            return result_entity
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while creating the medical record.")

    def get_patient_medical_record(self, patient_id: int, doctor_id: int):
        try:
            return self.get_patient_medical_record_use_case.execute(patient_id=patient_id, doctor_id=doctor_id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while retrieving the medical record.")

    def search_medical_records(self, doctor_id: int, name=None, last_name=None):
        try:
            return self.search_medical_records_by_patient_name_use_case.execute(doctor_id=doctor_id, name=name, last_name=last_name)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while searching medical records.")

    def evaluate_risk(self, medical_record_id: int):
        try:
            return self.evaluate_patient_risk_use_case.execute(medical_record_id=medical_record_id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while evaluating the risk.")

    def update_medical_record(self, medical_record_id: int, data: MedicalRecordUpdate):
        try:
            changes = data.model_dump(exclude_unset=True)
            return self.update_medical_record_use_case.execute(medical_record_id=medical_record_id, data=changes)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while updating the medical record: {str(e)}")
