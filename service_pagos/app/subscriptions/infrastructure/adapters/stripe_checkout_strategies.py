import os
import stripe
from dotenv import load_dotenv

from typing import Optional
from salud_prenatal_shared_core.enums import PlanTypeEnum
from app.subscriptions.domain.ports import ICheckoutStrategy
from app.subscriptions.application.dtos import CheckoutSessionResult
from app.subscriptions.infrastructure.adapters.stripe_gateway_adapter import _require_env

load_dotenv()


class StripeRecurringCheckoutStrategy(ICheckoutStrategy):
    def _price_id_for(self, plan_type: PlanTypeEnum) -> str:
        if plan_type == PlanTypeEnum.basic:
            return _require_env("STRIPE_PRICE_ID_BASIC")
        if plan_type == PlanTypeEnum.premium:
            return _require_env("STRIPE_PRICE_ID_PREMIUM")
        raise ValueError(f"Unsupported plan type: {plan_type}")

    def create_checkout_session(
        self, user_id: int, email: str, plan_type: PlanTypeEnum, stripe_customer_id: Optional[str] = None
    ) -> CheckoutSessionResult:
        stripe.api_key = _require_env("STRIPE_PRIVATE_KEY")
        frontend_url = _require_env("FRONTEND_URL")
        metadata = {"user_id": str(user_id), "plan_type": plan_type.value}

        kwargs = {
            "mode": "subscription",
            "line_items": [{"price": self._price_id_for(plan_type), "quantity": 1}],
            "client_reference_id": str(user_id),
            "metadata": metadata,
            "subscription_data": {"metadata": metadata},
            "success_url": f"{frontend_url}/subscription/success?session_id={{CHECKOUT_SESSION_ID}}",
            "cancel_url": f"{frontend_url}/subscription/cancel",
        }
        
        if stripe_customer_id:
            kwargs["customer"] = stripe_customer_id
        else:
            kwargs["customer_email"] = email

        session = stripe.checkout.Session.create(**kwargs)

        return CheckoutSessionResult(
            checkout_url=session.url,
            stripe_customer_id=getattr(session, "customer", None),
            stripe_subscription_id=getattr(session, "subscription", None),
        )


class StripeOneTimeCheckoutStrategy(ICheckoutStrategy):
    def _price_id_for_onetime(self, plan_type: PlanTypeEnum) -> str:
        if plan_type == PlanTypeEnum.basic:
            return _require_env("STRIPE_PRICE_ID_BASIC_ONETIME")
        if plan_type == PlanTypeEnum.premium:
            return _require_env("STRIPE_PRICE_ID_PREMIUM_ONETIME")
        raise ValueError(f"Unsupported plan type: {plan_type}")

    def create_checkout_session(
        self, user_id: int, email: str, plan_type: PlanTypeEnum, stripe_customer_id: Optional[str] = None
    ) -> CheckoutSessionResult:
        stripe.api_key = _require_env("STRIPE_PRIVATE_KEY")
        frontend_url = _require_env("FRONTEND_URL")
        metadata = {
            "user_id": str(user_id),
            "plan_type": plan_type.value,
            "payment_mode": "one_time"
        }

        # Para customer_balance (SPEI) Stripe exige que exista un customer explícito
        if not stripe_customer_id:
            customer = stripe.Customer.create(email=email, metadata={"user_id": str(user_id)})
            stripe_customer_id = customer.id

        session = stripe.checkout.Session.create(
            mode="payment",
            payment_method_types=["card", "oxxo", "customer_balance"],
            payment_method_options={
                "customer_balance": {
                    "funding_type": "bank_transfer",
                    "bank_transfer": {
                        "type": "mx_bank_transfer"
                    }
                }
            },
            line_items=[{"price": self._price_id_for_onetime(plan_type), "quantity": 1}],
            customer=stripe_customer_id,
            client_reference_id=str(user_id),
            metadata=metadata,
            success_url=f"{frontend_url}/subscription/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{frontend_url}/subscription/cancel",
        )

        return CheckoutSessionResult(
            checkout_url=session.url,
            stripe_customer_id=getattr(session, "customer", None),
            stripe_subscription_id=getattr(session, "subscription", None),
        )
