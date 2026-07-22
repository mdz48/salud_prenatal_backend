"""Origenes CORS permitidos para los 5 servicios.

`allow_origins=["*"]` junto con `allow_credentials=True` expone cualquier
request autenticada (Authorization: Bearer) a un origen arbitrario -- el
navegador no bloquea la respuesta porque Starlette refleja el Origin pedido
en vez de mandar literalmente "*" cuando allow_credentials=True. Este helper
lee `FRONTEND_URL` (uno o más orígenes separados por coma) y, si no está
seteada, no permite ningún origen cross-site (falla cerrado).
"""
import os


def get_cors_origins() -> list[str]:
    raw = os.getenv("FRONTEND_URL", "")
    return [origin.strip() for origin in raw.split(",") if origin.strip()]
