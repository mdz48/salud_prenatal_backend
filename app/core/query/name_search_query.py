"""Patrón Query Object (ADR-07): criterio de búsqueda por nombre/apellido.

Encapsula la regla de coincidencia (parcial, sin distinción de mayúsculas ni
acentos) en un objeto reutilizable, en vez de repetir el filtrado en cada caso de
uso. Los casos de uso extraen los campos de su entidad y delegan la comparación.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.core.text import normalize_text


@dataclass(frozen=True)
class NameSearchCriteria:
    name: Optional[str] = None
    last_name: Optional[str] = None

    def is_empty(self) -> bool:
        return not self.name and not self.last_name

    def matches(self, name_value: Optional[str], last_name_value: Optional[str]) -> bool:
        if self.name and normalize_text(self.name) not in normalize_text(name_value or ""):
            return False
        if self.last_name and normalize_text(self.last_name) not in normalize_text(last_name_value or ""):
            return False
        return True
