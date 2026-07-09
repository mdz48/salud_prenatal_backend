"""Infraestructura de eventos de dominio (patrón Observer, ADR-04)."""
from app.core.events.event_bus import DomainEvent, EventBus, IEventHandler
from app.core.events.events import (
    AppointmentCreatedEvent,
    PatientLinkedToDoctorEvent,
)

__all__ = [
    "DomainEvent",
    "EventBus",
    "IEventHandler",
    "AppointmentCreatedEvent",
    "PatientLinkedToDoctorEvent",
]
