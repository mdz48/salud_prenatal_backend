"""Patrón Factory Method (ADR-12) para códigos de invitación.

`InvitationCodeFactory` define el esqueleto de construcción (código + expiración) y
delega la generación del código en el método fábrica `generate_code`, que las
subclases concretas implementan. Permite cambiar la estrategia de generación sin
tocar el repositorio.
"""
from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Any, Dict


class InvitationCodeFactory(ABC):
    TTL_HOURS = 72

    def build(self, doctor_id: int) -> Dict[str, Any]:
        return {
            "code": self.generate_code(),
            "doctor_id": doctor_id,
            "expires_at": self._expires_at(),
        }

    def _expires_at(self) -> datetime:
        return datetime.now(timezone.utc) + timedelta(hours=self.TTL_HOURS)

    @abstractmethod
    def generate_code(self) -> str:
        ...


class UuidInvitationCodeFactory(InvitationCodeFactory):
    """Genera un código de 8 caracteres derivado de un UUID4."""

    def generate_code(self) -> str:
        return str(uuid.uuid4())[:8]
