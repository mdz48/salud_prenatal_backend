import logging
from datetime import datetime, timedelta
from app.core.database import SessionLocal
from app.features.appointments.infrastructure.models.appointment_model import Appointment
from app.features.notifications.infrastructure.repositories.device_token_repository import DeviceTokenRepository
from app.core.services.firebase_service import FirebaseNotificationService
from app.core.enums import AppointmentStatusEnum

logger = logging.getLogger(__name__)

def notify_upcoming_appointments_job():
    db = SessionLocal()
    token_repo = DeviceTokenRepository(db)
    try:
        now = datetime.now()
        
        # 1. 24-hour window (citas entre 23h 45m y 24h en el futuro)
        window_24h_start = now + timedelta(hours=23, minutes=45)
        window_24h_end = now + timedelta(hours=24)
        appointments_24h = db.query(Appointment).filter(
            Appointment.status.in_([AppointmentStatusEnum.pending, AppointmentStatusEnum.confirmed]),
            Appointment.appointment_date >= window_24h_start,
            Appointment.appointment_date <= window_24h_end,
            Appointment.notified_24h == False
        ).all()
        
        # 2. 12-hour window (citas entre 11h 45m y 12h en el futuro)
        window_12h_start = now + timedelta(hours=11, minutes=45)
        window_12h_end = now + timedelta(hours=12)
        appointments_12h = db.query(Appointment).filter(
            Appointment.status.in_([AppointmentStatusEnum.pending, AppointmentStatusEnum.confirmed]),
            Appointment.appointment_date >= window_12h_start,
            Appointment.appointment_date <= window_12h_end,
            Appointment.notified_12h == False
        ).all()

        # 3. 1-hour window (citas entre 45m y 1h en el futuro)
        window_1h_start = now + timedelta(minutes=45)
        window_1h_end = now + timedelta(hours=1)
        appointments_1h = db.query(Appointment).filter(
            Appointment.status.in_([AppointmentStatusEnum.pending, AppointmentStatusEnum.confirmed]),
            Appointment.appointment_date >= window_1h_start,
            Appointment.appointment_date <= window_1h_end,
            Appointment.notified_1h == False
        ).all()

        # Send 24h notifications
        for appt in appointments_24h:
            if appt.patient and appt.patient.user_id:
                user_id = appt.patient.user_id
                tokens = token_repo.get_tokens_by_user_id(user_id)
                if tokens:
                    time_str = appt.appointment_date.strftime("%I:%M %p")
                    title = "Recordatorio de Cita"
                    body = f"Hola, recuerda que tienes una cita programada para mañana a las {time_str}."
                    invalid_tokens = FirebaseNotificationService.send_multicast_notification(tokens, title, body)
                    for t in invalid_tokens:
                        token_repo.delete_token(t)
            appt.notified_24h = True

        # Send 12h notifications
        for appt in appointments_12h:
            if appt.patient and appt.patient.user_id:
                user_id = appt.patient.user_id
                tokens = token_repo.get_tokens_by_user_id(user_id)
                if tokens:
                    time_str = appt.appointment_date.strftime("%I:%M %p")
                    title = "Recordatorio de Cita"
                    body = f"Hola, tu cita médica está programada para dentro de 12 horas, a las {time_str}."
                    invalid_tokens = FirebaseNotificationService.send_multicast_notification(tokens, title, body)
                    for t in invalid_tokens:
                        token_repo.delete_token(t)
            appt.notified_12h = True

        # Send 1h notifications
        for appt in appointments_1h:
            if appt.patient and appt.patient.user_id:
                user_id = appt.patient.user_id
                tokens = token_repo.get_tokens_by_user_id(user_id)
                if tokens:
                    title = "Cita Próxima"
                    body = "Tu cita médica iniciará en 1 hora. ¡No lo olvides!"
                    invalid_tokens = FirebaseNotificationService.send_multicast_notification(tokens, title, body)
                    for t in invalid_tokens:
                        token_repo.delete_token(t)
            appt.notified_1h = True
            
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error in notify_upcoming_appointments_job: {e}")
    finally:
        db.close()
