from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class ReportEntity(BaseModel):
    report_id: Optional[int] = None
    reporter_id: int
    post_id: Optional[int] = None
    comment_id: Optional[int] = None
    reason: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
