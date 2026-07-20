from salud_prenatal_shared_core.database import Base
from salud_prenatal_shared_core.time import now_cdmx
from sqlalchemy import Column, Integer, ForeignKey, Float, Text, DateTime
from sqlalchemy.orm import relationship

class PatientDiary(Base):
    __tablename__ = "patient_diaries"

    patient_diary_id = Column(Integer, primary_key=True, autoincrement=True)
    medical_record_id = Column(Integer, ForeignKey("medical_records.medical_record_id"), nullable=False, index=True)
    weight_kg = Column(Float, nullable=True)
    systolic = Column(Integer, nullable=True)
    diastolic = Column(Integer, nullable=True)
    symptoms = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=now_cdmx)
    updated_at = Column(DateTime(timezone=True), default=now_cdmx, onupdate=now_cdmx)

    # Relationships
    medical_record = relationship("MedicalRecord", back_populates="patient_diaries")

    @property
    def weight_gain(self) -> float | None:
        if self.weight_kg and self.medical_record and self.medical_record.initial_weight:
            return round(self.weight_kg - self.medical_record.initial_weight, 2)
        return None