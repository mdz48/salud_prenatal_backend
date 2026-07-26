from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class PatientDirectoryQuery:
    doctor_id: int
    patient_ids_filter: Optional[List[int]] = None
    linked_after: Optional[datetime] = None
    linked_before: Optional[datetime] = None
