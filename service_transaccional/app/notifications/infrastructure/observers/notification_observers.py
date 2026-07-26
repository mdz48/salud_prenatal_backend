import logging
from typing import Optional
from salud_prenatal_shared_core.database import get_session_factory
from salud_prenatal_shared_core.events import (
    AppointmentCreatedEvent,
    MessageSentEvent,
    PatientLinkedEvent,
)
from app.notifications.domain.notification_entity import NotificationEntity
from app.notifications.infrastructure.repositories.notification_repository import NotificationRepository
from app.notifications.infrastructure.repositories.device_token_repository import DeviceTokenRepository
from app.chat.infrastructure.websocket_manager import manager as ws_manager
from app.core.services.firebase_service import FirebaseNotificationService
from app.readmodels.users_read_repository import UsersReadRepository

logger = logging.getLogger(__name__)


class NotificationLogObserver:
    """Observer que persiste avisos en la tabla `notifications` de la BD."""

    def __call__(self, event) -> None:
        db = get_session_factory()()
        try:
            repo = NotificationRepository(db=db)
            users_repo = UsersReadRepository(db=db)

            if isinstance(event, AppointmentCreatedEvent):
                doctor_user_id = users_repo.get_user_id_by_doctor_id(event.doctor_id)
                if doctor_user_id:
                    repo.create(NotificationEntity(
                        user_id=doctor_user_id,
                        title="Nueva Cita Agendada",
                        body=f"Cita agendada para la fecha {event.appointment_date.strftime('%Y-%m-%d %H:%M')}",
                        type="appointment",
                    ))
                patient_user_id = users_repo.get_user_id_by_patient_id(event.patient_id)
                if patient_user_id:
                    repo.create(NotificationEntity(
                        user_id=patient_user_id,
                        title="Cita Confirmada",
                        body=f"Su cita ha sido agendada para {event.appointment_date.strftime('%Y-%m-%d %H:%M')}",
                        type="appointment",
                    ))

            elif isinstance(event, MessageSentEvent):
                repo.create(NotificationEntity(
                    user_id=event.receiver_id,
                    title="Nuevo Mensaje",
                    body=event.content[:100],
                    type="chat",
                ))

            elif isinstance(event, PatientLinkedEvent):
                doctor_user_id = users_repo.get_user_id_by_doctor_id(event.doctor_id)
                if doctor_user_id:
                    repo.create(NotificationEntity(
                        user_id=doctor_user_id,
                        title="Nuevo Paciente Vinculado",
                        body=f"El paciente #{event.patient_id} se ha vinculado a su consultorio.",
                        type="linking",
                    ))
                patient_user_id = users_repo.get_user_id_by_patient_id(event.patient_id)
                if patient_user_id:
                    repo.create(NotificationEntity(
                        user_id=patient_user_id,
                        title="Vinculación Exitosa",
                        body="Se ha completado su vinculación con el médico tratante.",
                        type="linking",
                    ))
        except Exception as e:
            logger.error(f"Error in NotificationLogObserver handling event {type(event).__name__}: {e}", exc_info=True)
        finally:
            db.close()


class ChatWebSocketObserver:
    """Observer que envía actualizaciones en tiempo real por WebSocket a usuarios conectados."""

    async def _async_notify_chat(self, event: MessageSentEvent) -> None:
        try:
            payload = {
                "type": "chat_message",
                "message_id": event.message_id,
                "sender_id": event.sender_id,
                "receiver_id": event.receiver_id,
                "content": event.content,
            }
            await ws_manager.send_personal_message(payload, event.receiver_id)
        except Exception as exc:
            logger.error(f"Error in ChatWebSocketObserver sending WS message: {exc}", exc_info=True)

    def __call__(self, event) -> None:
        if isinstance(event, MessageSentEvent):
            if event.receiver_id in ws_manager.active_connections:
                import asyncio
                try:
                    loop = asyncio.get_running_loop()
                    task = loop.create_task(self._async_notify_chat(event))
                    task.add_done_callback(lambda t: t.exception() if not t.cancelled() and t.exception() else None)
                except RuntimeError:
                    asyncio.run(self._async_notify_chat(event))


class FirebasePushObserver:
    """Observer que envía notificaciones Push vía Firebase a dispositivos móviles."""

    def __call__(self, event) -> None:
        db = get_session_factory()()
        try:
            device_repo = DeviceTokenRepository(db=db)
            users_repo = UsersReadRepository(db=db)

            target_user_id = None
            title = "Notificación"
            body = ""
            extra_data = {}

            if isinstance(event, MessageSentEvent):
                if event.receiver_id not in ws_manager.active_connections:
                    target_user_id = event.receiver_id
                    sender = users_repo.get_by_id(event.sender_id)
                    title = sender.name if sender else "Nuevo mensaje"
                    body = event.content[:100]
                    extra_data = {"type": "chat_message", "sender_id": str(event.sender_id)}

            elif isinstance(event, AppointmentCreatedEvent):
                target_user_id = users_repo.get_user_id_by_doctor_id(event.doctor_id)
                title = "Nueva Cita Agendada"
                body = f"Próxima cita: {event.appointment_date.strftime('%Y-%m-%d %H:%M')}"
                extra_data = {"type": "appointment_created", "appointment_id": str(event.appointment_id)}

            elif isinstance(event, PatientLinkedEvent):
                target_user_id = users_repo.get_user_id_by_doctor_id(event.doctor_id)
                title = "Nuevo Paciente Vinculado"
                body = f"Paciente #{event.patient_id} vinculado."
                extra_data = {"type": "patient_linked", "patient_id": str(event.patient_id)}

            if target_user_id:
                tokens = device_repo.get_tokens_by_user_id(target_user_id)
                if tokens:
                    invalid_tokens = FirebaseNotificationService.send_multicast_notification(tokens, title, body, extra_data)
                    for t in invalid_tokens:
                        device_repo.delete_token(t)
        except Exception as e:
            logger.error(f"Error in FirebasePushObserver: {e}", exc_info=True)
        finally:
            db.close()
