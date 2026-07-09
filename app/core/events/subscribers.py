"""Observadores por defecto y ensamblado del bus de eventos."""
from __future__ import annotations

import logging

from app.core.events.event_bus import DomainEvent, EventBus
from app.core.events.events import (
    AppointmentCreatedEvent,
    PatientLinkedToDoctorEvent,
)

logger = logging.getLogger("domain.events")


class LoggingSubscriber:
    """Observador de ejemplo: registra cada evento de dominio."""

    def handle(self, event: DomainEvent) -> None:
        logger.info("Evento de dominio: %s", event)


def build_event_bus() -> EventBus:
    """Fábrica del bus con los observadores por defecto ya suscritos."""
    bus = EventBus()
    logging_subscriber = LoggingSubscriber()
    bus.subscribe(PatientLinkedToDoctorEvent, logging_subscriber)
    bus.subscribe(AppointmentCreatedEvent, logging_subscriber)
    return bus
