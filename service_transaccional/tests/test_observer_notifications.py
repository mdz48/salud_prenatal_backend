from datetime import datetime, timezone
from unittest.mock import MagicMock

from salud_prenatal_shared_core.database import ReadModelBase, Base, get_engine, get_session_factory
from app.core.events.domain_event import (
    AppointmentCreatedEvent,
    MessageSentEvent,
    PatientLinkedEvent,
    DomainEvent,
)
from app.core.events.event_dispatcher import InMemoryEventDispatcher
from app.notifications.domain.notification_entity import NotificationEntity
from app.notifications.infrastructure.repositories.notification_repository import NotificationRepository
from app.notifications.infrastructure.observers.notification_observers import (
    NotificationLogObserver,
    ChatWebSocketObserver,
)
from app.appointments.domain.appointment_entity import AppointmentEntity
from app.appointments.application.create_appointment_usecase import CreateAppointmentUseCase
from app.chat.application.save_message_usecase import SaveMessageUseCase
from app.notifications.application.publish_patient_linked_event_usecase import PublishPatientLinkedEventUseCase
from app.readmodels.users_readmodels import DoctorRead, PatientRead


def setup_test_db():
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    ReadModelBase.metadata.create_all(bind=engine)
    return get_session_factory()()


def test_in_memory_event_dispatcher_publishes_to_subscribers():
    dispatcher = InMemoryEventDispatcher()

    appointment_events = []
    message_events = []

    dispatcher.subscribe(AppointmentCreatedEvent, lambda e: appointment_events.append(e))
    dispatcher.subscribe(MessageSentEvent, lambda e: message_events.append(e))

    evt1 = AppointmentCreatedEvent(appointment_id=1, patient_id=10, doctor_id=20, appointment_date=datetime.now())
    evt2 = MessageSentEvent(message_id=100, sender_id=5, receiver_id=6, content="Hola")

    dispatcher.publish(evt1)
    dispatcher.publish(evt2)

    assert len(appointment_events) == 1
    assert appointment_events[0].appointment_id == 1
    assert len(message_events) == 1
    assert message_events[0].message_id == 100


def test_notification_log_observer_creates_db_rows():
    db = setup_test_db()
    try:
        # Seed readmodels for doctor (id=20) -> user_id=200 and patient (id=10) -> user_id=100
        doc = DoctorRead(doctor_id=20, user_id=200)
        pat = PatientRead(patient_id=10, user_id=100)
        db.add_all([doc, pat])
        db.commit()

        observer = NotificationLogObserver()

        evt = AppointmentCreatedEvent(
            appointment_id=1,
            patient_id=10,
            doctor_id=20,
            appointment_date=datetime(2026, 8, 1, 10, 0),
        )
        observer(evt)

        repo = NotificationRepository(db=db)
        doc_notifs = repo.get_by_user_id(200)
        pat_notifs = repo.get_by_user_id(100)

        assert len(doc_notifs) == 1
        assert doc_notifs[0].title == "Nueva Cita Agendada"
        assert doc_notifs[0].type == "appointment"

        assert len(pat_notifs) == 1
        assert pat_notifs[0].title == "Cita Confirmada"
        assert pat_notifs[0].type == "appointment"
    finally:
        db.close()


def test_create_appointment_usecase_dispatches_event():
    appointment_repo = MagicMock()
    patient_lookup = MagicMock()
    doctor_lookup = MagicMock()
    dispatcher = MagicMock()

    patient_lookup.get_by_id.return_value = object()
    doctor_lookup.get_by_id.return_value = object()

    entity = AppointmentEntity(
        appointment_id=1,
        patient_id=10,
        doctor_id=20,
        appointment_date=datetime(2026, 8, 1, 10, 0),
    )
    appointment_repo.create.return_value = entity

    usecase = CreateAppointmentUseCase(
        appointment_repo=appointment_repo,
        patient_repo=patient_lookup,
        doctor_repo=doctor_lookup,
        event_dispatcher=dispatcher,
    )

    created = usecase.execute(entity)
    assert created.appointment_id == 1
    assert dispatcher.publish.called
    published_evt = dispatcher.publish.call_args[0][0]
    assert isinstance(published_evt, AppointmentCreatedEvent)
    assert published_evt.appointment_id == 1


def test_save_message_usecase_dispatches_event():
    chat_repo = MagicMock()
    dispatcher = MagicMock()

    msg = MagicMock()
    msg.message_id = 99
    msg.sender_id = 1
    msg.receiver_id = 2
    msg.content = "Probando evento"
    chat_repo.save_message.return_value = msg

    usecase = SaveMessageUseCase(chat_repository=chat_repo, event_dispatcher=dispatcher)
    result = usecase.execute(sender_id=1, receiver_id=2, content="Probando evento")

    assert result.message_id == 99
    assert dispatcher.publish.called
    published_evt = dispatcher.publish.call_args[0][0]
    assert isinstance(published_evt, MessageSentEvent)
    assert published_evt.content == "Probando evento"


def test_publish_patient_linked_event_usecase_dispatches_event():
    dispatcher = MagicMock()
    usecase = PublishPatientLinkedEventUseCase(event_dispatcher=dispatcher)

    usecase.execute(patient_id=5, doctor_id=10)

    assert dispatcher.publish.called
    published_evt = dispatcher.publish.call_args[0][0]
    assert isinstance(published_evt, PatientLinkedEvent)
    assert published_evt.patient_id == 5
    assert published_evt.doctor_id == 10


def test_patient_linked_event_reaches_log_and_push_observers():
    """PatientLinkedEvent, ahora publicado DENTRO de transaccional (vía el endpoint
    interno), sí llega a NotificationLogObserver -- a diferencia de cuando lo
    publicaba service_usuarios en su propio proceso aislado."""
    db = setup_test_db()
    try:
        doc = DoctorRead(doctor_id=21, user_id=201)
        pat = PatientRead(patient_id=11, user_id=101)
        db.add_all([doc, pat])
        db.commit()

        observer = NotificationLogObserver()
        observer(PatientLinkedEvent(patient_id=11, doctor_id=21))

        repo = NotificationRepository(db=db)
        doc_notifs = repo.get_by_user_id(201)
        pat_notifs = repo.get_by_user_id(101)

        assert len(doc_notifs) == 1
        assert doc_notifs[0].title == "Nuevo Paciente Vinculado"
        assert len(pat_notifs) == 1
        assert pat_notifs[0].title == "Vinculación Exitosa"
    finally:
        db.close()
