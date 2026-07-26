from app.subscriptions.domain.ports import IPaymentTransactionRepository
from app.subscriptions.domain.payment_transaction_entity import PaymentTransactionEntity


class GetMyPaymentsUseCase:
    def __init__(self, transaction_repository: IPaymentTransactionRepository):
        self.transaction_repository = transaction_repository

    def execute(self, user_id: int) -> list[PaymentTransactionEntity]:
        return self.transaction_repository.list_by_user_id(user_id)
