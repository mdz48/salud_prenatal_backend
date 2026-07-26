from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class UnlinkRequestEntity(BaseModel):
    unlink_request_id: Optional[int] = None
    patient_id: int
    doctor_id: int
    status: str = "pending"
    reason: Optional[str] = None
    created_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    # Se rellena solo en los listados (join con el usuario de la paciente);
    # en create/get_by_id/update queda None. Evita que el doctor tenga que
    # hacer otra llamada para saber de quien es la solicitud.
    patient_full_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
