from app.medical_record.domain.ports import IMedicalRecordRepository, IPatientInfoPort, IRiskPredictionRepository, ILatestDiaryPort, IDiarySymptomSummaryPort

class GetPatientMedicalRecordUseCase:
    def __init__(
        self,
        medical_record_repository: IMedicalRecordRepository,
        patient_repository: IPatientInfoPort,
        risk_prediction_repository: IRiskPredictionRepository,
        latest_diary_repository: ILatestDiaryPort,
        symptom_summary_port: IDiarySymptomSummaryPort,
    ):
        self.medical_record_repository = medical_record_repository
        self.patient_repository = patient_repository
        self.risk_prediction_repository = risk_prediction_repository
        self.latest_diary_repository = latest_diary_repository
        self.symptom_summary_port = symptom_summary_port

    def execute(self, patient_id: int, doctor_id: int) -> dict:
        patient = self.patient_repository.get_patient_info(patient_id)
        if not patient:
            raise ValueError("Patient not found")

        if patient.doctor_id != doctor_id:
            raise ValueError("El paciente no tiene una relación con este doctor")

        medical_record = self.medical_record_repository.get_by_patient_and_doctor(patient_id, doctor_id)
        if not medical_record:
            raise ValueError("El doctor aún no ha creado el expediente clínico para este paciente")

        consultations_list = []
        if medical_record.consultations:
            for consultation in medical_record.consultations:
                consultations_list.append({
                    "consultation_id": consultation.consultation_id,
                    "created_at": consultation.created_at
                })

        # Lectura pura: la evaluacion de riesgo se persiste con el boton del doctor
        # (EvaluatePatientRiskUseCase); aqui solo se lee la ultima, sin llamar al ML.
        risk_prediction = None
        latest_diary = self.latest_diary_repository.get_latest_diary_for_medical_record(medical_record.medical_record_id)

        latest_eval = self.risk_prediction_repository.get_latest_for_medical_record(medical_record.medical_record_id)
        if latest_eval:
            # stale: hay bitacoras nuevas desde la ultima evaluacion
            d_time = latest_diary.created_at.replace(tzinfo=None) if (latest_diary and latest_diary.created_at and latest_diary.created_at.tzinfo) else (latest_diary.created_at if latest_diary else None)
            e_time = latest_eval.predicted_at.replace(tzinfo=None) if (latest_eval and latest_eval.predicted_at and latest_eval.predicted_at.tzinfo) else (latest_eval.predicted_at if latest_eval else None)
            stale = bool(d_time and e_time and d_time > e_time)
            risk_prediction = {
                "status": latest_eval.status,
                "prediction": latest_eval.prediction,
                "missing_fields": latest_eval.missing_fields,
                "predicted_at": latest_eval.predicted_at,
                "model_version": latest_eval.ml_model_version,
                "stale": stale,
            }

        # Aviso de sintomas: solo lo registrado despues de la ultima consulta
        # (el doctor ya atendio lo anterior). Sin consultas, marca de agua nula.
        watermark = None
        if medical_record.consultations:
            fechas = [c.created_at for c in medical_record.consultations if c.created_at]
            watermark = max(fechas) if fechas else None
        symptom_alert = self.symptom_summary_port.get_symptom_summary(
            medical_record.medical_record_id, since=watermark
        )

        return {
            "user_id": patient.user_id,
            "name": patient.name,
            "last_name": patient.last_name,
            "current_gestational_weeks": medical_record.current_gestational_weeks,
            "age": patient.age,
            "medical_record": medical_record,
            "consultations": consultations_list,
            "risk_prediction": risk_prediction,
            "symptom_alert": symptom_alert
        }
