from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class MedicalRecord(Base):
    __tablename__ = "medical_records"

    medical_record_id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"), unique=True, nullable=False)

    # Medical history
    previous_hypertension = Column(Boolean, nullable=True) # Hipertensión previa
    diabetes = Column(Boolean, nullable=True) # Diabetes
    family_history_hypertension = Column(Boolean, nullable=True) # Antecedentes familiares de hipertensión

    # Obstetric history
    previous_pregnancies = Column(Boolean, nullable=True) # Embarazos previos
    previous_deliveries = Column(Boolean, nullable=True) # Partos previos
    previous_miscarriages = Column(Boolean, nullable=True) # Abortos previos
    previous_cesareans = Column(Boolean, nullable=True) # Cesáreas previas
    previous_preeclampsia = Column(Boolean, nullable=True) # Preeclampsia previa

    # Chronic / pathological history
    chronic_kidney_disease = Column(Boolean, nullable=True) # Enfermedad renal cronica
    chronic_hypertension = Column(Boolean, nullable=True) # Hipertensión crónica
    multiple_pregnancy = Column(Boolean, nullable=True) # Embarazo múltiple
    fetal_death = Column(Boolean, nullable=True) # Muerte fetal
    fetal_growth_restriction = Column(Boolean, nullable=True) # Restricción del crecimiento fetal

    # Family history
    family_history_heart_disease = Column(Boolean, nullable=True) # Antecedentes familiares de enfermedades cardíacas

    # Relationships
    patient = relationship("Patient", back_populates="medical_record")