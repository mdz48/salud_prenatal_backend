from typing import List


class Notification:
    """Patrón Notification (Fowler): acumula todos los errores de validación
    antes de rechazar, en vez de abortar en el primer campo inválido."""

    def __init__(self):
        self._errors: List[str] = []

    def add_error(self, message: str) -> None:
        self._errors.append(message)

    def has_errors(self) -> bool:
        return bool(self._errors)

    @property
    def errors(self) -> List[str]:
        return list(self._errors)

    def message(self) -> str:
        return "; ".join(self._errors)
