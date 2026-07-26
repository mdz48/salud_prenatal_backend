import logging
from typing import Protocol, Type, Callable, Dict, List, Any
from salud_prenatal_shared_core.events.domain_event import DomainEvent

logger = logging.getLogger(__name__)


class IEventDispatcher(Protocol):
    def subscribe(self, event_type: Type[DomainEvent], observer: Callable[[Any], None]) -> None: ...
    def publish(self, event: DomainEvent) -> None: ...


class InMemoryEventDispatcher(IEventDispatcher):
    def __init__(self):
        self._observers: Dict[Type[DomainEvent], List[Callable[[Any], None]]] = {}

    def subscribe(self, event_type: Type[DomainEvent], observer: Callable[[Any], None]) -> None:
        if event_type not in self._observers:
            self._observers[event_type] = []
        self._observers[event_type].append(observer)

    def publish(self, event: DomainEvent) -> None:
        event_type = type(event)
        observers = self._observers.get(event_type, [])
        for observer in observers:
            try:
                observer(event)
            except Exception as exc:
                logger.error(f"Error handling event {event_type.__name__} in observer {observer}: {exc}", exc_info=True)
