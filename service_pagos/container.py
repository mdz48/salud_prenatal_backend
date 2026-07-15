"""Composition root del servicio pagos — solo el slice de subscriptions."""
from dependency_injector import containers, providers

from salud_prenatal_shared_core.database import get_db

from app.subscriptions.infrastructure.repositories.subscription_repository import SubscriptionRepository
from app.subscriptions.infrastructure.adapters.stripe_gateway_adapter import StripeGatewayAdapter
from app.subscriptions.application.create_checkout_session_usecase import CreateCheckoutSessionUseCase
from app.subscriptions.application.get_my_subscription_usecase import GetMySubscriptionUseCase
from app.subscriptions.application.handle_payment_event_usecase import HandlePaymentEventUseCase
from app.subscriptions.application.create_portal_session_usecase import CreatePortalSessionUseCase
from app.subscriptions.infrastructure.controllers.subscription_controller import SubscriptionController


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "main",
            "app.subscriptions.infrastructure.routes.subscription_router",
        ]
    )

    db = providers.Resource(get_db)

    subscription_repository = providers.Factory(SubscriptionRepository, db=db)
    stripe_payment_gateway = providers.Factory(StripeGatewayAdapter)

    create_checkout_session_use_case = providers.Factory(
        CreateCheckoutSessionUseCase,
        subscription_repository=subscription_repository,
        payment_gateway=stripe_payment_gateway,
    )
    get_my_subscription_use_case = providers.Factory(
        GetMySubscriptionUseCase, subscription_repository=subscription_repository
    )
    handle_payment_event_use_case = providers.Factory(
        HandlePaymentEventUseCase,
        subscription_repository=subscription_repository,
        payment_gateway=stripe_payment_gateway,
    )
    create_portal_session_use_case = providers.Factory(
        CreatePortalSessionUseCase,
        subscription_repository=subscription_repository,
        payment_gateway=stripe_payment_gateway,
    )

    subscription_controller = providers.Factory(
        SubscriptionController,
        create_checkout_session_use_case,
        get_my_subscription_use_case,
        handle_payment_event_use_case,
        create_portal_session_use_case,
    )
