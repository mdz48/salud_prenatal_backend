"""Composition root del servicio pagos — solo el slice de subscriptions."""
from dependency_injector import containers, providers

from salud_prenatal_shared_core.database import get_session_factory

from app.subscriptions.infrastructure.repositories.subscription_repository import SubscriptionRepository
from app.subscriptions.infrastructure.adapters.stripe_gateway_adapter import StripeGatewayAdapter
from app.subscriptions.infrastructure.adapters.stripe_checkout_strategies import StripeRecurringCheckoutStrategy, StripeOneTimeCheckoutStrategy
from app.subscriptions.application.create_checkout_session_usecase import CreateCheckoutSessionUseCase
from app.subscriptions.application.get_my_subscription_usecase import GetMySubscriptionUseCase
from app.subscriptions.application.handle_payment_event_usecase import HandlePaymentEventUseCase
from app.subscriptions.application.create_portal_session_usecase import CreatePortalSessionUseCase
from salud_prenatal_shared_core.enums import PaymentModeEnum
from app.subscriptions.infrastructure.controllers.subscription_controller import SubscriptionController


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "main",
            "app.subscriptions.infrastructure.routes.subscription_router",
        ]
    )

    db = providers.ContextLocalSingleton(lambda: get_session_factory()())

    subscription_repository = providers.Factory(SubscriptionRepository, db=db)
    stripe_payment_gateway = providers.Factory(StripeGatewayAdapter)
    
    stripe_recurring_strategy = providers.Factory(StripeRecurringCheckoutStrategy)
    stripe_onetime_strategy = providers.Factory(StripeOneTimeCheckoutStrategy)

    create_checkout_session_use_case = providers.Factory(
        CreateCheckoutSessionUseCase,
        subscription_repository=subscription_repository,
        checkout_strategies=providers.Dict({
            PaymentModeEnum.recurring: stripe_recurring_strategy,
            PaymentModeEnum.one_time: stripe_onetime_strategy,
        })
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
