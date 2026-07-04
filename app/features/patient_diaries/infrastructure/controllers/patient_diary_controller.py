from fastapi import HTTPException, status
from app.features.patient_diaries.infrastructure.schemas.patient_diary_schema import PatientDiaryCreate, PatientDiaryUpdate
from app.features.patient_diaries.application.create_patient_diary_usecase import CreatePatientDiaryUseCase
from app.features.patient_diaries.application.get_all_patient_diaries_usecase import GetAllPatientDiariesUseCase
from app.features.patient_diaries.application.get_patient_diary_by_id_usecase import GetPatientDiaryByIdUseCase
from app.features.patient_diaries.application.get_diaries_by_medical_record_usecase import GetDiariesByMedicalRecordUseCase
from app.features.patient_diaries.application.update_patient_diary_usecase import UpdatePatientDiaryUseCase
from app.features.patient_diaries.application.delete_patient_diary_usecase import DeletePatientDiaryUseCase
from app.features.patient_diaries.domain.patient_diary_entity import PatientDiaryEntity

class PatientDiaryController:
    def __init__(
        self,
        create_patient_diary_use_case: CreatePatientDiaryUseCase,
        get_all_patient_diaries_use_case: GetAllPatientDiariesUseCase,
        get_diaries_by_medical_record_use_case: GetDiariesByMedicalRecordUseCase,
        get_patient_diary_by_id_use_case: GetPatientDiaryByIdUseCase,
        update_patient_diary_use_case: UpdatePatientDiaryUseCase,
        delete_patient_diary_use_case: DeletePatientDiaryUseCase
    ):
        self.create_patient_diary_use_case = create_patient_diary_use_case
        self.get_all_patient_diaries_use_case = get_all_patient_diaries_use_case
        self.get_diaries_by_medical_record_use_case = get_diaries_by_medical_record_use_case
        self.get_patient_diary_by_id_use_case = get_patient_diary_by_id_use_case
        self.update_patient_diary_use_case = update_patient_diary_use_case
        self.delete_patient_diary_use_case = delete_patient_diary_use_case

    def create_patient_diary(self, data: PatientDiaryCreate):
        try:
            entity = PatientDiaryEntity(**data.model_dump())
            return self.create_patient_diary_use_case.execute(data=entity)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def get_all_patient_diaries(self, skip: int = 0, limit: int = 100):
        return self.get_all_patient_diaries_use_case.execute(skip=skip, limit=limit)

    def get_diaries_by_medical_record(self, medical_record_id: int):
        return self.get_diaries_by_medical_record_use_case.execute(medical_record_id=medical_record_id)

    def get_patient_diary(self, patient_diary_id: int):
        try:
            return self.get_patient_diary_by_id_use_case.execute(patient_diary_id=patient_diary_id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    def update_patient_diary(self, patient_diary_id: int, data: PatientDiaryUpdate):
        try:
            entity = PatientDiaryEntity(**data.model_dump(exclude_unset=True))
            return self.update_patient_diary_use_case.execute(patient_diary_id=patient_diary_id, data=entity)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def delete_patient_diary(self, patient_diary_id: int):
        try:
            self.delete_patient_diary_use_case.execute(patient_diary_id=patient_diary_id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
