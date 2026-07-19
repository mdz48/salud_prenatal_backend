from typing import Optional
from datetime import timedelta
from salud_prenatal_shared_core.enums import PlanTypeEnum, SubscriptionStatusEnum
from salud_prenatal_shared_core.time import now_cdmx
from app.subscriptions.domain.ports import ISubscriptionRepository, IPaymentGateway, IPaymentTransactionRepository
from app.subscriptions.domain.subscription_entity import SubscriptionEntity
from app.subscriptions.domain.payment_transaction_entity import PaymentTransactionEntity
from app.subscriptions.application.dtos import PaymentEventDTO


class HandlePaymentEventUseCase:
    def __init__(
        self,
        subscription_repository: ISubscriptionRepository,
        payment_gateway: IPaymentGateway,
        transaction_repository: IPaymentTransactionRepository,
    ):
        self.subscription_repository = subscription_repository
        self.payment_gateway = payment_gateway
        self.transaction_repository = transaction_repository

    def execute(self, payload: bytes, signature: str) -> None:
        event = self.payment_gateway.parse_webhook_event(payload, signature)
        if event is None:
            return  # tipo de evento irrelevante

        # Idempotencia: Stripe reintenta webhooks ante timeouts/errores 5xx. Si el
        # evento ya está en el ledger, ya fue aplicado — sin esta guarda, cada
        # reintento de one_time_payment_succeeded sumaba +30 días al periodo.
        if event.stripe_event_id and self.transaction_repository.exists_by_event_id(event.stripe_event_id):
            return

        subscription = self._locate(event)
        if subscription is None:
            return  # no se pudo correlacionar; idempotente, sin crash

        if not self._apply_transition(subscription, event):
            return  # evento no mapeado; no-op

        self.subscription_repository.update(subscription.subscription_id, subscription)

        # El ledger se escribe DESPUÉS de aplicar el cambio: si el proceso muere
        # entre ambos commits, el reintento de Stripe re-aplica (ventana mínima);
        # el orden inverso perdería la activación si el update fallara.
        if event.stripe_event_id:
            self.transaction_repository.create(
                PaymentTransactionEntity(
                    stripe_event_id=event.stripe_event_id,
                    user_id=subscription.user_id,
                    subscription_id=subscription.subscription_id,
                    kind=event.kind,
                    amount_cents=event.amount_cents,
                    currency=event.currency,
                )
            )

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
            
        if event.kind == "one_time_payment_succeeded":
            if event.stripe_customer_id:
                sub.stripe_customer_id = event.stripe_customer_id
            if event.plan_type:
                sub.plan_type = PlanTypeEnum(event.plan_type)
            
            sub.status = SubscriptionStatusEnum.active
            now = now_cdmx()
            # Si sub.current_period_end es naïve (sin zona horaria) y now es aware, dará error.
            # Convertimos ambos a datetime base si es necesario, o aseguramos tzinfo.
            # now_cdmx() devuelve datetime aware. Si DB devuelve naïve, asumimos UTC, 
            # pero el código del proyecto antes no lidiaba con tz en models.
            # Veamos si es mejor usar now_cdmx() y quitar tz, o adaptar.
            # Para evitar bugs de tz-naive vs tz-aware, usamos now.replace(tzinfo=None) si falla.
            # Asumiendo SQLAlchemy guarda timestamp sin tz:
            try:
                base = sub.current_period_end if (sub.current_period_end and sub.current_period_end > now) else now
            except TypeError:
                now_naive = now.replace(tzinfo=None)
                base = sub.current_period_end if (sub.current_period_end and sub.current_period_end > now_naive) else now_naive
                
            sub.current_period_end = base + timedelta(days=30)
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
