# Fix CORS wildcard + credenciales (auditoría seguridad)

## Problema detectado

Escaneo con HTTP Toolkit y OWASP ZAP marcó **alto** en los 5 servicios:

```python
allow_origins=["*"]
allow_credentials=True
```

`allow_origins=["*"]` combinado con `allow_credentials=True` es el peor caso posible: Starlette
no puede mandar literalmente `*` cuando hay credenciales (lo prohíbe el spec CORS), así que
**refleja el `Origin` que mandó el cliente** como si fuera válido. Resultado: cualquier request
autenticada (`Authorization: Bearer ...`) hecha desde JS de **cualquier origen** pasa el chequeo
del navegador y puede leer la respuesta.

Esto aplica sin importar que el consumidor real sea una app móvil — el riesgo no es la app,
es cualquier ruta browser hacia el API (docs/Swagger, un webview, XSS en otro sitio con el
token accesible, etc.). El scanner no puede saber la intención de uso, evalúa la política tal
cual queda expuesta.

## Fix — commit `d0e166e` (rama `seguridad`)

Nuevo helper compartido [`shared_core/salud_prenatal_shared_core/cors.py`](../shared_core/salud_prenatal_shared_core/cors.py),
usado por los 5 servicios (`service_auth`, `service_gateway`, `service_pagos`,
`service_transaccional`, `service_usuarios`):

```python
allow_origins=get_cors_origins(),   # antes: ["*"]
allow_credentials=True,
```

## Simplificación posterior

Se confirmó que **ninguno de los 5 servicios tiene consumidor browser legítimo**:

- El cliente real es la app móvil — no manda header `Origin`, CORS no le aplica nunca.
- El panel admin (`admin_backend`) vive en repo/deploy separado, no llama a estos servicios
  directamente, y tiene su propia auth (HS256, `SECRET_KEY` propio, no usa `shared_core`).

Por lo tanto no existe ningún origen real que deba permitirse. `get_cors_origins()` se
simplificó para no depender de variable de entorno — retorna lista vacía fija (fallo cerrado
permanente):

```python
def get_cors_origins() -> list[str]:
    return []
```

Esto también resuelve una colisión de nombre: `service_pagos` ya usaba `FRONTEND_URL` para
construir la URL de callback de Stripe (`saludprenatal://payment-callback`, un deep-link, no un
origen HTTP). Al no leer más esa variable, CORS y Stripe dejan de compartir el mismo nombre de
env var por accidente.

## Pendientes / notas

- **`main.py` / `Dockerfile` en la raíz del repo**: monolito pre-split, todavía con
  `allow_origins=["*"]` hardcodeado. No aparece en ningún `docker-compose*.yml` (solo referencian
  los `service_*/Dockerfile`) y el commit `d0e166e` ya borró el directorio `app/` que este
  archivo importa — quedó con imports rotos. Es código muerto, candidato a eliminar.
- Considerar renombrar `FRONTEND_URL` → `STRIPE_RETURN_URL` en `service_pagos` para que el
  nombre no sugiera relación con CORS (ya no hay colisión funcional, pero sigue siendo confuso).
