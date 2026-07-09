import os
from datetime import datetime
from typing import Optional

import stripe
from dotenv import load_dotenv

from app.core.enums import PlanTypeEnum
from app.features.subscriptions.domain.ports import IPaymentGateway, InvalidWebhookError
from app.features.subscriptions.application.dtos import CheckoutSessionResult, PaymentEventDTO

load_dotenv()


def _require_env(name: str) -> str:
    """Lee una variable de entorno obligatoria. Falla ruidoso si falta, en vez de
    llamar a Stripe con credenciales vacias (espejo de get_secret_key())."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


class StripeGatewayAdapter(IPaymentGateway):
    """Transporte hacia Stripe. Toda la config se lee lazy dentro de los metodos:
    conftest importa main sin las claves de Stripe, asi que nada puede leerse a
    nivel de modulo."""

    def _price_id_for(self, plan_type: PlanTypeEnum) -> str:
        if plan_type == PlanTypeEnum.basic:
            return _require_env("STRIPE_PRICE_ID_BASIC")
        if plan_type == PlanTypeEnum.premium:
            return _require_env("STRIPE_PRICE_ID_PREMIUM")
        raise ValueError(f"Unsupported plan type: {plan_type}")

    def create_checkout_session(
        self, user_id: int, email: str, plan_type: PlanTypeEnum
    ) -> CheckoutSessionResult:
        stripe.api_key = _require_env("STRIPE_PRIVATE_KEY")
        frontend_url = _require_env("FRONTEND_URL")
        metadata = {"user_id": str(user_id), "plan_type": plan_type.value}

        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": self._price_id_for(plan_type), "quantity": 1}],
            customer_email=email,
            client_reference_id=str(user_id),
            metadata=metadata,
            subscription_data={"metadata": metadata},
            success_url=f"{frontend_url}/subscription/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{frontend_url}/subscription/cancel",
        )

        return CheckoutSessionResult(
            checkout_url=session.url,
            stripe_customer_id=self._f(session, "customer"),
            stripe_subscription_id=self._f(session, "subscription"),
        )

    def parse_webhook_event(self, payload: bytes, signature: str) -> Optional[PaymentEventDTO]:
        webhook_secret = _require_env("STRIPE_WEBHOOK_SECRET")
        try:
            event = stripe.Webhook.construct_event(payload, signature, webhook_secret)
        except stripe.error.SignatureVerificationError as e:
            raise InvalidWebhookError("Invalid Stripe signature") from e
        except ValueError as e:
            raise InvalidWebhookError("Invalid webhook payload") from e

        event_type = event["type"]
        obj = event["data"]["object"]

        if event_type == "checkout.session.completed":
            meta = self._f(obj, "metadata")
            return PaymentEventDTO(
                kind="checkout_completed",
                user_id=self._user_id_from(self._f(obj, "client_reference_id"), meta),
                stripe_customer_id=self._f(obj, "customer"),
                stripe_subscription_id=self._f(obj, "subscription"),
                plan_type=self._f(meta, "plan_type"),
            )

        if event_type == "invoice.paid":
            return PaymentEventDTO(
                kind="payment_succeeded",
                stripe_customer_id=self._f(obj, "customer"),
                stripe_subscription_id=self._f(obj, "subscription"),
                current_period_end=self._period_end_from_invoice(obj),
            )

        if event_type == "invoice.payment_failed":
            return PaymentEventDTO(
                kind="payment_failed",
                stripe_customer_id=self._f(obj, "customer"),
                stripe_subscription_id=self._f(obj, "subscription"),
            )

        if event_type == "customer.subscription.updated":
            return PaymentEventDTO(
                kind="subscription_updated",
                user_id=self._user_id_from(None, self._f(obj, "metadata")),
                stripe_customer_id=self._f(obj, "customer"),
                stripe_subscription_id=self._f(obj, "id"),
                stripe_status=self._f(obj, "status"),
                current_period_end=self._ts_to_dt(self._f(obj, "current_period_end")),
            )

        if event_type == "customer.subscription.deleted":
            return PaymentEventDTO(
                kind="subscription_canceled",
                stripe_customer_id=self._f(obj, "customer"),
                stripe_subscription_id=self._f(obj, "id"),
            )

        return None  # evento irrelevante

    @staticmethod
    def _f(obj, key, default=None):
        """Acceso seguro a campos de objetos Stripe (StripeObject usa atributos,
        no .get()) y tambien de dicts planos. Devuelve default si falta."""
        return getattr(obj, key, default)

    def _user_id_from(self, client_reference_id, metadata) -> Optional[int]:
        raw = client_reference_id if client_reference_id is not None else self._f(metadata, "user_id")
        try:
            return int(raw) if raw is not None else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _ts_to_dt(ts) -> Optional[datetime]:
        return datetime.fromtimestamp(ts) if ts else None

    def _period_end_from_invoice(self, invoice) -> Optional[datetime]:
        lines = self._f(invoice, "lines")
        data = self._f(lines, "data") or []
        if data:
            period = self._f(data[0], "period")
            return self._ts_to_dt(self._f(period, "end"))
        return None
