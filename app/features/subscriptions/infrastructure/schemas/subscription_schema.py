from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.core.enums import PlanTypeEnum


class CheckoutSessionRequest(BaseModel):
    plan_type: PlanTypeEnum


class CheckoutSessionResponse(BaseModel):
    checkout_url: str


class SubscriptionResponse(BaseModel):
    status: str
    plan_type: Optional[str] = None
    current_period_end: Optional[datetime] = None
