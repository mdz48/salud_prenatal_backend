from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import engine, Base
from app.features.users.routes.user_router import router as user_router
from app.features.users.routes.patient_router import router as patient_router
from app.features.users.routes.doctor_router import router as doctor_router
from app.features.appointments.routes.appointment_router import router as appointment_router

app = FastAPI()
app.include_router(user_router, prefix="/api/v1")
app.include_router(patient_router, prefix="/api/v1")
app.include_router(doctor_router, prefix="/api/v1")
app.include_router(appointment_router, prefix="/api/v1")

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