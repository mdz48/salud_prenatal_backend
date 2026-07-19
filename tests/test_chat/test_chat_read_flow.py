"""Flujo de lectura de chat contra SQLite real: consumir el history marca
como leidos SOLO los mensajes dirigidos a quien consulta."""
import pytest

pytestmark = pytest.mark.integration

DOCTOR_ID = 9001
PACIENTE_ID = 9002


@pytest.fixture()
def repo(app):
    from app.core.database import get_session_factory
    from app.features.chat.infrastructure.models.chat_model import Message
    from app.features.chat.infrastructure.repositories.chat_repository import ChatRepository

    db = get_session_factory()()
    try:
        # Limpia mensajes de corridas previas de estos usuarios sinteticos
        db.query(Message).filter(
            Message.sender_id.in_([DOCTOR_ID, PACIENTE_ID])
        ).delete(synchronize_session=False)
        db.commit()
        yield ChatRepository(db)
    finally:
        db.close()


def test_history_marca_leidos_solo_los_entrantes(repo):
    from app.features.chat.application.get_history_usecase import GetHistoryUseCase

    repo.save_message(DOCTOR_ID, PACIENTE_ID, "hola paciente 1")
    repo.save_message(DOCTOR_ID, PACIENTE_ID, "hola paciente 2")
    repo.save_message(PACIENTE_ID, DOCTOR_ID, "hola doctor")

    # El paciente abre la conversacion (paciente = quien consulta)
    history = GetHistoryUseCase(repo).execute(PACIENTE_ID, DOCTOR_ID)

    assert len(history) == 3
    entrantes = [m for m in history if m.receiver_id == PACIENTE_ID]
    salientes = [m for m in history if m.sender_id == PACIENTE_ID]
    assert all(m.is_read for m in entrantes)          # lo que recibio queda leido
    assert all(not m.is_read for m in salientes)      # lo que envio lo marca el doctor, no el

    # Inbox: el paciente ya no tiene no-leidos; el doctor sigue con 1
    inbox_paciente = {s.other_user_id: s for s in repo.get_inbox(PACIENTE_ID)}
    inbox_doctor = {s.other_user_id: s for s in repo.get_inbox(DOCTOR_ID)}
    assert inbox_paciente[DOCTOR_ID].unread_count == 0
    assert inbox_doctor[PACIENTE_ID].unread_count == 1


def test_mark_conversation_read_es_idempotente(repo):
    repo.save_message(DOCTOR_ID, PACIENTE_ID, "mensaje nuevo")

    assert repo.mark_conversation_read(reader_id=PACIENTE_ID, other_user_id=DOCTOR_ID) == 1
    assert repo.mark_conversation_read(reader_id=PACIENTE_ID, other_user_id=DOCTOR_ID) == 0
