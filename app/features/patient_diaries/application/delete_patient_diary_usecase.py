from app.features.patient_diaries.domain.ports import IPatientDiaryRepository

class DeletePatientDiaryUseCase:
    def __init__(self, repository: IPatientDiaryRepository):
        self.repository = repository
        
    def execute(self, patient_diary_id: int) -> bool:
        success = self.repository.delete(patient_diary_id)
        if not success:
            raise ValueError("Patient diary not found") 
        return success
