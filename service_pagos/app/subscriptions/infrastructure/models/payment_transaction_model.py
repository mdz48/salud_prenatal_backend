from sqlalchemy import Column, Integer, String
from salud_prenatal_shared_core.database import Base, TimestampMixin


class PaymentTransaction(Base, TimestampMixin):
    """Ledger de eventos de pago procesados. Una fila por evento de Stripe
    aplicado — sirve de historial (recibos/auditoría) y de guarda de
    idempotencia contra los reintentos de webhook de Stripe."""

    __tablename__ = "payment_transactions"

    transaction_id = Column(Integer, primary_key=True, autoincrement=True)
    # Clave de idempotencia: id del evento de Stripe (evt_...). UNIQUE para que
    # un reintento jamás pueda registrarse (ni re-aplicarse) dos veces.
    stripe_event_id = Column(String(255), nullable=False, unique=True, index=True)
    # DB compartida: referencia lógica a users.user_id, sin ForeignKey ni relación
    # ORM (misma razón que subscriptions.user_id — ver subscription_model.py).
    user_id = Column(Integer, nullable=True, index=True)
    subscription_id = Column(Integer, nullable=True)
    kind = Column(String(50), nullable=False)
    amount_cents = Column(Integer, nullable=True)
    currency = Column(String(10), nullable=True)
