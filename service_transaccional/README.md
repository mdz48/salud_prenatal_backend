# service_transaccional (:8004)

Servicio **transaccional** — el más grande. Absorbe 7 features:
`appointments`, `consultations`, `medical_record`, `patient_diaries`, `forums`,
`chat`, `notifications`.

- Se llena en la **Sesión 6**.
- Adapters entre estas features quedan **en-proceso** (mismo servicio) → sin cambios.
- Adapters que cruzaban a `users` → lectura directa a la DB compartida (modelos propios).
- Estado de suscripción (ad eligibility) → claim del JWT.
- Integraciones externas ML/NLP (`ML_SERVICE_URL`) → siguen como HTTP.

Placeholder actual: solo `GET /health`.
