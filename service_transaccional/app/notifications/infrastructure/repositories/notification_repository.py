from typing import List, Optional
from sqlalchemy.orm import Session
from app.notifications.domain.ports import INotificationRepository
from app.notifications.domain.notification_entity import NotificationEntity
from app.notifications.infrastructure.models.notification_model import NotificationModel


class NotificationRepository(INotificationRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, notification: NotificationEntity) -> NotificationEntity:
        db_obj = NotificationModel(
            user_id=notification.user_id,
            title=notification.title,
            body=notification.body,
            type=notification.type,
            is_read=notification.is_read,
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return NotificationEntity.model_validate(db_obj)

    def get_by_user_id(self, user_id: int, limit: int = 50) -> List[NotificationEntity]:
        records = (
            self.db.query(NotificationModel)
            .filter(NotificationModel.user_id == user_id)
            .order_by(NotificationModel.created_at.desc())
            .limit(limit)
            .all()
        )
        return [NotificationEntity.model_validate(r) for r in records]

    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        record = (
            self.db.query(NotificationModel)
            .filter(NotificationModel.id == notification_id, NotificationModel.user_id == user_id)
            .first()
        )
        if not record:
            return False
        record.is_read = True
        self.db.commit()
        return True
