"""Patrón Specification (ADR-08).

Encapsula una regla de negocio como un objeto con `is_satisfied_by`, componible
mediante `and_`/`or_`/`not_`. Permite que los casos de uso expresen reglas de
forma declarativa y reutilizable en lugar de condicionales dispersos.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class Specification(ABC, Generic[T]):
    @abstractmethod
    def is_satisfied_by(self, candidate: T) -> bool:  # pragma: no cover - interfaz
        ...

    def and_(self, other: "Specification[T]") -> "Specification[T]":
        return AndSpecification(self, other)

    def or_(self, other: "Specification[T]") -> "Specification[T]":
        return OrSpecification(self, other)

    def not_(self) -> "Specification[T]":
        return NotSpecification(self)


class AndSpecification(Specification[T]):
    def __init__(self, left: Specification[T], right: Specification[T]):
        self._left = left
        self._right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        return self._left.is_satisfied_by(candidate) and self._right.is_satisfied_by(candidate)


class OrSpecification(Specification[T]):
    def __init__(self, left: Specification[T], right: Specification[T]):
        self._left = left
        self._right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        return self._left.is_satisfied_by(candidate) or self._right.is_satisfied_by(candidate)


class NotSpecification(Specification[T]):
    def __init__(self, spec: Specification[T]):
        self._spec = spec

    def is_satisfied_by(self, candidate: T) -> bool:
        return not self._spec.is_satisfied_by(candidate)
