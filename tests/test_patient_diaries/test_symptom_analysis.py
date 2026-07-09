"""ADR-14 Strategy: análisis de síntomas con estrategia intercambiable."""
from app.features.patient_diaries.application.analyze_symptoms_usecase import AnalyzeSymptomsUseCase
from app.features.patient_diaries.domain.symptom_analysis import (
    KeywordSymptomStrategy,
    NoopSymptomStrategy,
    SymptomAnalyzer,
)


def test_keyword_strategy_flags_danger():
    result = KeywordSymptomStrategy().analyze("Tengo sangrado y mareo")
    assert result.severity == "danger"
    assert "sangrado" in result.flags


def test_keyword_strategy_flags_warning():
    result = KeywordSymptomStrategy().analyze("solo un poco de mareo")
    assert result.severity == "warning"


def test_keyword_strategy_handles_accents_and_case():
    # "visión borrosa" con acento y mayúsculas debe seguir detectándose
    result = KeywordSymptomStrategy().analyze("VISIÓN BORROSA por la mañana")
    assert result.severity == "danger"


def test_empty_symptoms_is_none():
    assert KeywordSymptomStrategy().analyze(None).severity == "none"
    assert KeywordSymptomStrategy().analyze("   ").severity == "none"


def test_analyzer_strategy_is_swappable():
    analyzer = SymptomAnalyzer(KeywordSymptomStrategy())
    assert analyzer.analyze("sangrado").severity == "danger"
    analyzer.set_strategy(NoopSymptomStrategy())
    assert analyzer.analyze("sangrado").severity == "none"


def test_analyze_symptoms_usecase():
    usecase = AnalyzeSymptomsUseCase(SymptomAnalyzer(KeywordSymptomStrategy()))
    assert usecase.execute("dolor de cabeza intenso").severity == "danger"
