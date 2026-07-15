"""Key Manager de la llave del JWT — detrás de una interfaz (port).

La caja "Key Manager" del diagrama: quién firma (Auth Generator = servicio auth) y
quién valida (Auth Checker = gateway / servicios) le piden la llave AQUÍ, sin saber
de dónde sale. Hoy sale del entorno (HS256, una sola SECRET_KEY). Mañana, si el key
manager es un servicio EXTERNO, se agrega otro adapter (p. ej. HttpJwksJwtKeyProvider
que descarga la llave pública por JWKS) y NADIE MÁS cambia: ni la firma ni la
validación se tocan.

- HS256 (hoy): la misma SECRET_KEY firma y valida.
- RS256 (externo, futuro): firma con privada (solo el key manager la tiene), valida
  con la pública que expone por JWKS. Por eso `get_verification_key(kid)` acepta un
  `kid` (key id) para soportar rotación.
"""
from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Optional
import os

from dotenv import load_dotenv

ALGORITHM_HS256 = "HS256"


class IJwtKeyProvider(ABC):
    """Provee las llaves para firmar y validar JWTs. La implementación decide la
    fuente (env, KMS, JWKS de un servicio externo…)."""

    @property
    @abstractmethod
    def algorithm(self) -> str:
        ...

    @abstractmethod
    def get_signing_key(self) -> str:
        """Llave para FIRMAR. La usa solo el servicio auth (Auth Generator)."""
        ...

    @abstractmethod
    def get_verification_key(self, kid: Optional[str] = None) -> str:
        """Llave para VALIDAR. La usan el gateway y los servicios. En HS256 es la
        misma que la de firma; en RS256 sería la pública, seleccionada por `kid`."""
        ...


class EnvJwtKeyProvider(IJwtKeyProvider):
    """HS256: una sola SECRET_KEY del entorno firma y valida. Es el comportamiento
    actual del sistema, ahora detrás del port."""

    @property
    def algorithm(self) -> str:
        return ALGORITHM_HS256

    def _secret(self) -> str:
        load_dotenv()
        key = os.getenv("SECRET_KEY")
        if not key:
            raise RuntimeError("SECRET_KEY no configurada; requerida para firmar/validar JWTs.")
        return key

    def get_signing_key(self) -> str:
        return self._secret()

    def get_verification_key(self, kid: Optional[str] = None) -> str:
        return self._secret()


@lru_cache
def get_jwt_key_provider() -> IJwtKeyProvider:
    """Punto ÚNICO para obtener el Key Manager activo. Para externalizarlo (JWKS de
    un servicio de llaves) se cambia SOLO esta función por el nuevo adapter; ni la
    firma ni la validación se enteran."""
    return EnvJwtKeyProvider()
