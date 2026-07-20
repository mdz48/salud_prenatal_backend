from typing import Optional
from fastapi import BackgroundTasks
from salud_prenatal_shared_core.database import get_session_factory

from app.patient_diaries.domain.ports import (
    IPatientDiaryRepository,
    ISymptomExtractionPort,
    IDiarySymptomRepository,
)
from app.patient_diaries.domain.patient_diary_entity import PatientDiaryEntity
from app.patient_diaries.infrastructure.repositories.diary_symptom_extraction_repository import DiarySymptomExtractionRepository


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

    def execute(
        self,
        data: PatientDiaryEntity,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> PatientDiaryEntity:
        created = self.repository.create(data)
        if background_tasks:
            background_tasks.add_task(self._extract_symptoms_bg, created)
        else:
            self._extract_symptoms(created)
        return created

    def _extract_symptoms_bg(self, diary: PatientDiaryEntity) -> None:
        """Tarea asincrona en segundo plano para extraccion NLP de sintomas con LLM.
        Abre su propia sesion de DB para ser hilo-segura tras el cierre de la sesion HTTP."""
        if not self.symptom_extraction_port:
            return
        if not diary.patient_diary_id:
            return

        text = " ".join(t for t in (diary.symptoms, diary.notes) if t).strip()
        if not text:
            return

        db = get_session_factory()()
        try:
            repo = DiarySymptomExtractionRepository(db=db)
            result = self.symptom_extraction_port.extract(text)
            if result.symptoms or result.body_zones:
                repo.replace_for_diary(
                    diary.patient_diary_id, diary.medical_record_id, result
                )
        except Exception as e:
            print("Background symptom extraction skipped:", str(e))
        finally:
            db.close()

    def _extract_symptoms(self, diary: PatientDiaryEntity) -> None:
        """Extraccion NLP sincrona de fallback."""
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
