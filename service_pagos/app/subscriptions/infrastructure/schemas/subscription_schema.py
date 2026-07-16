from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from salud_prenatal_shared_core.enums import PlanTypeEnum, PaymentModeEnum

class CheckoutSessionRequest(BaseModel):
    plan_type: PlanTypeEnum
    payment_mode: PaymentModeEnum = PaymentModeEnum.recurring


class CheckoutSessionResponse(BaseModel):
    checkout_url: str


class PortalSessionResponse(BaseModel):
    portal_url: str


class SubscriptionResponse(BaseModel):
    status: str
    plan_type: Optional[str] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool = False
    auto_renewal: bool = False
