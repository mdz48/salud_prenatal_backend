from typing import Optional
from app.chat.domain.ports import IChatRepository
from app.chat.domain.chat_message_entity import ChatMessage
from app.core.events.domain_event import MessageSentEvent
from app.core.events.event_dispatcher import IEventDispatcher


class SaveMessageUseCase:
    def __init__(self, chat_repository: IChatRepository, event_dispatcher: Optional[IEventDispatcher] = None):
        self.chat_repository = chat_repository
        self.event_dispatcher = event_dispatcher

    def execute(self, sender_id: int, receiver_id: int, content: str) -> ChatMessage:
        saved_msg = self.chat_repository.save_message(sender_id, receiver_id, content)

        if self.event_dispatcher and saved_msg.message_id:
            self.event_dispatcher.publish(
                MessageSentEvent(
                    message_id=saved_msg.message_id,
                    sender_id=saved_msg.sender_id,
                    receiver_id=saved_msg.receiver_id,
                    content=saved_msg.content,
                )
            )

        return saved_msg
