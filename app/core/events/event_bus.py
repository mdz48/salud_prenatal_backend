"""Patrón Observer (ADR-04): bus de eventos de dominio.

Los casos de uso publican eventos (`publish`) sin conocer a sus consumidores; los
observadores se registran (`subscribe`) por tipo de evento. Desacopla los efectos
secundarios (notificaciones, logging, side-effects) de la lógica de negocio.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Protocol, Type, runtime_checkable


@dataclass
class DomainEvent:
    """Clase base de todo evento de dominio."""

    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@runtime_checkable
class IEventHandler(Protocol):
    def handle(self, event: DomainEvent) -> None: ...


class EventBus:
    def __init__(self) -> None:
        self._subscribers: Dict[Type[DomainEvent], List[IEventHandler]] = defaultdict(list)

    def subscribe(self, event_type: Type[DomainEvent], handler: IEventHandler) -> None:
        self._subscribers[event_type].append(handler)

    def publish(self, event: DomainEvent) -> None:
        # Copia defensiva: un handler podría (des)suscribir durante el despacho.
        for handler in list(self._subscribers.get(type(event), [])):
            handler.handle(event)

    def clear(self) -> None:
        self._subscribers.clear()
