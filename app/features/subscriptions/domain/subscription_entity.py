from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from app.core.enums import PlanTypeEnum, SubscriptionStatusEnum


class SubscriptionEntity(BaseModel):
    subscription_id: Optional[int] = None
    user_id: int
    plan_type: Optional[PlanTypeEnum] = None
    status: SubscriptionStatusEnum = SubscriptionStatusEnum.pending
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)