from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class DomainEvent(BaseModel):
    """Base class for all domain events in the system."""
    occurred_on: datetime = Field(default_factory=datetime.utcnow)


class AppointmentCreatedEvent(DomainEvent):
    appointment_id: int
    patient_id: int
    doctor_id: int
    appointment_date: datetime
    reason: Optional[str] = None


class MessageSentEvent(DomainEvent):
    message_id: int
    sender_id: int
    receiver_id: int
    content: str


class PatientLinkedEvent(DomainEvent):
    patient_id: int
    doctor_id: int
