from sqlalchemy.orm import Session
from app.subscriptions.infrastructure.models.payment_transaction_model import PaymentTransaction
from app.subscriptions.domain.ports import IPaymentTransactionRepository
from app.subscriptions.domain.payment_transaction_entity import PaymentTransactionEntity


class PaymentTransactionRepository(IPaymentTransactionRepository):
    def __init__(self, db: Session):
        self.db = db

    def exists_by_event_id(self, stripe_event_id: str) -> bool:
        return (
            self.db.query(PaymentTransaction)
            .filter(PaymentTransaction.stripe_event_id == stripe_event_id)
            .first()
            is not None
        )

    def create(self, tx: PaymentTransactionEntity) -> PaymentTransactionEntity:
        data = tx.model_dump(exclude={"transaction_id", "created_at", "updated_at"})
        db_tx = PaymentTransaction(**data)
        self.db.add(db_tx)
        self.db.commit()
        self.db.refresh(db_tx)
        return PaymentTransactionEntity.model_validate(db_tx)

    def list_by_user_id(self, user_id: int) -> list[PaymentTransactionEntity]:
        # transaction_id como desempate: created_at tiene resolución de segundos
        # y dos eventos pueden caer en el mismo instante.
        rows = (
            self.db.query(PaymentTransaction)
            .filter(PaymentTransaction.user_id == user_id)
            .order_by(PaymentTransaction.created_at.desc(), PaymentTransaction.transaction_id.desc())
            .all()
        )
        return [PaymentTransactionEntity.model_validate(r) for r in rows]
