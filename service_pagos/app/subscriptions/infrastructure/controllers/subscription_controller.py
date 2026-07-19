from fastapi import HTTPException, status
from salud_prenatal_shared_core.enums import PlanTypeEnum
from app.subscriptions.domain.ports import InvalidWebhookError
from app.subscriptions.infrastructure.schemas.subscription_schema import (
    CheckoutSessionRequest,
    CheckoutSessionResponse,
    PortalSessionResponse,
    SubscriptionResponse,
    PaymentTransactionResponse,
)


class SubscriptionController:
    def __init__(
        self,
        create_checkout_session_use_case,
        get_my_subscription_use_case,
        handle_payment_event_use_case,
        create_portal_session_use_case,
        get_my_payments_use_case,
    ):
        self.create_checkout_session_use_case = create_checkout_session_use_case
        self.get_my_subscription_use_case = get_my_subscription_use_case
        self.handle_payment_event_use_case = handle_payment_event_use_case
        self.create_portal_session_use_case = create_portal_session_use_case
        self.get_my_payments_use_case = get_my_payments_use_case

    def create_checkout_session(self, user_id: int, email: str, req: CheckoutSessionRequest) -> CheckoutSessionResponse:
        try:
            url = self.create_checkout_session_use_case.execute(
                user_id=user_id, email=email, plan_type=req.plan_type, payment_mode=req.payment_mode
            )
            return CheckoutSessionResponse(checkout_url=url)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            print(f"Error creating checkout session: {repr(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating the checkout session.",
            )

    def create_portal_session(self, user_id: int) -> PortalSessionResponse:
        try:
            url = self.create_portal_session_use_case.execute(user_id=user_id)
            return PortalSessionResponse(portal_url=url)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            print(f"Error creating portal session: {repr(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating the portal session.",
            )

    def get_my_subscription(self, user_id: int) -> SubscriptionResponse:
        dto = self.get_my_subscription_use_case.execute(user_id=user_id)
        return SubscriptionResponse(
            status=dto.status,
            plan_type=dto.plan_type,
            current_period_end=dto.current_period_end,
            cancel_at_period_end=dto.cancel_at_period_end,
            auto_renewal=dto.auto_renewal,
        )

    def get_my_payments(self, user_id: int) -> list[PaymentTransactionResponse]:
        txs = self.get_my_payments_use_case.execute(user_id=user_id)
        return [
            PaymentTransactionResponse(
                kind=t.kind,
                amount_cents=t.amount_cents,
                currency=t.currency,
                created_at=t.created_at,
            )
            for t in txs
        ]

    def handle_webhook(self, payload: bytes, signature: str) -> dict:
        try:
            self.handle_payment_event_use_case.execute(payload, signature)
            return {"received": True}
        except InvalidWebhookError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            print(f"Error handling webhook: {repr(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while handling the webhook.",
            )
