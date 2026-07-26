import unicodedata


def normalize_text(value: str) -> str:
    """Minúsculas y sin acentos, para comparaciones de búsqueda."""
    decomposed = unicodedata.normalize("NFD", value)
    without_accents = "".join(c for c in decomposed if not unicodedata.combining(c))
    return without_accents.casefold()
