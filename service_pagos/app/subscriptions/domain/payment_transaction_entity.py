from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class PaymentTransactionEntity(BaseModel):
    transaction_id: Optional[int] = None
    stripe_event_id: str
    user_id: Optional[int] = None
    subscription_id: Optional[int] = None
    kind: str
    amount_cents: Optional[int] = None
    currency: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
