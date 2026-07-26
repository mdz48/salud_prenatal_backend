from typing import Protocol, Optional
from salud_prenatal_shared_core.enums import PlanTypeEnum
from app.subscriptions.domain.subscription_entity import SubscriptionEntity
from app.subscriptions.application.dtos import CheckoutSessionResult, PaymentEventDTO
from app.subscriptions.domain.payment_transaction_entity import PaymentTransactionEntity


class ISubscriptionRepository(Protocol):
    def create(self, sub: SubscriptionEntity) -> SubscriptionEntity: ...
    def get_by_user_id(self, user_id: int) -> Optional[SubscriptionEntity]: ...
    def get_by_stripe_subscription_id(self, stripe_subscription_id: str) -> Optional[SubscriptionEntity]: ...
    def update(self, subscription_id: int, sub: SubscriptionEntity) -> Optional[SubscriptionEntity]: ...


class InvalidWebhookError(Exception):
    """Firma de webhook invalida o payload no verificable."""

class ICheckoutStrategy(Protocol):
    def create_checkout_session(
        self, user_id: int, email: str, plan_type: PlanTypeEnum, stripe_customer_id: Optional[str] = None
    ) -> CheckoutSessionResult: ...


class IPaymentGateway(Protocol):
    def create_portal_session(self, stripe_customer_id: str) -> str: ...

    def parse_webhook_event(
        self, payload: bytes, signature: str
    ) -> Optional[PaymentEventDTO]:
        """Verifica la firma y normaliza el evento. Lanza InvalidWebhookError si la
        firma es invalida; devuelve None para tipos de evento irrelevantes."""
        ...


class IPaymentTransactionRepository(Protocol):
    """Ledger de eventos de pago: idempotencia de webhooks + historial por usuario."""

    def exists_by_event_id(self, stripe_event_id: str) -> bool: ...
    def create(self, tx: PaymentTransactionEntity) -> PaymentTransactionEntity: ...
    def list_by_user_id(self, user_id: int) -> list[PaymentTransactionEntity]: ...
