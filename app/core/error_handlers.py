"""Manejo centralizado de errores.

Objetivo: nunca exponer detalles internos (SQL, trazas, errores de driver)
al cliente. El detalle completo se registra en el log del servidor y al
cliente solo se le devuelve un mensaje generico.
"""
import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger("app")

# Mensaje generico que ve el cliente ante cualquier fallo interno.
GENERIC_INTERNAL_DETAIL = "Ocurrio un error interno. Intenta de nuevo mas tarde."


def internal_error(exc: Exception) -> HTTPException:
    """Registra el detalle real y devuelve un HTTPException 500 generico.

    Usar en los controllers en lugar de `HTTPException(500, detail=str(exc))`
    para no filtrar la causa interna del fallo al cliente.
    """
    logger.exception("Error interno no controlado: %s", exc)
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=GENERIC_INTERNAL_DETAIL,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Red de seguridad global para excepciones que escapen de los controllers.

    Las `HTTPException` de dominio (400/402/404/429...) siguen su curso normal
    porque Starlette las maneja aparte; aqui solo capturamos lo inesperado.
    """

    @app.exception_handler(SQLAlchemyError)
    async def _sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
        logger.exception(
            "Error de base de datos en %s %s", request.method, request.url.path
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": GENERIC_INTERNAL_DETAIL},
        )

    @app.exception_handler(Exception)
    async def _unhandled_error_handler(request: Request, exc: Exception):
        logger.exception(
            "Error no controlado en %s %s", request.method, request.url.path
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": GENERIC_INTERNAL_DETAIL},
        )
