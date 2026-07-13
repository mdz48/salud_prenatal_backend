from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Request, status
from app.core.containers import Container
from app.core.dependencies import RoleChecker, get_current_user
from app.core.enums import RoleEnum
from app.features.users.domain.user_entity import UserEntity
from app.features.subscriptions.infrastructure.schemas.subscription_schema import (
    CheckoutSessionRequest,
    CheckoutSessionResponse,
    PortalSessionResponse,
    SubscriptionResponse,
)
from app.features.subscriptions.infrastructure.controllers.subscription_controller import SubscriptionController

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])

require_doctor = RoleChecker([RoleEnum.doctor])


@router.post("/checkout-session", response_model=CheckoutSessionResponse, status_code=status.HTTP_201_CREATED)
@inject
def create_checkout_session(
    data: CheckoutSessionRequest,
    current_user: UserEntity = Depends(require_doctor),
    controller: SubscriptionController = Depends(Provide[Container.subscription_controller]),
):
    return controller.create_checkout_session(
        user_id=current_user.user_id, email=current_user.email, plan_type=data.plan_type
    )


@router.post("/portal-session", response_model=PortalSessionResponse, status_code=status.HTTP_201_CREATED)
@inject
def create_portal_session(
    current_user: UserEntity = Depends(require_doctor),
    controller: SubscriptionController = Depends(Provide[Container.subscription_controller]),
):
    return controller.create_portal_session(user_id=current_user.user_id)


@router.get("/me", response_model=SubscriptionResponse, status_code=status.HTTP_200_OK)
@inject
def get_my_subscription(
    current_user: UserEntity = Depends(require_doctor),
    controller: SubscriptionController = Depends(Provide[Container.subscription_controller]),
):
    return controller.get_my_subscription(user_id=current_user.user_id)


@router.post("/webhook", status_code=status.HTTP_200_OK)
@inject
async def stripe_webhook(
    request: Request,
    controller: SubscriptionController = Depends(Provide[Container.subscription_controller]),
):
    # La firma de Stripe se calcula sobre los bytes crudos exactos: nunca parsear
    # el body con pydantic aqui.
    payload = await request.body()
    signature = request.headers.get("stripe-signature")
    return controller.handle_webhook(payload, signature)
