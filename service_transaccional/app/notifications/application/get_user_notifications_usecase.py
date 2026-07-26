from typing import List
from app.notifications.domain.ports import INotificationRepository
from app.notifications.domain.notification_entity import NotificationEntity


class GetUserNotificationsUseCase:
    def __init__(self, notification_repository: INotificationRepository):
        self.notification_repository = notification_repository

    def execute(self, user_id: int, limit: int = 50) -> List[NotificationEntity]:
        return self.notification_repository.get_by_user_id(user_id=user_id, limit=limit)
