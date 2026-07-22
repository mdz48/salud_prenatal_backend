"""salud-prenatal · Gateway = backend ForwardAuth de Traefik + docs agregadas.

Este servicio YA NO proxea tráfico. Traefik es el edge (enruta, hace TLS y
proxya el WebSocket del chat nativo); antes de enrutar cada request llama aquí:

- GET /validate         -> valida-si-viene: anónimo pasa con identidad vacía.
- GET /validate/strict  -> fail-closed: anónimo = 401 (prefijos 100% protegidos).

Si el token es válido, la respuesta lleva los headers X-User-* y Traefik los
copia al request (authResponseHeaders) BORRANDO los que trajera el cliente.
Los servicios reconstruyen el Principal desde esos headers (shared_core) y
nunca decodifican JWT. Además este servicio conserva la agregación del Swagger
multi-spec en /docs (slice docs_aggregation).
"""
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from salud_prenatal_shared_core.cors import get_cors_origins
from features.jwt_validation.router import router as jwt_validation_router
from features.docs_aggregation.router import router as docs_router

app = FastAPI(title="salud-prenatal · API Gateway (ForwardAuth)", docs_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jwt_validation_router)
app.include_router(docs_router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "gateway"}


@app.get("/")
def root():
    return {
        "service": "salud-prenatal · API Gateway",
        "role": "forwardauth",
        "note": "Traefik enruta; este servicio solo valida JWTs (una vez, en el edge) y agrega /docs.",
    }
