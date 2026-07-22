from app.core.events.domain_event import PatientLinkedEvent
from app.core.events.event_dispatcher import IEventDispatcher


class PublishPatientLinkedEventUseCase:
    def __init__(self, event_dispatcher: IEventDispatcher):
        self.event_dispatcher = event_dispatcher

    def execute(self, patient_id: int, doctor_id: int) -> None:
        self.event_dispatcher.publish(PatientLinkedEvent(patient_id=patient_id, doctor_id=doctor_id))
