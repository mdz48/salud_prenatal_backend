"""service_transaccional — placeholder (Sesión 0).

Se llenará en la Sesión 6 con 7 features: appointments, consultations,
medical_record, patient_diaries, forums, chat y notifications. Es el servicio
más grande; concentra el grafo interno de adapters (quedan en-proceso).
"""
from fastapi import FastAPI

app = FastAPI(title="salud-prenatal · transaccional")


@app.get("/health")
def health():
    return {"status": "ok", "service": "transaccional"}
