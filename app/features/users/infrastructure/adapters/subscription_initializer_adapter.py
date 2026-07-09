from typing import Optional
from app.core.enums import SubscriptionStatusEnum
from app.features.users.domain.ports import ISubscriptionInitializer, ISubscriptionStatusLookup
from app.features.subscriptions.domain.subscription_entity import SubscriptionEntity
from app.features.subscriptions.infrastructure.repositories.subscription_repository import SubscriptionRepository


class SubscriptionInitializerAdapter(ISubscriptionInitializer, ISubscriptionStatusLookup):
    """Puente del feature users hacia subscriptions. Envuelve el repositorio de
    subscriptions para crear la fila pendiente al registrar un doctor y para leer
    el estado durante el login, sin que users conozca el ORM/repos ajenos."""

    def __init__(self, subscription_repository: SubscriptionRepository):
        self.subscription_repository = subscription_repository

    def create_pending(self, user_id: int) -> None:
        existing = self.subscription_repository.get_by_user_id(user_id)
        if existing is None:
            self.subscription_repository.create(
                SubscriptionEntity(user_id=user_id, status=SubscriptionStatusEnum.pending)
            )

    def get_status(self, user_id: int) -> Optional[str]:
        subscription = self.subscription_repository.get_by_user_id(user_id)
        return subscription.status.value if subscription else None
