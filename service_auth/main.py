"""service_auth — placeholder (Sesión 0).

Se llenará en la Sesión 5 con el login y la emisión de JWT (hoy en
app/features/users/application/auth). Por ahora solo expone /health para
validar el scaffold y docker-compose.
"""
from fastapi import FastAPI

app = FastAPI(title="salud-prenatal · auth")


@app.get("/health")
def health():
    return {"status": "ok", "service": "auth"}
