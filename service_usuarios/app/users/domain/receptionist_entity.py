from pydantic import BaseModel, ConfigDict
from typing import Optional

class ReceptionistEntity(BaseModel):
    receptionist_id: Optional[int] = None
    user_id: int
    doctor_id: int

    model_config = ConfigDict(from_attributes=True)
