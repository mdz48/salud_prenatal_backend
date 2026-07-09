from app.features.medical_record.domain.ports import IMedicalRecordRepository, IPatientInfoPort, IRiskPredictionRepository, ILatestDiaryPort

class GetPatientMedicalRecordUseCase:
    def __init__(
        self,
        medical_record_repository: IMedicalRecordRepository,
        patient_repository: IPatientInfoPort,
        risk_prediction_repository: IRiskPredictionRepository,
        latest_diary_repository: ILatestDiaryPort
    ):
        self.medical_record_repository = medical_record_repository
        self.patient_repository = patient_repository
        self.risk_prediction_repository = risk_prediction_repository
        self.latest_diary_repository = latest_diary_repository

    def execute(self, patient_id: int, doctor_id: int) -> dict:
        patient = self.patient_repository.get_patient_info(patient_id)

        # La autorización (paciente existe + pertenece al doctor) la aplica el
        # Protection Proxy (ProtectedMedicalRecordRepository) al pedir el expediente.
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
            stale = bool(
                latest_diary and latest_eval.predicted_at
                and latest_diary.created_at and latest_diary.created_at > latest_eval.predicted_at
            )
            risk_prediction = {
                "status": latest_eval.status,
                "prediction": latest_eval.prediction,
                "missing_fields": latest_eval.missing_fields,
                "predicted_at": latest_eval.predicted_at,
                "model_version": latest_eval.ml_model_version,
                "stale": stale,
            }

        return {
            "user_id": patient.user_id,
            "name": patient.name,
            "last_name": patient.last_name,
            "current_gestational_weeks": medical_record.current_gestational_weeks,
            "age": patient.age,
            "medical_record": medical_record,
            "consultations": consultations_list,
            "risk_prediction": risk_prediction
        }
