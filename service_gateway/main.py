import json
import os
import asyncio
from urllib.parse import urlsplit
import httpx
import websockets
from fastapi import FastAPI, Request, Response, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

load_dotenv()

from salud_prenatal_shared_core.auth_dependencies import principal_from_token

app = FastAPI(title="salud-prenatal · API Gateway", docs_url=None) # Desactivar docs por defecto

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROXY_URL = os.getenv("PROXY_URL")

# URLs internas de cada servicio. En docker-compose se resuelven por NOMBRE de
# servicio (auth, usuarios, pagos, transaccional) dentro de la red del compose;
# desde el contenedor del gateway "localhost" apuntaría a sí mismo, no a los otros.
# Para correr el gateway en local (fuera de docker) exporta las *_URL a localhost.
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
    {"url": "/openapi.json", "name": "Gateway (solo el proxy)"},
]


@app.get("/docs", include_in_schema=False)
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

@app.get("/api/v1/{service}/openapi.json", include_in_schema=False)
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
    except Exception as e:
        pass
    raise HTTPException(status_code=503, detail=f"Could not retrieve openapi for {service}")

def get_target_url(path: str) -> str:
    if PROXY_URL:
        return f"{PROXY_URL.rstrip('/')}/{path.lstrip('/')}"

    path_lower = path.lower()
    if "users/login" in path_lower or "users/refresh" in path_lower:
        base = SERVICE_URLS["auth"]
    elif "users" in path_lower or "doctors" in path_lower or "patients" in path_lower or "receptionists" in path_lower:
        base = SERVICE_URLS["usuarios"]
    elif "subscriptions" in path_lower:
        base = SERVICE_URLS["pagos"]
    else:
        base = SERVICE_URLS["transaccional"]
    return f"{base}/{path.lstrip('/')}"

async_client = httpx.AsyncClient()

@app.websocket("/api/v1/chat/ws")
async def websocket_proxy(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    principal = principal_from_token(token)
    if not principal:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()

    if PROXY_URL:
        ws_base = PROXY_URL.replace("http://", "ws://").replace("https://", "wss://")
        target_ws_url = f"{ws_base.rstrip('/')}/api/v1/chat/ws?token={token}"
    else:
        tx_ws = SERVICE_URLS["transaccional"].replace("http://", "ws://").replace("https://", "wss://")
        target_ws_url = f"{tx_ws}/api/v1/chat/ws?token={token}"

    try:
        async with websockets.connect(target_ws_url) as target_ws:
            async def forward_to_client():
                try:
                    async for message in target_ws:
                        await websocket.send_text(message)
                except Exception:
                    pass

            async def forward_to_target():
                try:
                    while True:
                        data = await websocket.receive()
                        if "text" in data:
                            await target_ws.send(data["text"])
                        elif "bytes" in data:
                            await target_ws.send(data["bytes"])
                except WebSocketDisconnect:
                    pass
                except Exception:
                    pass

            await asyncio.gather(forward_to_client(), forward_to_target())
    except Exception:
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def gateway_proxy(request: Request, path: str):
    if path == "health" or path == "":
        return {"status": "ok", "service": "gateway"}

    # Auth Checker: si viene token, se valida aquí y se corta en seco si es
    # inválido (falla rápido, sin gastar un round-trip al servicio destino).
    # Si NO viene token, se deja pasar: la autorización real (qué rutas son
    # públicas y cuáles requieren rol/sesión) ya vive en cada servicio, vía
    # RoleChecker/get_current_user — igual que en el monolito. Mantener aquí
    # una lista de "rutas públicas" duplicaba esa decisión y se desincronizaba
    # (rompía /doctors/register, /patients/register, etc., que nunca requirieron
    # auth). El gateway solo garantiza que un token, SI se presenta, sea legítimo.
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        principal = principal_from_token(token)
        if not principal:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    target_url = get_target_url(path)

    headers = dict(request.headers)
    headers.pop("host", None)

    body = await request.body()
    params = dict(request.query_params)

    try:
        response = await async_client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            params=params,
            content=body,
            timeout=30.0,
        )
        resp_headers = dict(response.headers)
        # Reescribir el header Location de los redirects. FastAPI redirige las rutas
        # de colección sin "/" final (p.ej. GET /api/v1/users -> 307 /api/v1/users/),
        # y el servicio interno pone Location: http://usuarios:8002/api/v1/users/ (host
        # interno de Docker, inalcanzable desde el navegador). Se deja solo el path
        # (relativo al dominio público) para que el redirect funcione tras el gateway.
        location = resp_headers.get("location")
        if location:
            parts = urlsplit(location)
            if parts.netloc:  # es absoluta (tiene host) -> volverla relativa
                resp_headers["location"] = parts.path + (f"?{parts.query}" if parts.query else "")
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=resp_headers,
        )
    except httpx.ConnectError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unavailable",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gateway error: {str(e)}",
        )
