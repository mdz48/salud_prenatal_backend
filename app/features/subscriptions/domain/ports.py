from typing import Protocol, Optional
from app.core.enums import PlanTypeEnum
from app.features.subscriptions.domain.subscription_entity import SubscriptionEntity
from app.features.subscriptions.application.dtos import CheckoutSessionResult, PaymentEventDTO


class ISubscriptionRepository(Protocol):
    def create(self, sub: SubscriptionEntity) -> SubscriptionEntity: ...
    def get_by_user_id(self, user_id: int) -> Optional[SubscriptionEntity]: ...
    def get_by_stripe_subscription_id(self, stripe_subscription_id: str) -> Optional[SubscriptionEntity]: ...
    def update(self, subscription_id: int, sub: SubscriptionEntity) -> Optional[SubscriptionEntity]: ...


class InvalidWebhookError(Exception):
    """Firma de webhook invalida o payload no verificable."""


class IPaymentGateway(Protocol):
    def create_portal_session(self, stripe_customer_id: str) -> str: ...

    def create_checkout_session(
        self, user_id: int, email: str, plan_type: PlanTypeEnum
    ) -> CheckoutSessionResult: ...

    def parse_webhook_event(
        self, payload: bytes, signature: str
    ) -> Optional[PaymentEventDTO]:
        """Verifica la firma y normaliza el evento. Lanza InvalidWebhookError si la
        firma es invalida; devuelve None para tipos de evento irrelevantes."""
        ...
