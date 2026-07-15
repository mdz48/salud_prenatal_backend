"""service_pagos — placeholder (Sesión 0).

Se llenará en la Sesión 3 con la feature `subscriptions` (Stripe): checkout,
portal, webhook y consulta de suscripción. Corte más limpio: sin deps internas.
"""
from fastapi import FastAPI

app = FastAPI(title="salud-prenatal · pagos")


@app.get("/health")
def health():
    return {"status": "ok", "service": "pagos"}
