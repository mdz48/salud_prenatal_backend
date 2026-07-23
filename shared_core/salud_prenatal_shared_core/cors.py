"""Origenes CORS permitidos para los 5 servicios.

Ninguno de estos servicios tiene un cliente browser legítimo: el consumidor
es la app móvil (no manda header `Origin`, CORS no le aplica) o admin_backend,
que vive en un repo/deploy separado y no llama a estos servicios directamente.
Por eso no hay ningún origen que permitir -- lista vacía, fallo cerrado fijo.

`allow_origins=["*"]` junto con `allow_credentials=True` expondría cualquier
request autenticada (Authorization: Bearer) a un origen arbitrario -- el
navegador no bloquea la respuesta porque Starlette refleja el Origin pedido
en vez de mandar literalmente "*" cuando allow_credentials=True.
"""


def get_cors_origins() -> list[str]:
    return []
