"""Servicio transaccional (:8004) — el más grande.

Absorbe 7 features: appointments, consultations, medical_record, patient_diaries,
forums, chat y notifications. Los adapters internos entre estas features quedan
EN-PROCESO; los que cruzaban a users/subscriptions leen la DB compartida vía
read-models. La autorización de rutas usa el JWT (claims) de shared_core.
"""
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from salud_prenatal_shared_core.database import Base, get_engine
from salud_prenatal_shared_core.error_handlers import register_exception_handlers
from app.notifications.application.tasks import (
    notify_upcoming_appointments_job,
    send_daily_bitacora_reminder_job,
)

# --- Registrar modelos propios en Base.metadata antes de create_all ---
from app.appointments.infrastructure.models import appointment_model  # noqa: F401
from app.chat.infrastructure.models import chat_model  # noqa: F401
from app.consultations.infrastructure.models import consultation_model  # noqa: F401
from app.medical_record.infrastructure.models import medical_record_model, risk_prediction_model  # noqa: F401
from app.patient_diaries.infrastructure.models import (  # noqa: F401
    patient_diaries_model,
    diary_body_zone_model,
    diary_symptom_extraction_model,
)
from app.forums.infrastructure.models import (  # noqa: F401
    post_model,
    comment_model,
    community_group_model,
    report_model,
    social_profile_model,
)
from app.notifications.infrastructure.models import device_token_model  # noqa: F401
# Read-models sobre la DB compartida (users/subscriptions) — solo lectura.
from app.readmodels import users_readmodels, subscriptions_readmodels  # noqa: F401

# --- Routers ---
from app.appointments.infrastructure.routes.appointment_router import router as appointment_router
from app.chat.infrastructure.routes.chat_router import router as chat_router
from app.consultations.infrastructure.routes.consultation_router import router as consultation_router
from app.medical_record.infrastructure.routes.medical_record_router import router as medical_record_router
from app.patient_diaries.infrastructure.routes.patient_diary_router import router as patient_diary_router
from app.forums.infrastructure.routes.profiles_router import router as profiles_router
from app.forums.infrastructure.routes.groups_router import router as groups_router
from app.forums.infrastructure.routes.posts_router import router as posts_router
from app.forums.infrastructure.routes.reports_router import router as reports_router
from app.notifications.infrastructure.routes.notification_router import router as notification_router

from container import Container


@asynccontextmanager
async def lifespan(app: FastAPI):
    # DB compartida: create_all con checkfirst solo crea las tablas de este servicio
    # si faltan. Las tablas de users/subscriptions las owned sus servicios; aquí
    # solo se leen por read-model (extend_existing, no las recrea).
    Base.metadata.create_all(bind=get_engine())

    # Jobs de notificaciones (antes en el monolito). Viven aquí porque transaccional
    # es dueño de appointments + notifications. Sin esto, los recordatorios de cita
    # y el aviso diario de bitácora no se envían.
    scheduler = AsyncIOScheduler()
    scheduler.add_job(notify_upcoming_appointments_job, "interval", minutes=15)
    scheduler.add_job(send_daily_bitacora_reminder_job, "cron", hour=9, minute=0)
    scheduler.start()
    yield
    scheduler.shutdown()


container = Container()

app = FastAPI(title="salud-prenatal · transaccional", lifespan=lifespan)
app.container = container

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

# Mismos prefijos que el monolito: /api/v1/...
for r in (
    appointment_router,
    chat_router,
    consultation_router,
    medical_record_router,
    patient_diary_router,
    profiles_router,
    groups_router,
    posts_router,
    reports_router,
    notification_router,
):
    app.include_router(r, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok", "service": "transaccional"}
