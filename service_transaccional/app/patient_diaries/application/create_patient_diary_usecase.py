from typing import Optional

from app.patient_diaries.domain.ports import (
    IPatientDiaryRepository,
    ISymptomExtractionPort,
    IDiarySymptomRepository,
)
from app.patient_diaries.domain.patient_diary_entity import PatientDiaryEntity


class CreatePatientDiaryUseCase:
    def __init__(
        self,
        repository: IPatientDiaryRepository,
        symptom_extraction_port: Optional[ISymptomExtractionPort] = None,
        symptom_repository: Optional[IDiarySymptomRepository] = None,
    ):
        self.repository = repository
        # Dependencias NLP opcionales: si no se inyectan, la creacion de bitacora
        # funciona igual (degradacion limpia, tests unitarios sin NLP).
        self.symptom_extraction_port = symptom_extraction_port
        self.symptom_repository = symptom_repository

    def execute(self, data: PatientDiaryEntity) -> PatientDiaryEntity:
        created = self.repository.create(data)
        self._extract_symptoms(created)
        return created

    def _extract_symptoms(self, diary: PatientDiaryEntity) -> None:
        """Extraccion NLP de sintomas del texto libre (RF-29/31). Best-effort:
        cualquier fallo del NLP se traga y NUNCA rompe el guardado de la bitacora.

        Sincrono por simplicidad; RT-F2 (worker asincrono) puede moverlo a un
        BackgroundTask mas adelante sin tocar esta interfaz."""
        if not (self.symptom_extraction_port and self.symptom_repository):
            return
        if not diary.patient_diary_id:
            return

        text = " ".join(t for t in (diary.symptoms, diary.notes) if t).strip()
        if not text:
            return

        try:
            result = self.symptom_extraction_port.extract(text)
            if result.symptoms or result.body_zones:
                self.symptom_repository.replace_for_diary(
                    diary.patient_diary_id, diary.medical_record_id, result
                )
        except Exception as e:
            print("Symptom extraction skipped:", str(e))
