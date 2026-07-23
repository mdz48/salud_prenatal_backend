"""Servicio auth (:8001) — login y emisión de JWT.

App FastAPI delgada: verifica la contraseña sobre la tabla `users` (DB compartida)
y emite el JWT con claims (`user_id`, `role`, `subscription_status`). Es el ÚNICO
servicio que emite tokens; los demás solo los validan con la misma `SECRET_KEY`.

No es dueño de ninguna tabla: solo LEE (read-models). Por eso el lifespan no crea
schema — deja ese trabajo a los servicios dueños (usuarios/pagos/transaccional).
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from salud_prenatal_shared_core.cors import get_cors_origins
from salud_prenatal_shared_core.error_handlers import register_exception_handlers
from salud_prenatal_shared_core.security_headers import register_security_headers

# Importa los read-models para que queden mapeados en Base.metadata (no create_all).
from app.auth.infrastructure.models import auth_readmodels  # noqa: F401
from app.auth.infrastructure.routes.auth_router import router as auth_router
from container import Container

container = Container()

app = FastAPI(title="salud-prenatal · auth")
app.container = container

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
register_security_headers(app)

# Mismo path que el monolito: /api/v1/users/login (no cambia el frontend).
app.include_router(auth_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok", "service": "auth"}
