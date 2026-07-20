from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, Boolean, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.enums import BloodTypeEnum
from app.core.database import Base
from app.core.pregnancy_calculations import gestational_weeks
from app.core.security import EncryptedString

class MedicalRecord(Base):
    __tablename__ = "medical_records"
    __table_args__ = (UniqueConstraint("patient_id", "doctor_id", name="uq_medical_record_patient_doctor"),)

    medical_record_id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"), nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.doctor_id"), nullable=False, index=True)

    # Clinical profile (del expediente, capturado por el doctor)
    blood_type = Column(Enum(BloodTypeEnum), nullable=True) # Tipo de sangre
    weeks_at_registration = Column(Integer, nullable=True) # Semana de gestación al registrarse
    last_menstrual_period = Column(Date, nullable=True) # Fecha del ultimo periodo menstrual
    residence = Column(EncryptedString, nullable=True) # Residencia
    education_level = Column(EncryptedString, nullable=True) # Nivel educativo
    marital_status = Column(EncryptedString, nullable=True) # Estado civil
    height_cm = Column(Integer, nullable=True) # Altura en centimetros
    initial_weight = Column(Float, nullable=True) # Peso inicial en kilogramos
    initial_systolic = Column(Integer, nullable=True) # Presion sistolica de la primera visita
    initial_diastolic = Column(Integer, nullable=True) # Presion diastolica de la primera visita

    # Medical history
    previous_hypertension = Column(Boolean, nullable=True) # Hipertensión previa
    diabetes = Column(Boolean, nullable=True) # Diabetes
    family_history_hypertension = Column(Boolean, nullable=True) # Antecedentes familiares de hipertensión

    # Obstetric history
    previous_pregnancies = Column(Integer, nullable=True) # Embarazos previos
    previous_deliveries = Column(Integer, nullable=True) # Partos previos
    previous_miscarriages = Column(Integer, nullable=True) # Abortos previos
    previous_cesareans = Column(Integer, nullable=True) # Cesáreas previas
    previous_preeclampsia = Column(Boolean, nullable=True) # Preeclampsia previa

    # Chronic / pathological history
    chronic_kidney_disease = Column(Boolean, nullable=True) # Enfermedad renal cronica
    chronic_hypertension = Column(Boolean, nullable=True) # Hipertensión crónica
    multiple_pregnancy = Column(Boolean, nullable=True) # Embarazo múltiple
    fetal_death = Column(Boolean, nullable=True) # Muerte fetal
    fetal_growth_restriction = Column(Boolean, nullable=True) # Restricción del crecimiento fetal

    # Family history
    family_history_heart_disease = Column(Boolean, nullable=True) # Antecedentes familiares de enfermedades cardíacas

    # Lifestyle
    active_smoking = Column(Boolean, nullable=True) # Tabaquismo activo

    # Relationships
    patient = relationship("Patient", back_populates="medical_records")
    doctor = relationship("Doctor")
    consultations = relationship("Consultation", back_populates="medical_record")
    patient_diaries = relationship("PatientDiary", back_populates="medical_record")

    @property
    def current_gestational_weeks(self) -> int | None:
        return gestational_weeks(self.last_menstrual_period, self.weeks_at_registration)