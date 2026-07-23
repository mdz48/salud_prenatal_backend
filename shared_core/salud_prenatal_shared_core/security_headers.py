"""Cabeceras de seguridad HTTP faltantes (detectadas por ZAP).

Ningún cliente legítimo depende de que falten estas cabeceras, así que se
aplican a toda respuesta sin excepción:

- Strict-Transport-Security: fuerza HTTPS en el navegador (Traefik ya sirve
  todo por TLS). max-age 1 año + subdominios.
- X-Content-Type-Options: nosniff -- evita que el navegador reinterprete el
  Content-Type declarado (mitiga MIME-sniffing).
- Cache-Control: no-store -- estas APIs devuelven datos autenticados/PII,
  nunca deben cachearse (browser, proxy, o disco).
"""
from fastapi import FastAPI, Request


def register_security_headers(app: FastAPI) -> None:
    @app.middleware("http")
    async def _security_headers_middleware(request: Request, call_next):
        response = await call_next(request)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Cache-Control"] = "no-store"
        return response
