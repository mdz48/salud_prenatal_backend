"""Analiza el texto de síntomas usando la estrategia configurada (ADR-14)."""
from typing import Optional

from app.features.patient_diaries.domain.symptom_analysis import (
    SymptomAnalysis,
    SymptomAnalyzer,
)


class AnalyzeSymptomsUseCase:
    def __init__(self, analyzer: SymptomAnalyzer):
        self.analyzer = analyzer

    def execute(self, symptoms: Optional[str]) -> SymptomAnalysis:
        return self.analyzer.analyze(symptoms)
