"""Read-model de solo lectura sobre la tabla `medical_records` (owned por el
servicio transaccional). El servicio usuarios lo usa para resolver el expediente
y las semanas de gestación en los dashboards / listado de pacientes.
"""
from sqlalchemy import Column, Integer, Date
from salud_prenatal_shared_core.database import Base
from salud_prenatal_shared_core.pregnancy_calculations import gestational_weeks


class MedicalRecordRead(Base):
    __tablename__ = "medical_records"
    __table_args__ = {"extend_existing": True}

    medical_record_id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, index=True)
    doctor_id = Column(Integer, index=True)
    # Necesarias para calcular las semanas de gestación (misma lógica que el modelo real).
    last_menstrual_period = Column(Date, nullable=True)
    weeks_at_registration = Column(Integer, nullable=True)

    @property
    def current_gestational_weeks(self):
        return gestational_weeks(self.last_menstrual_period, self.weeks_at_registration)
