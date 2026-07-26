# Métodos de pago

**Ubicación:** `service_pagos/`

Integración con **Stripe** para suscripciones de doctores, con dos modalidades de cobro y soporte para métodos de pago locales de México.

## Métodos soportados

| Método | Modo de Stripe | Renovación | Notas |
|---|---|---|---|
| **Tarjeta (recurrente)** | `subscription` | Automática | Renovación gestionada por Stripe |
| **Tarjeta (pago único)** | `payment` | Manual | Añade 30 días de vigencia |
| **OXXO** | `payment` | Manual | Pago en efectivo en tienda |
| **SPEI** | `payment` (`customer_balance`, `mx_bank_transfer`) | Manual | Transferencia bancaria mexicana |

La elección se resuelve con el **patrón Strategy** en [`stripe_checkout_strategies.py`](../service_pagos/app/subscriptions/infrastructure/adapters/stripe_checkout_strategies.py):

- `StripeRecurringCheckoutStrategy` — crea una sesión `mode="subscription"`.
- `StripeOneTimeCheckoutStrategy` — crea una sesión `mode="payment"` con `payment_method_types=["card", "oxxo", "customer_balance"]`. Para SPEI, Stripe exige un `Customer` explícito, por lo que la estrategia lo crea antes si aún no existe.

Ambas implementan el mismo puerto `ICheckoutStrategy` de [`domain/ports.py`](../service_pagos/app/subscriptions/domain/ports.py): añadir un método de pago nuevo es añadir una estrategia, no modificar el caso de uso.

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/v1/subscriptions/checkout-session` | Crea la sesión de pago (recurrente o único) |
| `POST` | `/api/v1/subscriptions/portal-session` | Abre el portal de facturación de Stripe |
| `GET` | `/api/v1/subscriptions/me` | Suscripción actual del doctor |
| `GET` | `/api/v1/subscriptions/payments` | Historial de pagos |
| `POST` | `/api/v1/subscriptions/webhook` | Receptor de eventos de Stripe |

## Webhook e idempotencia

Stripe reintenta los webhooks. Sin protección, un reintento de `one_time_payment_succeeded` sumaría 30 días de vigencia dos veces.

La solución es un **libro mayor de transacciones de pago**: `HandlePaymentEventUseCase` ([`handle_payment_event_usecase.py`](../service_pagos/app/subscriptions/application/handle_payment_event_usecase.py)) consulta `exists_by_event_id` antes de aplicar cualquier efecto. Si el evento ya fue procesado, la operación es un no-op. La tabla vive en [`payment_transaction_model.py`](../service_pagos/app/subscriptions/infrastructure/models/payment_transaction_model.py) y sirve además como historial consultable por el usuario.

El webhook verifica la firma del payload con `STRIPE_WEBHOOK_SECRET`, que es lo que garantiza que el evento viene realmente de Stripe. Por eso esa ruta pasa por `jwt-auth` y no por `jwt-strict`: Stripe no envía nuestro JWT.

## Discriminador para el cliente

`GET /subscriptions/me` expone el campo `auto_renewal` (verdadero si existe una suscripción de Stripe). El frontend lo usa para decidir qué ofrecer: **portal de facturación** si la suscripción es recurrente, o **un nuevo checkout** si el usuario pagó una sola vez con OXXO o SPEI.

## Estado de la suscripción en el JWT

El estado de suscripción viaja en el token y el gateway lo propaga como `X-Subscription-Status` y `X-Subscription-Period-End`. Así, los demás servicios pueden restringir funcionalidad de pago sin consultar al servicio de pagos en cada petición.

## Variables de entorno

`STRIPE_PRIVATE_KEY`, `STRIPE_PUBLIC_KEY`, `STRIPE_WEBHOOK_SECRET`, `FRONTEND_URL`, y los cuatro identificadores de precio: `STRIPE_PRICE_ID_BASIC` / `_PREMIUM` (recurrentes) y `STRIPE_PRICE_ID_BASIC_ONETIME` / `_PREMIUM_ONETIME` (pago único, OXXO y SPEI). Ver [`.env.example`](../.env.example).

---

Ver también: [gateway](gateway.md) · [cifrado en reposo](cifrado-en-reposo.md) · [integración frontend OXXO/SPEI](integracion_frontend_oxxo_spei.md) · [suscripciones](suscripciones_doctores_stripe.md)
