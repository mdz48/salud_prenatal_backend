"""Servicio pagos (:8003) — suscripciones y facturación vía Stripe.

App FastAPI independiente sobre la DB compartida. Solo EMITE cobros por Stripe;
la autenticación se valida con el JWT (claims) vía shared_core, sin tocar la DB
de usuarios.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from salud_prenatal_shared_core.cors import get_cors_origins
from salud_prenatal_shared_core.database import Base, get_engine
from salud_prenatal_shared_core.error_handlers import register_exception_handlers

# Importa los modelos para que queden registrados en Base.metadata antes de create_all.
from app.subscriptions.infrastructure.models import subscription_model  # noqa: F401
from app.subscriptions.infrastructure.models import payment_transaction_model  # noqa: F401
from app.subscriptions.infrastructure.routes.subscription_router import router as subscription_router
from container import Container


@asynccontextmanager
async def lifespan(app: FastAPI):
    # DB compartida: create_all con checkfirst (default) solo crea la tabla
    # subscriptions si no existe. El resto de tablas las crean sus servicios.
    Base.metadata.create_all(bind=get_engine())
    yield


container = Container()

app = FastAPI(title="salud-prenatal · pagos", lifespan=lifespan)
app.container = container

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

# Mismo prefijo que el monolito: /api/v1/subscriptions/...
app.include_router(subscription_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok", "service": "pagos"}
