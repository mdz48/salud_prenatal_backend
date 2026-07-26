from fastapi import APIRouter, Depends, Request, status
from container import Container
from salud_prenatal_shared_core.auth_dependencies import RoleChecker, Principal
from salud_prenatal_shared_core.db_cleanup import close_db_after
from salud_prenatal_shared_core.enums import RoleEnum
from app.subscriptions.infrastructure.schemas.subscription_schema import (
    CheckoutSessionRequest,
    CheckoutSessionResponse,
    PortalSessionResponse,
    SubscriptionResponse,
    PaymentTransactionResponse,
)
from app.subscriptions.infrastructure.controllers.subscription_controller import SubscriptionController
from container import Container

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])

require_doctor = RoleChecker([RoleEnum.doctor])


@router.post("/checkout-session", response_model=CheckoutSessionResponse, status_code=status.HTTP_201_CREATED)
@close_db_after(Container)
def create_checkout_session(
    data: CheckoutSessionRequest,
    current_user: Principal = Depends(require_doctor),
):
    controller = Container.subscription_controller()
    return controller.create_checkout_session(
        user_id=current_user.user_id, email=current_user.email, req=data
    )


@router.post("/portal-session", response_model=PortalSessionResponse, status_code=status.HTTP_201_CREATED)
@close_db_after(Container)
def create_portal_session(
    current_user: Principal = Depends(require_doctor),
):
    controller = Container.subscription_controller()
    return controller.create_portal_session(user_id=current_user.user_id)


@router.get("/me", response_model=SubscriptionResponse, status_code=status.HTTP_200_OK)
@close_db_after(Container)
def get_my_subscription(
    current_user: Principal = Depends(require_doctor),
):
    controller = Container.subscription_controller()
    return controller.get_my_subscription(user_id=current_user.user_id)


@router.get("/payments", response_model=list[PaymentTransactionResponse], status_code=status.HTTP_200_OK)
@close_db_after(Container)
def get_my_payments(
    current_user: Principal = Depends(require_doctor),
):
    """Historial de pagos del doctor autenticado (ledger de webhooks aplicados)."""
    controller = Container.subscription_controller()
    return controller.get_my_payments(user_id=current_user.user_id)


@router.post("/webhook", status_code=status.HTTP_200_OK)
@close_db_after(Container)
async def stripe_webhook(
    request: Request,
):
    # La firma de Stripe se calcula sobre los bytes crudos exactos: nunca parsear
    # el body con pydantic aqui.
    controller = Container.subscription_controller()
    payload = await request.body()
    signature = request.headers.get("stripe-signature")
    return controller.handle_webhook(payload, signature)
