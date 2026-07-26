"""Decorador que garantiza el cierre de la sesion `db` (ContextLocalSingleton)
al final de cada request, sync o async. Un middleware ASGI no sirve: los handlers
sync se despachan en su propio to_thread.run_sync, distinto del que usa cada
Depends generador; el middleware corre en el contexto async padre y nunca ve el
ContextVar seteado dentro de esos hilos. Un decorador que envuelve la funcion ruta
si corre en el mismo hilo/tarea que el handler."""
import asyncio
import functools
import logging

logger = logging.getLogger("app")


def close_db_after(container):
    def decorator(func):
        def _cleanup():
            try:
                db = container.db()
                db.close()
            except Exception:
                logger.exception("Error cerrando sesion db en cleanup de request")
            finally:
                container.db.reset()

        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                finally:
                    _cleanup()
            return async_wrapper

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            finally:
                _cleanup()
        return sync_wrapper

    return decorator
