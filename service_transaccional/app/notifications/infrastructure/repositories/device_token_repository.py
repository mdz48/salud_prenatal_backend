from typing import List, Optional
from sqlalchemy.orm import Session
from app.notifications.infrastructure.models.device_token_model import DeviceToken

class DeviceTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def register_token(self, user_id: Optional[int], token: str, device_type: Optional[str] = "android") -> DeviceToken:
        # Check if the token already exists
        existing_device = self.db.query(DeviceToken).filter(DeviceToken.token == token).first()

        if existing_device:
            # Reassign token to the new user if it was registered to someone else
            existing_device.user_id = user_id
            existing_device.device_type = device_type
            self.db.commit()
            self.db.refresh(existing_device)
            return existing_device
        
        # If it doesn't exist, create a new record
        new_device = DeviceToken(user_id=user_id, token=token, device_type=device_type)
        self.db.add(new_device)
        self.db.commit()
        self.db.refresh(new_device)
        return new_device

    def unregister_token(self, user_id: int, token: str) -> bool:
        device = self.db.query(DeviceToken).filter(
            DeviceToken.user_id == user_id,
            DeviceToken.token == token
        ).first()

        if device:
            self.db.delete(device)
            self.db.commit()
            return True
        return False

    def get_tokens_by_user_id(self, user_id: int) -> List[str]:
        devices = self.db.query(DeviceToken).filter(DeviceToken.user_id == user_id).all()
        return [d.token for d in devices]

    def get_all_tokens(self) -> List[str]:
        devices = self.db.query(DeviceToken).all()
        return [d.token for d in devices]

    def delete_token(self, token: str) -> None:
        device = self.db.query(DeviceToken).filter(DeviceToken.token == token).first()
        if device:
            self.db.delete(device)
            self.db.commit()
