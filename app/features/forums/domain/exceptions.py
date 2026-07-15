class AdPermissionError(Exception):
    """El autor no tiene suscripcion premium activa para publicar anuncios."""


class AdRateLimitError(Exception):
    """El autor ya alcanzo el tope semanal de anuncios."""
