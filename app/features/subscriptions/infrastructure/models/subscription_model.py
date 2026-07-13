from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.core.database import Base, TimestampMixin
from app.core.enums import PlanTypeEnum, SubscriptionStatusEnum


class Subscription(Base, TimestampMixin):
    __tablename__ = "subscriptions"

    subscription_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True, nullable=False, index=True)
    plan_type = Column(SAEnum(PlanTypeEnum), nullable=True)
    status = Column(
        SAEnum(SubscriptionStatusEnum),
        nullable=False,
        default=SubscriptionStatusEnum.pending,
    )
    stripe_customer_id = Column(String(255), nullable=True, index=True)
    stripe_subscription_id = Column(String(255), nullable=True, unique=True, index=True)
    current_period_end = Column(DateTime, nullable=True)
    cancel_at_period_end = Column(Boolean, nullable=False, default=False)

    user = relationship("Usuario")