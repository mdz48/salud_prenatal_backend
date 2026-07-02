from typing import Protocol, Optional, List
from .entities import PatientDiaryEntity

class IPatientDiaryRepository(Protocol):
    def get_all(self, skip: int = 0, limit: int = 100) -> List[PatientDiaryEntity]:
        ...
    
    def get_by_id(self, patient_diary_id: int) -> Optional[PatientDiaryEntity]:
        ...
        
    def get_by_medical_record_id(self, medical_record_id: int) -> List[PatientDiaryEntity]:
        ...
        
    def create(self, diary_data: PatientDiaryEntity) -> PatientDiaryEntity:
        ...
        
    def update(self, patient_diary_id: int, update_data: PatientDiaryEntity) -> Optional[PatientDiaryEntity]:
        ...
        
    def delete(self, patient_diary_id: int) -> bool:
        ...
