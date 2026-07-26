import os
import logging
import firebase_admin
from firebase_admin import credentials, messaging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# Resolve path relative to project root
cred_path = os.path.join(os.getcwd(), "firebasecredencials.json")

# Initialize Firebase App
try:
    if not firebase_admin._apps:
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin SDK initialized successfully.")
        else:
            logger.warning(f"Firebase credentials file not found at {cred_path}. Push notifications will not be sent.")
except Exception as e:
    logger.error(f"Error initializing Firebase Admin SDK: {e}")

class FirebaseNotificationService:
    @staticmethod
    def send_multicast_notification(
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None
    ) -> List[str]:
        """
        Sends push notifications to a list of tokens.
        Returns a list of tokens that failed/expired so they can be cleaned up from DB.
        """
        if not firebase_admin._apps:
            logger.error("Firebase App is not initialized. Cannot send notification.")
            return []

        if not tokens:
            return []

        # FCM multicast message
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            tokens=tokens,
        )

        invalid_tokens = []
        try:
            response = messaging.send_each_for_multicast(message)
            logger.info(f"Successfully sent {response.success_count} notifications out of {len(tokens)}.")
            
            # Identify invalid or expired tokens
            for idx, resp in enumerate(response.responses):
                if not resp.success:
                    logger.warning(f"Failed to send to token {tokens[idx]}: {resp.exception}")
                    invalid_tokens.append(tokens[idx])
        except Exception as e:
            logger.error(f"Error sending multicast notification: {e}")
            
        return invalid_tokens
