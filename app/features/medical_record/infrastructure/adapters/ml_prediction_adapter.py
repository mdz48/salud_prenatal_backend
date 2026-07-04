import os
import requests
from dotenv import load_dotenv
from app.features.medical_record.domain.ports import IMLPredictionService

load_dotenv()

class MlPredictionServiceAdapter(IMLPredictionService):
    def build_payload(self, patient, medical_record, latest_diary: object) -> dict:
        bmi_initial = 0.0
        if patient.initial_weight and patient.height_cm:
            bmi_initial = patient.initial_weight / ((patient.height_cm / 100.0) ** 2)

        gestational_week = patient.current_gestational_weeks or 0
        gestational_trimester = gestational_week // 13

        mean_arterial_pressure = 0.0
        if latest_diary and latest_diary.systolic and latest_diary.diastolic:
            mean_arterial_pressure = (latest_diary.systolic + 2 * latest_diary.diastolic) / 3

        nulliparous = 1 if not medical_record.previous_deliveries else 0

        ed_lvl = (patient.education_level or "superior").lower()
        if ed_lvl not in ["primaria", "secundaria", "superior"]:
            ed_lvl = "superior"

        res = (patient.residence or "urbana").lower()
        if res not in ["rural", "urbana"]:
            res = "urbana"

        ms = (patient.marital_status or "married").lower()
        if ms not in ["single", "married"]:
            ms = "married"

        return {
            "age_years": patient.age or 0,
            "bmi_initial": round(bmi_initial, 2),
            "gestational_week": gestational_week,
            "gestational_trimester": gestational_trimester,
            "height_cm": float(patient.height_cm) if patient.height_cm else 0.0,
            "initial_weight": float(patient.initial_weight) if patient.initial_weight else 0.0,
            "weight_kg": float(latest_diary.weight_kg) if latest_diary and latest_diary.weight_kg else float(patient.initial_weight or 0.0),
            "weight_gain": float(latest_diary.weight_gain) if latest_diary and latest_diary.weight_gain else 0.0,
            "systolic": float(latest_diary.systolic) if latest_diary and latest_diary.systolic else 0.0,
            "diastolic": float(latest_diary.diastolic) if latest_diary and latest_diary.diastolic else 0.0,
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

    def predict(self, patient, medical_record, latest_diary) -> dict | None:
        ml_service_url = os.getenv("ML_SERVICE_URL")
        if not ml_service_url:
            return None

        payload = self.build_payload(patient, medical_record, latest_diary)
        try:
            response = requests.post(f"{ml_service_url}/predict", json=payload, timeout=2.0)
            if response.status_code == 200:
                return response.json()
            print("ML Service returned non-200:", response.status_code, response.text)
        except Exception as e:
            print("ML Service Exception:", str(e))

        return None
