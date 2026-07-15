from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum as SAEnum
from salud_prenatal_shared_core.database import Base, TimestampMixin
from salud_prenatal_shared_core.enums import PlanTypeEnum, SubscriptionStatusEnum


class Subscription(Base, TimestampMixin):
    __tablename__ = "subscriptions"

    subscription_id = Column(Integer, primary_key=True, autoincrement=True)
    # DB compartida: user_id referencia logicamente a users.user_id (owned por el
    # servicio usuarios). El servicio pagos NO declara el ForeignKey ni la relacion
    # ORM hacia Usuario, para poder crear su tabla de forma independiente sin que la
    # tabla users tenga que existir en SU metadata. La integridad referencial de
    # user_id la garantiza el servicio usuarios.
    user_id = Column(Integer, unique=True, nullable=False, index=True)
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
