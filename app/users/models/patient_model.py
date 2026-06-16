from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from app.models.enums import BloodTypeEnum
from app.core.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True, nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=True)
    birthdate = Column(Date, nullable=False)
    blood_type = Column(Enum(BloodTypeEnum), nullable=True)
    weeks_at_registration = Column(Integer, nullable=True)
    last_menstrual_period = Column(Date, nullable=True)

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
    user = relationship("Usuario", back_populates="patient_profile")
    doctor = relationship("Doctor", back_populates="patients")