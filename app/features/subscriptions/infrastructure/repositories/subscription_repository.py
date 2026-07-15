from typing import Optional
from sqlalchemy.orm import Session
from app.features.subscriptions.infrastructure.models.subscription_model import Subscription
from app.features.subscriptions.domain.ports import ISubscriptionRepository
from app.features.subscriptions.domain.subscription_entity import SubscriptionEntity


class SubscriptionRepository(ISubscriptionRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, sub: SubscriptionEntity) -> SubscriptionEntity:
        data = sub.model_dump(exclude={"subscription_id", "created_at", "updated_at"}, exclude_unset=True)
        db_sub = Subscription(**data)
        self.db.add(db_sub)
        self.db.commit()
        self.db.refresh(db_sub)
        return SubscriptionEntity.model_validate(db_sub)

    def get_by_user_id(self, user_id: int) -> Optional[SubscriptionEntity]:
        db_sub = self.db.query(Subscription).filter(Subscription.user_id == user_id).first()
        return SubscriptionEntity.model_validate(db_sub) if db_sub else None

    def get_by_stripe_subscription_id(self, stripe_subscription_id: str) -> Optional[SubscriptionEntity]:
        db_sub = (
            self.db.query(Subscription)
            .filter(Subscription.stripe_subscription_id == stripe_subscription_id)
            .first()
        )
        return SubscriptionEntity.model_validate(db_sub) if db_sub else None

    def update(self, subscription_id: int, sub: SubscriptionEntity) -> Optional[SubscriptionEntity]:
        db_sub = self.db.query(Subscription).filter(Subscription.subscription_id == subscription_id).first()
        if not db_sub:
            return None

        update_data = sub.model_dump(exclude={"subscription_id", "user_id", "created_at", "updated_at"})
        for key, value in update_data.items():
            setattr(db_sub, key, value)

        self.db.commit()
        self.db.refresh(db_sub)
        return SubscriptionEntity.model_validate(db_sub)
