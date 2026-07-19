import logging
from datetime import datetime, timedelta
from salud_prenatal_shared_core.database import get_session_factory
from app.appointments.infrastructure.models.appointment_model import Appointment
from app.notifications.infrastructure.repositories.device_token_repository import DeviceTokenRepository
from app.core.services.firebase_service import FirebaseNotificationService
from salud_prenatal_shared_core.enums import AppointmentStatusEnum
# En el split, Appointment ya no tiene la relación ORM `patient` (patient_id es una
# columna plana). El user_id del paciente se resuelve leyendo el read-model de la
# tabla `patients` (owned por el servicio usuarios) sobre la DB compartida.
from app.readmodels.users_readmodels import PatientRead

logger = logging.getLogger(__name__)


def _user_id_for_patient(db, patient_id: int):
    patient = db.query(PatientRead).filter(PatientRead.patient_id == patient_id).first()
    return patient.user_id if patient else None

def notify_upcoming_appointments_job():
    db = get_session_factory()()
    token_repo = DeviceTokenRepository(db)
    
    appointments_to_notify_24h = []
    appointments_to_notify_12h = []
    appointments_to_notify_1h = []
    
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

        for appt in appointments_24h:
            user_id = _user_id_for_patient(db, appt.patient_id)
            if user_id:
                tokens = token_repo.get_tokens_by_user_id(user_id)
                if tokens:
                    appointments_to_notify_24h.append({
                        "appt_id": appt.appointment_id,
                        "tokens": tokens,
                        "time_str": appt.appointment_date.strftime("%I:%M %p")
                    })
        
        for appt in appointments_12h:
            user_id = _user_id_for_patient(db, appt.patient_id)
            if user_id:
                tokens = token_repo.get_tokens_by_user_id(user_id)
                if tokens:
                    appointments_to_notify_12h.append({
                        "appt_id": appt.appointment_id,
                        "tokens": tokens,
                        "time_str": appt.appointment_date.strftime("%I:%M %p")
                    })
                    
        for appt in appointments_1h:
            user_id = _user_id_for_patient(db, appt.patient_id)
            if user_id:
                tokens = token_repo.get_tokens_by_user_id(user_id)
                if tokens:
                    appointments_to_notify_1h.append({
                        "appt_id": appt.appointment_id,
                        "tokens": tokens
                    })
    except Exception as e:
        logger.error(f"Error in notify_upcoming_appointments_job (Read Phase): {e}")
        return
    finally:
        db.close()

    # 2. Fase de notificaciones (Sin DB activa)
    invalid_tokens_to_delete = []
    notified_24h_ids = []
    notified_12h_ids = []
    notified_1h_ids = []

    for info in appointments_to_notify_24h:
        title = "Recordatorio de Cita"
        body = f"Hola, recuerda que tienes una cita programada para mañana a las {info['time_str']}."
        try:
            invalid = FirebaseNotificationService.send_multicast_notification(info["tokens"], title, body)
            if invalid:
                invalid_tokens_to_delete.extend(invalid)
            notified_24h_ids.append(info["appt_id"])
        except Exception as e:
            logger.error(f"Error sending 24h notification for appt {info['appt_id']}: {e}")

    for info in appointments_to_notify_12h:
        title = "Recordatorio de Cita"
        body = f"Hola, tu cita médica está programada para dentro de 12 horas, a las {info['time_str']}."
        try:
            invalid = FirebaseNotificationService.send_multicast_notification(info["tokens"], title, body)
            if invalid:
                invalid_tokens_to_delete.extend(invalid)
            notified_12h_ids.append(info["appt_id"])
        except Exception as e:
            logger.error(f"Error sending 12h notification for appt {info['appt_id']}: {e}")

    for info in appointments_to_notify_1h:
        title = "Cita Próxima"
        body = "Tu cita médica iniciará en 1 hora. ¡No lo olvides!"
        try:
            invalid = FirebaseNotificationService.send_multicast_notification(info["tokens"], title, body)
            if invalid:
                invalid_tokens_to_delete.extend(invalid)
            notified_1h_ids.append(info["appt_id"])
        except Exception as e:
            logger.error(f"Error sending 1h notification for appt {info['appt_id']}: {e}")

    # 3. Fase de escritura (Nueva sesión DB)
    if notified_24h_ids or notified_12h_ids or notified_1h_ids or invalid_tokens_to_delete:
        db = get_session_factory()()
        token_repo = DeviceTokenRepository(db)
        try:
            for t in invalid_tokens_to_delete:
                try:
                    token_repo.delete_token(t)
                except Exception as ex:
                    logger.error(f"Error deleting invalid token {t}: {ex}")
            
            if notified_24h_ids:
                db.query(Appointment).filter(Appointment.appointment_id.in_(notified_24h_ids)).update(
                    {Appointment.notified_24h: True}, synchronize_session=False
                )
            if notified_12h_ids:
                db.query(Appointment).filter(Appointment.appointment_id.in_(notified_12h_ids)).update(
                    {Appointment.notified_12h: True}, synchronize_session=False
                )
            if notified_1h_ids:
                db.query(Appointment).filter(Appointment.appointment_id.in_(notified_1h_ids)).update(
                    {Appointment.notified_1h: True}, synchronize_session=False
                )
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Error in notify_upcoming_appointments_job (Write Phase): {e}")
        finally:
            db.close()

def send_daily_bitacora_reminder_job():
    db = get_session_factory()()
    token_repo = DeviceTokenRepository(db)
    try:
        tokens = token_repo.get_all_tokens()
        if not tokens:
            return

        title = "Recordatorio diario"
        body = "Recuerda hacer tus registros en la bitácora"
        data = {"type": "daily_reminder"}

        # FCM permite máximo 500 tokens por multicast; se envía en lotes.
        batch_size = 500
        invalid_tokens = []
        for i in range(0, len(tokens), batch_size):
            batch = tokens[i:i + batch_size]
            invalid_tokens.extend(
                FirebaseNotificationService.send_multicast_notification(batch, title, body, data)
            )

        for t in invalid_tokens:
            token_repo.delete_token(t)
    except Exception as e:
        logger.error(f"Error in send_daily_bitacora_reminder_job: {e}")
    finally:
        db.close()
