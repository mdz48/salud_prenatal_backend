"""Slice de agregación de documentación: el Swagger multi-spec del sistema.

Movido tal cual del gateway-proxy anterior: un HTML propio con el dropdown
multi-spec (StandaloneLayout) + passthrough de los openapi.json de cada
servicio con el campo `servers` reescrito a "/" para que el try-it-out salga
por el edge (Traefik) y gane identidad vía ForwardAuth.
"""
import json
import os

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

router = APIRouter()

# URLs internas de cada servicio. En docker-compose se resuelven por NOMBRE de
# servicio dentro de la red del compose; para correr el gateway en local (fuera
# de docker) exporta las *_URL a localhost.
SERVICE_URLS = {
    "auth": os.getenv("AUTH_URL", "http://auth:8001"),
    "usuarios": os.getenv("USUARIOS_URL", "http://usuarios:8002"),
    "pagos": os.getenv("PAGOS_URL", "http://pagos:8003"),
    "transaccional": os.getenv("TRANSACCIONAL_URL", "http://transaccional:8004"),
}

# Selector de specs para el Swagger del gateway. NO se usa fastapi.openapi.docs.
# get_swagger_ui_html: siempre inyecta un `url: '<openapi_url>'` (singular) fijo en
# el JS, y combinado con `swagger_ui_parameters={"urls": [...]}` (plural, para el
# dropdown multi-spec) Swagger UI v5 recibe una config contradictoria y no renderiza
# nada (pantalla en blanco). Con HTML propio solo emitimos `urls`.
_SWAGGER_SPECS = [
    {"url": "/api/v1/usuarios/openapi.json", "name": "Usuarios"},
    {"url": "/api/v1/pagos/openapi.json", "name": "Pagos"},
    {"url": "/api/v1/transaccional/openapi.json", "name": "Transaccional"},
    {"url": "/api/v1/auth/openapi.json", "name": "Auth"},
    {"url": "/openapi.json", "name": "Gateway (validador)"},
]


@router.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    # El dropdown multi-spec (`urls`) es una feature del StandaloneLayout, que vive
    # en el bundle "standalone-preset". Hay que cargar ESE script además del bundle
    # normal y usar layout:"StandaloneLayout" + SwaggerUIStandalonePreset (global).
    # Si falta, Swagger no encuentra definición y muestra "No API definition provided".
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link type="text/css" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
<link rel="shortcut icon" href="https://fastapi.tiangolo.com/img/favicon.png">
<title>salud-prenatal · API Gateway Docs</title>
</head>
<body>
<div id="swagger-ui"></div>
<script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
<script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-standalone-preset.js"></script>
<script>
const ui = SwaggerUIBundle({{
    urls: {json.dumps(_SWAGGER_SPECS)},
    "urls.primaryName": "Usuarios",
    dom_id: "#swagger-ui",
    deepLinking: true,
    presets: [SwaggerUIBundle.presets.apis, SwaggerUIStandalonePreset],
    layout: "StandaloneLayout",
}});
</script>
</body>
</html>"""
    return HTMLResponse(html)


@router.get("/api/v1/{service}/openapi.json", include_in_schema=False)
async def get_service_openapi(service: str):
    base = SERVICE_URLS.get(service)
    if not base:
        raise HTTPException(status_code=404, detail="Service not found")

    url = f"{base}/openapi.json"
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url)
            if res.status_code == 200:
                openapi_data = res.json()
                openapi_data["servers"] = [{"url": "/"}]
                return openapi_data
    except Exception:
        pass
    raise HTTPException(status_code=503, detail=f"Could not retrieve openapi for {service}")
