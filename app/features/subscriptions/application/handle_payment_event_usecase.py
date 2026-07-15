from typing import Optional
from app.core.enums import PlanTypeEnum, SubscriptionStatusEnum
from app.features.subscriptions.domain.ports import ISubscriptionRepository, IPaymentGateway
from app.features.subscriptions.domain.subscription_entity import SubscriptionEntity
from app.features.subscriptions.application.dtos import PaymentEventDTO


class HandlePaymentEventUseCase:
    def __init__(self, subscription_repository: ISubscriptionRepository, payment_gateway: IPaymentGateway):
        self.subscription_repository = subscription_repository
        self.payment_gateway = payment_gateway

    def execute(self, payload: bytes, signature: str) -> None:
        event = self.payment_gateway.parse_webhook_event(payload, signature)
        if event is None:
            return  # tipo de evento irrelevante

        subscription = self._locate(event)
        if subscription is None:
            return  # no se pudo correlacionar; idempotente, sin crash

        if not self._apply_transition(subscription, event):
            return  # evento no mapeado; no-op

        self.subscription_repository.update(subscription.subscription_id, subscription)

    def _locate(self, event: PaymentEventDTO) -> Optional[SubscriptionEntity]:
        if event.stripe_subscription_id:
            found = self.subscription_repository.get_by_stripe_subscription_id(event.stripe_subscription_id)
            if found:
                return found
        if event.user_id is not None:
            return self.subscription_repository.get_by_user_id(event.user_id)
        return None

    def _apply_transition(self, sub: SubscriptionEntity, event: PaymentEventDTO) -> bool:
        """Muta `sub` segun el evento. Devuelve False si el evento no aplica cambios."""
        if event.kind == "checkout_completed":
            if event.stripe_customer_id:
                sub.stripe_customer_id = event.stripe_customer_id
            if event.stripe_subscription_id:
                sub.stripe_subscription_id = event.stripe_subscription_id
            if event.plan_type:
                sub.plan_type = PlanTypeEnum(event.plan_type)
            sub.status = SubscriptionStatusEnum.active
            return True

        if event.kind == "payment_succeeded":
            sub.status = SubscriptionStatusEnum.active
            if event.current_period_end:
                sub.current_period_end = event.current_period_end
            return True

        if event.kind == "payment_failed":
            sub.status = SubscriptionStatusEnum.past_due
            return True

        if event.kind == "subscription_canceled":
            sub.status = SubscriptionStatusEnum.canceled
            sub.cancel_at_period_end = False
            return True

        if event.kind == "subscription_updated":
            if event.stripe_status:
                sub.status = self._map_stripe_status(event.stripe_status)
            if event.current_period_end:
                sub.current_period_end = event.current_period_end
            if event.plan_type_from_items:
                sub.plan_type = PlanTypeEnum(event.plan_type_from_items)
            if event.cancel_at_period_end is not None:
                sub.cancel_at_period_end = event.cancel_at_period_end
            return True

        return False  # evento desconocido

    @staticmethod
    def _map_stripe_status(stripe_status: str) -> SubscriptionStatusEnum:
        mapping = {
            "active": SubscriptionStatusEnum.active,
            "trialing": SubscriptionStatusEnum.active,
            "past_due": SubscriptionStatusEnum.past_due,
            "unpaid": SubscriptionStatusEnum.past_due,
            "canceled": SubscriptionStatusEnum.canceled,
        }
        return mapping.get(stripe_status, SubscriptionStatusEnum.past_due)
