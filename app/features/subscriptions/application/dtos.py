from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from app.core.enums import PlanTypeEnum


@dataclass
class CheckoutSessionResult:
    """Resultado de crear una sesion de Checkout en el gateway de pagos."""
    checkout_url: str
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None


@dataclass
class PaymentEventDTO:
    """Evento de pago normalizado, agnostico del proveedor. El adapter de Stripe
    traduce el webhook crudo a esta forma; el use case solo conoce esto."""
    kind: str  # checkout_completed | payment_succeeded | payment_failed | subscription_canceled | subscription_updated
    user_id: Optional[int] = None
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    plan_type: Optional[str] = None
    current_period_end: Optional[datetime] = None
    stripe_status: Optional[str] = None
    plan_type_from_items: Optional[str] = None
    cancel_at_period_end: Optional[bool] = None


@dataclass
class SubscriptionStatusDTO:
    """Vista de solo lectura del estado de suscripcion para GET /me y login."""
    status: str
    plan_type: Optional[str] = None
    current_period_end: Optional[datetime] = None
