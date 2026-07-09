"""Patrón Strategy (ADR-14): análisis de síntomas de la bitácora.

El campo `symptoms` es texto libre. `SymptomAnalyzer` (contexto) delega el análisis
en una estrategia intercambiable (`ISymptomAnalysisStrategy`). Hoy hay una
estrategia basada en palabras clave y una nula; en el futuro se puede añadir una
estrategia de NLP real sin tocar a los consumidores.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from app.core.text import normalize_text


@dataclass
class SymptomAnalysis:
    severity: str  # "none" | "info" | "warning" | "danger"
    flags: List[str]


class ISymptomAnalysisStrategy(ABC):
    @abstractmethod
    def analyze(self, symptoms: Optional[str]) -> SymptomAnalysis:
        ...


class NoopSymptomStrategy(ISymptomAnalysisStrategy):
    def analyze(self, symptoms: Optional[str]) -> SymptomAnalysis:
        return SymptomAnalysis(severity="none", flags=[])


class KeywordSymptomStrategy(ISymptomAnalysisStrategy):
    """Estrategia por reglas: marca síntomas de alarma obstétrica por palabra clave."""

    DANGER_KEYWORDS = (
        "sangrado",
        "vision borrosa",
        "dolor de cabeza intenso",
        "convulsion",
        "hinchazon",
        "dolor abdominal severo",
        "no siento al bebe",
    )
    WARNING_KEYWORDS = (
        "nauseas",
        "mareo",
        "dolor de cabeza",
        "vomito",
    )

    def analyze(self, symptoms: Optional[str]) -> SymptomAnalysis:
        if not symptoms or not symptoms.strip():
            return SymptomAnalysis(severity="none", flags=[])

        text = normalize_text(symptoms)

        danger = [kw for kw in self.DANGER_KEYWORDS if normalize_text(kw) in text]
        if danger:
            return SymptomAnalysis(severity="danger", flags=danger)

        warning = [kw for kw in self.WARNING_KEYWORDS if normalize_text(kw) in text]
        if warning:
            return SymptomAnalysis(severity="warning", flags=warning)

        return SymptomAnalysis(severity="info", flags=[])


class SymptomAnalyzer:
    def __init__(self, strategy: ISymptomAnalysisStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: ISymptomAnalysisStrategy) -> None:
        self._strategy = strategy

    def analyze(self, symptoms: Optional[str]) -> SymptomAnalysis:
        return self._strategy.analyze(symptoms)
