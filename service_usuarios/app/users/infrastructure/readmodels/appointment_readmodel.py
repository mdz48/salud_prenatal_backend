"""Read-model de solo lectura sobre la tabla `appointments` (owned por el servicio
transaccional). El servicio usuarios la lee para armar los dashboards, sin declarar
FK ni relaciones ORM: en la DB compartida basta con mapear las columnas necesarias.
"""
from sqlalchemy import Column, Integer, String, DateTime, Enum as SAEnum
from salud_prenatal_shared_core.database import ReadModelBase as Base
from salud_prenatal_shared_core.enums import AppointmentStatusEnum


class AppointmentRead(Base):
    __tablename__ = "appointments"
    # Solo lectura: no gestionamos su ciclo de vida. extend_existing por si otro
    # modelo del mismo proceso ya la declarara.
    __table_args__ = {"extend_existing": True}

    appointment_id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, index=True)
    doctor_id = Column(Integer, index=True)
    appointment_date = Column(DateTime)
    status = Column(SAEnum(AppointmentStatusEnum))
    reason = Column(String(255))
