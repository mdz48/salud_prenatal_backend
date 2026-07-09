"""Patrón Notification (ADR-05).

Objeto que acumula errores de validación en lugar de fallar al primero. Permite
reportar todos los problemas de una entrada de una sola vez. Basado en el patrón
Notification de Martin Fowler.
"""
from __future__ import annotations

from typing import List, Type


class Notification:
    def __init__(self) -> None:
        self._errors: List[str] = []

    def add_error(self, message: str) -> None:
        self._errors.append(message)

    def has_errors(self) -> bool:
        return bool(self._errors)

    def is_valid(self) -> bool:
        return not self._errors

    @property
    def errors(self) -> List[str]:
        return list(self._errors)

    def summary(self) -> str:
        return "; ".join(self._errors)

    def raise_if_errors(self, exc: Type[Exception] = ValueError) -> None:
        if self._errors:
            raise exc(self.summary())
