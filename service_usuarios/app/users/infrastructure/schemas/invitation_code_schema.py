from pydantic import BaseModel
from datetime import datetime

class InvitationCodeResponse(BaseModel):
    code: str
    expires_at: datetime

class RedeemCodeRequest(BaseModel):
    code: str
