from app.notifications.domain.ports import INotificationRepository


class MarkNotificationReadUseCase:
    def __init__(self, notification_repository: INotificationRepository):
        self.notification_repository = notification_repository

    def execute(self, notification_id: int, user_id: int) -> bool:
        return self.notification_repository.mark_as_read(notification_id=notification_id, user_id=user_id)
