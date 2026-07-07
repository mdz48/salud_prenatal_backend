"""Feature engineering para el modelo de riesgo de preeclampsia.

Funciones puras (sin I/O): construyen el payload que consume el microservicio ML
y evaluan si hay datos suficientes para una inferencia con sentido clinico.
El adapter de infraestructura solo transporta; el conocimiento clinico vive aqui.
"""
from typing import Optional


def effective_pressure(medical_record, latest_diary) -> tuple[Optional[int], Optional[int]]:
    """Presion efectiva: la de la bitacora si existe, si no la basal del expediente.

    Mismo patron que el peso. Unica fuente de verdad del fallback: la usan
    build_ml_payload y assess_completeness.
    """
    systolic = latest_diary.systolic if (latest_diary and latest_diary.systolic) else medical_record.initial_systolic
    diastolic = latest_diary.diastolic if (latest_diary and latest_diary.diastolic) else medical_record.initial_diastolic
    return systolic, diastolic


def assess_completeness(patient, medical_record, latest_diary) -> list[str]:
    """Campos criticos faltantes para la inferencia. Lista vacia = suficiente.

    Sin estos datos el modelo recibiria ceros que interpreta como outliers,
    no como faltantes (subestima el riesgo hipertensivo).
    """
    missing = []
    if patient.age is None:
        missing.append("age")
    if not medical_record.height_cm:
        missing.append("height_cm")
    if not medical_record.initial_weight:
        missing.append("initial_weight")
    systolic, diastolic = effective_pressure(medical_record, latest_diary)
    if not systolic:
        missing.append("systolic")
    if not diastolic:
        missing.append("diastolic")
    return missing


def build_ml_payload(patient, medical_record, latest_diary) -> dict:
    # Lo clinico vive en el expediente; de `patient` solo se usa la edad (deriva de birthdate).
    bmi_initial = 0.0
    if medical_record.initial_weight and medical_record.height_cm:
        bmi_initial = medical_record.initial_weight / ((medical_record.height_cm / 100.0) ** 2)

    gestational_week = medical_record.current_gestational_weeks or 0
    gestational_trimester = gestational_week // 13

    systolic, diastolic = effective_pressure(medical_record, latest_diary)

    mean_arterial_pressure = 0.0
    if systolic and diastolic:
        mean_arterial_pressure = (systolic + 2 * diastolic) / 3

    nulliparous = 1 if not medical_record.previous_deliveries else 0

    ed_lvl = (medical_record.education_level or "superior").lower()
    if ed_lvl not in ["primaria", "secundaria", "superior"]:
        ed_lvl = "superior"

    res = (medical_record.residence or "urbana").lower()
    if res not in ["rural", "urbana"]:
        res = "urbana"

    ms = (medical_record.marital_status or "married").lower()
    if ms not in ["single", "married"]:
        ms = "married"

    return {
        "age_years": patient.age or 0,
        "bmi_initial": round(bmi_initial, 2),
        "gestational_week": gestational_week,
        "gestational_trimester": gestational_trimester,
        "height_cm": float(medical_record.height_cm) if medical_record.height_cm else 0.0,
        "initial_weight": float(medical_record.initial_weight) if medical_record.initial_weight else 0.0,
        "weight_kg": float(latest_diary.weight_kg) if latest_diary and latest_diary.weight_kg else float(medical_record.initial_weight or 0.0),
        "weight_gain": float(latest_diary.weight_gain) if latest_diary and latest_diary.weight_gain else 0.0,
        "systolic": float(systolic) if systolic else 0.0,
        "diastolic": float(diastolic) if diastolic else 0.0,
        "mean_arterial_pressure": round(mean_arterial_pressure, 2),
        "diabetes": 1 if medical_record.diabetes else 0,
        "chronic_hypertension": 1 if medical_record.chronic_hypertension else 0,
        "previous_preeclampsia": 1 if medical_record.previous_preeclampsia else 0,
        "family_history_hypertension": 1 if medical_record.family_history_hypertension else 0,
        "family_history_heart_disease": 1 if medical_record.family_history_heart_disease else 0,
        "chronic_kidney_disease": 1 if medical_record.chronic_kidney_disease else 0,
        "multiple_pregnancy": 1 if medical_record.multiple_pregnancy else 0,
        "active_smoking": 1 if medical_record.active_smoking else 0,
        "previous_pregnancies": int(medical_record.previous_pregnancies or 0),
        "previous_deliveries": int(medical_record.previous_deliveries or 0),
        "previous_miscarriages": int(medical_record.previous_miscarriages or 0),
        "previous_cesareans": int(medical_record.previous_cesareans or 0),
        "nulliparous": nulliparous,
        "education_level": ed_lvl,
        "residence": res,
        "marital_status": ms,
    }
