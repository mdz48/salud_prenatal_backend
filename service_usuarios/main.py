"""service_usuarios — placeholder (Sesión 0).

Se llenará en la Sesión 4 con la feature `users` (CRUD de usuarios, doctores,
pacientes, recepcionistas, invitaciones), SIN el login (eso vive en service_auth).
"""
from fastapi import FastAPI

app = FastAPI(title="salud-prenatal · usuarios")


@app.get("/health")
def health():
    return {"status": "ok", "service": "usuarios"}
