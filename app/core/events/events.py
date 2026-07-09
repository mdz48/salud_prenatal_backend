"""Eventos de dominio concretos publicados por los casos de uso."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.core.events.event_bus import DomainEvent


@dataclass
class PatientLinkedToDoctorEvent(DomainEvent):
    """Un paciente quedó vinculado a un doctor (canje de código de invitación)."""

    patient_id: int = 0
    doctor_id: int = 0


@dataclass
class AppointmentCreatedEvent(DomainEvent):
    """Se creó una cita entre un paciente y un doctor."""

    appointment_id: Optional[int] = None
    patient_id: int = 0
    doctor_id: int = 0
