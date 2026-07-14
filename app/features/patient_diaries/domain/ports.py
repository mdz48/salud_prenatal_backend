from datetime import datetime
from typing import List, Optional, Dict
from typing import Protocol, Optional, List
from .patient_diary_entity import PatientDiaryEntity
from .extracted_symptom_entity import ExtractedSymptomEntity
from .body_zone_entity import BodyZoneEntity
from .symptom_extraction_result_entity import SymptomExtractionResult


class ISymptomExtractionPort(Protocol):
    """Puerto hacia el servicio NLP externo (adaptado por HTTP al microservicio ML,
    patron Gateway - ADR-06/14). Devuelve SymptomExtractionResult() vacio si el
    servicio esta caido: la extraccion es best-effort y nunca debe bloquear el
    guardado de la bitacora."""

    def extract(self, text: str) -> SymptomExtractionResult:
        ...


class IDiarySymptomRepository(Protocol):
    def replace_for_diary(self, patient_diary_id: int, medical_record_id: Optional[int],
                          result: SymptomExtractionResult) -> List[ExtractedSymptomEntity]:
        ...

    def get_by_diary_id(self, patient_diary_id: int) -> List[ExtractedSymptomEntity]:
        ...

    def get_by_medical_record_id(self, medical_record_id: int, since: Optional[datetime] = None) -> List[ExtractedSymptomEntity]:
        ...

    def get_body_zones_by_diary_id(self, patient_diary_id: int) -> List[BodyZoneEntity]:
        ...


class IPatientDiaryRepository(Protocol):
    def get_all(self, skip: int = 0, limit: int = 100) -> List[PatientDiaryEntity]:
        ...
    
    def get_by_id(self, patient_diary_id: int) -> Optional[PatientDiaryEntity]:
        ...
        
    def get_by_medical_record_id(self, medical_record_id: int) -> List[PatientDiaryEntity]:
        ...

    def get_latest_by_medical_record_id(self, medical_record_id: int) -> Optional[PatientDiaryEntity]:
        ...

    def create(self, diary_data: PatientDiaryEntity) -> PatientDiaryEntity:
        ...
        
    def update(self, patient_diary_id: int, update_data: PatientDiaryEntity) -> Optional[PatientDiaryEntity]:
        ...
        
    def delete(self, patient_diary_id: int) -> bool:
        ...
