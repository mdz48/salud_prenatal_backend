"""Tests de los building blocks de patrones en app/core (ADR-04, 05, 07, 08)."""
from dataclasses import dataclass

import pytest

from app.core.notification import Notification
from app.core.query.name_search_query import NameSearchCriteria
from app.core.specification import Specification
from app.core.events.event_bus import DomainEvent, EventBus


# --- ADR-08 Specification ---
class _GreaterThan(Specification[int]):
    def __init__(self, threshold):
        self.threshold = threshold

    def is_satisfied_by(self, candidate):
        return candidate > self.threshold


def test_specification_and_or_not():
    gt5 = _GreaterThan(5)
    gt10 = _GreaterThan(10)

    assert gt5.is_satisfied_by(7) is True
    assert gt5.and_(gt10).is_satisfied_by(7) is False
    assert gt5.and_(gt10).is_satisfied_by(11) is True
    assert gt5.or_(gt10).is_satisfied_by(7) is True
    assert gt5.not_().is_satisfied_by(3) is True


# --- ADR-05 Notification ---
def test_notification_accumulates_and_raises():
    n = Notification()
    assert n.is_valid() is True
    n.add_error("a")
    n.add_error("b")
    assert n.has_errors() is True
    assert n.errors == ["a", "b"]
    assert n.summary() == "a; b"
    with pytest.raises(ValueError, match="a; b"):
        n.raise_if_errors()


# --- ADR-07 Query Object ---
def test_name_search_criteria_matching():
    crit = NameSearchCriteria(name="mari")
    assert crit.is_empty() is False
    assert crit.matches("María", "López") is True
    assert crit.matches("Ana", "López") is False
    assert NameSearchCriteria().is_empty() is True
    # acentos y mayúsculas se ignoran
    assert NameSearchCriteria(last_name="martinez").matches("Ana", "Martínez") is True


# --- ADR-04 Observer ---
@dataclass
class _Ping(DomainEvent):
    value: int = 0


def test_event_bus_publishes_to_subscribers():
    received = []

    class _Handler:
        def handle(self, event):
            received.append(event.value)

    bus = EventBus()
    bus.subscribe(_Ping, _Handler())
    bus.subscribe(_Ping, _Handler())
    bus.publish(_Ping(value=42))

    assert received == [42, 42]


def test_event_bus_ignores_unsubscribed_event_types():
    received = []

    class _Handler:
        def handle(self, event):
            received.append(event)

    bus = EventBus()
    bus.subscribe(_Ping, _Handler())
    bus.publish(DomainEvent())  # tipo sin suscriptores

    assert received == []
