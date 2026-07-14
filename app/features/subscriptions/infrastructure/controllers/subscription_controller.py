from fastapi import HTTPException, status
from app.core.enums import PlanTypeEnum
from app.features.subscriptions.domain.ports import InvalidWebhookError
from app.features.subscriptions.infrastructure.schemas.subscription_schema import (
    CheckoutSessionResponse,
    SubscriptionResponse,
)


class SubscriptionController:
    def __init__(
        self,
        create_checkout_session_use_case,
        get_my_subscription_use_case,
        handle_payment_event_use_case,
    ):
        self.create_checkout_session_use_case = create_checkout_session_use_case
        self.get_my_subscription_use_case = get_my_subscription_use_case
        self.handle_payment_event_use_case = handle_payment_event_use_case

    def create_checkout_session(self, user_id: int, email: str, plan_type: PlanTypeEnum) -> CheckoutSessionResponse:
        try:
            url = self.create_checkout_session_use_case.execute(
                user_id=user_id, email=email, plan_type=plan_type
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

    def get_my_subscription(self, user_id: int) -> SubscriptionResponse:
        dto = self.get_my_subscription_use_case.execute(user_id=user_id)
        return SubscriptionResponse(
            status=dto.status,
            plan_type=dto.plan_type,
            current_period_end=dto.current_period_end,
        )

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
