# Gateway — autenticación en el edge

**Ubicación:** `service_gateway/` · Configuración de enrutado: [`docker-compose.yml`](../docker-compose.yml)

El gateway **no** es un proxy inverso. Traefik hace el enrutado; el gateway solo responde una pregunta: *¿esta petición trae una identidad válida?*

## Archivos clave

| Archivo | Qué hace |
|---|---|
| [`features/jwt_validation/router.py`](../service_gateway/features/jwt_validation/router.py) | Endpoints `/validate` y `/validate/strict` que Traefik consulta |
| [`features/jwt_validation/service.py`](../service_gateway/features/jwt_validation/service.py) | Resuelve el `Principal` desde el token y construye las cabeceras de identidad |
| [`features/jwt_validation/ports.py`](../service_gateway/features/jwt_validation/ports.py) | Puerto del verificador de tokens |
| [`features/docs_aggregation/router.py`](../service_gateway/features/docs_aggregation/router.py) | Reúne el `openapi.json` de los cinco servicios en un solo Swagger |
| [`docker-compose.yml`](../docker-compose.yml) | Define los middlewares `jwt-auth` / `jwt-strict` y las reglas de enrutado |

## Cómo funciona

1. Llega una petición a Traefik (`:8000`).
2. Antes de enrutar, Traefik llama al gateway (*ForwardAuth*).
3. El gateway decodifica el JWT con las llaves obtenidas de **Vault** y responde:
   - **200** con las cabeceras `X-User-Id`, `X-User-Email`, `X-User-Role`, `X-Subscription-Status`, `X-Subscription-Period-End`.
   - **401** si el token es inválido o expiró — la petición muere en el edge y nunca toca el servicio.
4. Traefik copia esas cabeceras al request y **descarta** las que hubiera enviado el cliente (`authResponseHeaders`), de modo que no se pueden falsificar desde fuera.
5. El servicio destino llama a `principal_from_headers(request.headers)` y obtiene un `Principal`.

Los servicios de negocio nunca decodifican tokens ni consultan la base de datos para saber quién es el usuario.

## Dos middlewares, dos políticas

| Middleware | Comportamiento | Se usa en |
|---|---|---|
| `jwt-auth` | *Valida si viene.* El anónimo pasa con identidad vacía; el token inválido devuelve 401. | Prefijos donde conviven rutas públicas y protegidas (`/users`, `/doctors`, `/patients`, foros, citas, expediente) |
| `jwt-strict` | *Fail-closed.* El anónimo recibe 401 en el edge. | Prefijos 100 % protegidos (`/chat`, `/subscriptions`, `/users/refresh`) |

**Excepción deliberada:** el webhook de Stripe (`/api/v1/subscriptions/webhook`) usa `jwt-auth` y no `jwt-strict`, porque Stripe no envía nuestro JWT. Esa ruta se protege con la verificación de firma del payload, no con identidad de usuario.

## Autorización dentro del servicio

Validar la identidad no es autorizar. Una vez que el servicio tiene su `Principal`, el control de acceso por rol lo aplica `RoleChecker` de [`auth_dependencies.py`](../shared_core/salud_prenatal_shared_core/auth_dependencies.py):

```python
require_doctor = RoleChecker([RoleEnum.doctor])
```

## Llaves de firma en Vault

La firma del JWT está detrás de un puerto, `IJwtKeyProvider` ([`jwt_key_provider.py`](../shared_core/salud_prenatal_shared_core/jwt_key_provider.py)), con dos implementaciones:

| Backend | Algoritmo | Cuándo |
|---|---|---|
| Env (`SECRET_KEY`) | HS256 simétrico | Desarrollo local y pruebas |
| **Vault** (`JWT_KEY_BACKEND=vault`) | **RS256 asimétrico** | Staging y producción |

`VaultJwtKeyProvider` ([`vault_jwt_key_provider.py`](../shared_core/salud_prenatal_shared_core/vault_jwt_key_provider.py)) se autentica por AppRole, lee el par RSA de `secret/jwt/private` y `secret/jwt/public`, y cachea las llaves en memoria para no consultar Vault en cada petición. Con RS256 solo el servicio `auth` posee la llave privada: el gateway únicamente verifica con la pública.

`get_secret_key()` lanza excepción si `SECRET_KEY` no está configurada — no existe valor por defecto, porque un fallback permitiría a cualquiera falsificar JWTs.

---

Ver también: [cifrado en reposo](cifrado-en-reposo.md) · [métodos de pago](metodos-de-pago.md) · [despliegue con Traefik y Vault](deploy-produccion-traefik-vault.md)
