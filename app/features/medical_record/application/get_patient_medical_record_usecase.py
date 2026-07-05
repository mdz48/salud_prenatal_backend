from app.features.medical_record.domain.ports import IMedicalRecordRepository, IPatientInfoPort, IMLPredictionService

class GetPatientMedicalRecordUseCase:
    def __init__(
        self,
        medical_record_repository: IMedicalRecordRepository,
        patient_repository: IPatientInfoPort,
        ml_prediction_service: IMLPredictionService
    ):
        self.medical_record_repository = medical_record_repository
        self.patient_repository = patient_repository
        self.ml_prediction_service = ml_prediction_service

    def execute(self, patient_id: int, doctor_id: int) -> dict:
        patient = self.patient_repository.get_patient_info(patient_id)
        if not patient:
            raise ValueError("Patient not found")

        medical_record = self.medical_record_repository.get_by_patient_and_doctor(patient_id, doctor_id)

        consultations_list = []
        if medical_record and medical_record.consultations:
            for consultation in medical_record.consultations:
                consultations_list.append({
                    "consultation_id": consultation.consultation_id,
                    "created_at": consultation.created_at
                })

        risk_prediction = None
        if medical_record:
            latest_diary = None
            if medical_record.patient_diaries:
                latest_diary = sorted(medical_record.patient_diaries, key=lambda d: d.created_at, reverse=True)[0]
            risk_prediction = self.ml_prediction_service.predict(patient, medical_record, latest_diary)

        return {
            "user_id": patient.user_id,
            "name": patient.name,
            "last_name": patient.last_name,
            "current_gestational_weeks": patient.current_gestational_weeks,
            "age": patient.age,
            "medical_record": medical_record,
            "consultations": consultations_list,
            "risk_prediction": risk_prediction
        }
