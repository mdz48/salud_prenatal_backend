"""Servicio usuarios (:8002) — CRUD de usuarios, doctores, pacientes, recepcionistas.

App FastAPI independiente sobre la DB compartida. El login NO vive aquí (va al
servicio auth); la autenticación de rutas usa el JWT (claims) vía shared_core.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from salud_prenatal_shared_core.database import Base, get_engine
from salud_prenatal_shared_core.error_handlers import register_exception_handlers

# Registrar los modelos (y read-models) en Base.metadata antes de create_all.
from app.users.infrastructure.models import (  # noqa: F401
    user_model,
    patient_model,
    doctor_model,
    receptionist_model,
    invitation_code_model,
)
from app.users.infrastructure.readmodels import (  # noqa: F401
    appointment_readmodel,
    medical_record_readmodel,
)

from app.users.infrastructure.routes.user_router import router as user_router
from app.users.infrastructure.routes.doctor_router import router as doctor_router
from app.users.infrastructure.routes.patient_router import router as patient_router
from container import Container


@asynccontextmanager
async def lifespan(app: FastAPI):
    # DB compartida: create_all con checkfirst solo crea las tablas de usuarios si
    # faltan. Las tablas appointments/medical_records las owned el servicio
    # transaccional; aquí solo se leen por read-model.
    Base.metadata.create_all(bind=get_engine())
    yield


container = Container()

app = FastAPI(title="salud-prenatal · usuarios", lifespan=lifespan)
app.container = container

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(user_router, prefix="/api/v1")
app.include_router(doctor_router, prefix="/api/v1")
app.include_router(patient_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok", "service": "usuarios"}
