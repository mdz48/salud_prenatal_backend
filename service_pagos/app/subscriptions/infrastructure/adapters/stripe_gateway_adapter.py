import os
from datetime import datetime
from typing import Optional

import stripe
from dotenv import load_dotenv

from salud_prenatal_shared_core.enums import PlanTypeEnum
from app.subscriptions.domain.ports import IPaymentGateway, InvalidWebhookError
from app.subscriptions.application.dtos import CheckoutSessionResult, PaymentEventDTO

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

    def create_portal_session(self, stripe_customer_id: str) -> str:
        stripe.api_key = _require_env("STRIPE_PRIVATE_KEY")
        frontend_url = _require_env("FRONTEND_URL")
        session = stripe.billing_portal.Session.create(
            customer=stripe_customer_id,
            return_url=f"{frontend_url}/subscription/me",
        )
        return session.url

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

        dto = self._parse_event(event_type, obj)
        if dto is not None:
            # Sello común a todo evento relevante: id (idempotencia) y monto si aplica.
            dto.stripe_event_id = self._f(event, "id")
            dto.amount_cents, dto.currency = self._amount_from(event_type, obj)
        return dto

    def _parse_event(self, event_type, obj) -> Optional[PaymentEventDTO]:
        if event_type == "checkout.session.completed":
            meta = self._f(obj, "metadata")
            mode = self._f(obj, "mode")
            payment_status = self._f(obj, "payment_status")
            
            if mode == "subscription":
                return PaymentEventDTO(
                    kind="checkout_completed",
                    user_id=self._user_id_from(self._f(obj, "client_reference_id"), meta),
                    stripe_customer_id=self._f(obj, "customer"),
                    stripe_subscription_id=self._f(obj, "subscription"),
                    plan_type=self._f(meta, "plan_type"),
                )
            elif mode == "payment" and payment_status == "paid":
                return PaymentEventDTO(
                    kind="one_time_payment_succeeded",
                    user_id=self._user_id_from(self._f(obj, "client_reference_id"), meta),
                    stripe_customer_id=self._f(obj, "customer"),
                    stripe_subscription_id=None,
                    plan_type=self._f(meta, "plan_type"),
                )
            # Si mode == "payment" y no es "paid" (ej. voucher pendiente), ignoramos.
            return None

        if event_type == "checkout.session.async_payment_succeeded":
            meta = self._f(obj, "metadata")
            return PaymentEventDTO(
                kind="one_time_payment_succeeded",
                user_id=self._user_id_from(self._f(obj, "client_reference_id"), meta),
                stripe_customer_id=self._f(obj, "customer"),
                stripe_subscription_id=None,
                plan_type=self._f(meta, "plan_type"),
            )
            
        if event_type == "checkout.session.async_payment_failed":
            return None

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
                plan_type_from_items=self._plan_type_from_price_id(self._current_price_id(obj)),
                cancel_at_period_end=self._f(obj, "cancel_at_period_end"),
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

    def _amount_from(self, event_type, obj):
        """Monto del evento en centavos, si el tipo lo trae. Checkout usa
        amount_total; invoices usan amount_paid. El resto no trae monto."""
        if event_type.startswith("checkout.session."):
            return self._f(obj, "amount_total"), self._f(obj, "currency")
        if event_type.startswith("invoice."):
            return self._f(obj, "amount_paid"), self._f(obj, "currency")
        return None, None

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

    def _current_price_id(self, subscription_obj) -> Optional[str]:
        items = self._f(subscription_obj, "items")
        data = self._f(items, "data") or []
        if not data:
            return None
        price = self._f(data[0], "price")
        return self._f(price, "id")

    @staticmethod
    def _plan_type_from_price_id(price_id: Optional[str]) -> Optional[str]:
        if price_id is None:
            return None
        if price_id == os.getenv("STRIPE_PRICE_ID_BASIC"):
            return PlanTypeEnum.basic.value
        if price_id == os.getenv("STRIPE_PRICE_ID_PREMIUM"):
            return PlanTypeEnum.premium.value
        return None
