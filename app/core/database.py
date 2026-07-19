"""Shim de migración → salud_prenatal_shared_core.database.

El código real vive en el paquete `shared_core`. Este módulo se conserva para
no romper los imports `from app.core.database import ...` del monolito durante
la migración a servicios (plan Sesión 1). Se retirará al final.
"""
from salud_prenatal_shared_core.database import *  # noqa: F401,F403
from salud_prenatal_shared_core.database import _resolve_database_url  # noqa: F401
