"""Auth para endpoints server-to-server (llamados por otros microservicios, no por
usuarios finales).

El catch-all de Traefik para transaccional (`PathPrefix('/api/v1')`) usa jwt-auth
(valida-si-viene: anónimo pasa con identidad vacía), no jwt-strict. Un endpoint
interno bajo ese prefijo es alcanzable públicamente aunque solo lo llame otro
servicio dentro de la red del compose, así que no puede confiar solo en la
topología de red: necesita su propio secreto compartido.

INTERNAL_SERVICE_TOKEN vive en el `.env` compartido por los 4 servicios.
"""
import os

from fastapi import Header, HTTPException, status

HEADER_INTERNAL_TOKEN = "X-Internal-Token"


def verify_internal_service_token(
    x_internal_token: str = Header(default=None, alias=HEADER_INTERNAL_TOKEN),
) -> None:
    expected = os.getenv("INTERNAL_SERVICE_TOKEN")
    if not expected or x_internal_token != expected:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid internal service token",
        )
