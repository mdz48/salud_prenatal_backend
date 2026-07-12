from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import get_engine, Base
from app.features.users.infrastructure.routes.user_router import router as user_router
from app.features.users.infrastructure.routes.patient_router import router as patient_router
from app.features.users.infrastructure.routes.doctor_router import router as doctor_router
from app.features.appointments.infrastructure.routes.appointment_router import router as appointment_router
from app.features.consultations.infrastructure.routes.consultation_router import router as consultation_router
from app.features.medical_record.infrastructure.routes.medical_record_router import router as medical_record_router
from app.features.patient_diaries.infrastructure.routes.patient_diary_router import router as patient_diary_router
from app.features.chat.infrastructure.routes.chat_router import router as chat_router
from app.features.forums.infrastructure.routes.profiles_router import router as profiles_router
from app.features.forums.infrastructure.routes.groups_router import router as groups_router
from app.features.forums.infrastructure.routes.posts_router import router as posts_router
from app.features.forums.infrastructure.routes.reports_router import router as reports_router
from app.features.subscriptions.infrastructure.routes.subscription_router import router as subscription_router
from app.core.containers import Container
from app.core.error_handlers import register_exception_handlers

container = Container()
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # El wiring lo declara Container.wiring_config; aqui solo se inicializa el esquema.
    Base.metadata.create_all(bind=get_engine())
    yield

app = FastAPI(lifespan=lifespan)
app.container = container
app.include_router(user_router, prefix="/api/v1")
app.include_router(patient_router, prefix="/api/v1")
app.include_router(doctor_router, prefix="/api/v1")
app.include_router(appointment_router, prefix="/api/v1")
app.include_router(consultation_router, prefix="/api/v1")
app.include_router(medical_record_router, prefix="/api/v1")
app.include_router(patient_diary_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(profiles_router, prefix="/api/v1")
app.include_router(groups_router, prefix="/api/v1")
app.include_router(posts_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")
app.include_router(subscription_router, prefix="/api/v1")

register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}