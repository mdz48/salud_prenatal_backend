# service_pagos (:8003)

Servicio de **pagos / suscripciones** (Stripe). El corte más limpio: sin
dependencias internas de salida.

- Se llena en la **Sesión 3** con `app/features/subscriptions`.
- Rutas: `POST /subscriptions/checkout-session`, `POST /subscriptions/portal-session`,
  `GET /subscriptions/me` (doctor), `POST /subscriptions/webhook` (sin auth, firma Stripe).
- Env propio: `STRIPE_*`, `FRONTEND_URL` (además de DB + SECRET_KEY + ENCRYPTION_KEY comunes).

Placeholder actual: solo `GET /health`.
