from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.database import engine, Base
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
from app.features.notifications.infrastructure.routes.notification_router import router as notification_router
from app.features.notifications.application.tasks import notify_upcoming_appointments_job, send_daily_bitacora_reminder_job
from app.core.containers import Container

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start APScheduler to check upcoming appointments
    scheduler = AsyncIOScheduler()
    scheduler.add_job(notify_upcoming_appointments_job, 'interval', minutes=15)
    scheduler.add_job(send_daily_bitacora_reminder_job, 'cron', hour=9, minute=0)
    scheduler.start()
    yield
    # Shutdown: Cleanly shut down scheduler
    scheduler.shutdown()

container = Container()
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
app.include_router(notification_router, prefix="/api/v1")

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

Base.metadata.create_all(bind=engine)