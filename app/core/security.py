"""Shim de migración → salud_prenatal_shared_core.security.

El código real vive en `shared_core`. Se conserva para no romper
`from app.core.security import ...` durante la migración (plan Sesión 1).
"""
from salud_prenatal_shared_core.security import *  # noqa: F401,F403
