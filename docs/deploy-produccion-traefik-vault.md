# Despliegue a producción — Traefik + ForwardAuth + Vault RS256

Runbook del corte del VPS `saludprenatal.sytes.net`. Reemplaza nginx + gateway-proxy por
Traefik como edge, con validación JWT única (ForwardAuth) y firma RS256 desde Vault.

> **Secuencia elegida:** se corta **directo con Vault (RS256)** — los servicios NUNCA
> corren HS256 en producción (Vault se bootstrapea ANTES de apagar nginx). Cert TLS
> reutilizado de certbot (sin ACME). Rate limit replicado del nginx actual.

> **Vault PERSISTENTE (actualizado):** producción **no** usa `-dev`. Corre con
> `storage "file"` sobre el volumen `vault_data` (config en [`vault/config.hcl`](../vault/config.hcl)),
> así que el par RSA, las políticas y los AppRoles sobreviven a reinicios y reboots.
> A cambio, Vault arranca **sellado**: lo desella el sidecar `vault_unsealer`
> ([`scripts/vault_unseal_loop.sh`](../scripts/vault_unseal_loop.sh)) con la key que
> genera [`scripts/vault_init.sh`](../scripts/vault_init.sh). Esto cierra el punto 1
> del "Nivel B" del spec de diseño.

> ⚠️ **Impacto obligado del corte:** pasar de HS256 a RS256 invalida **todos** los
> tokens vivos. Con `ACCESS_TOKEN_EXPIRE_MINUTES=43200` (30 días), eso es toda la
> base de usuarios de la app móvil: quedan deslogueados y deben volver a iniciar
> sesión. No hay forma de evitarlo cambiando de algoritmo de firma — elegir ventana
> de bajo tráfico y avisar.

---

## EJECUTADO EN PRODUCCIÓN — 2026-07-25

El corte está **hecho**. Producción firma en RS256 con Vault persistente. Lo que sigue
abajo (Fases 1–4) es el procedimiento de referencia; **no hay que volver a correrlo**.

### Estado del que se partió

nginx ya estaba `inactive` y `certbot.timer` `disabled` de cortes anteriores, así que la
**Fase 1 y el paso 3.1 no se ejecutaron**. Solo se hizo la parte de Vault (Fase 2) más la
recreación de `auth` y `gateway`.

No hizo falta `--build`: entre `develop` y `cambiosCompose` el único cambio bajo
`service_*/` fue `service_auth/tests/conftest.py`, y las imágenes ya traían `hvac`.
Importante con 2 GB de RAM libres (`ollama` retiene ~4.5 GB de los 7.8 GB del VPS) —
compilar 5 imágenes era el riesgo real de la ventana.

### Verificación final

| Prueba | Resultado |
|---|---|
| `vault status` | `Storage Type: file`, `Initialized true`, `Sealed false` |
| Login real (`house@hospital.com`) | header `{"alg":"RS256","typ":"JWT"}`, firma de **256 bytes** (RSA-2048; HS256 daría 32) |
| `/subscriptions/me`, `/chat/inbox` con ese token | 200 / 200 |
| Token basura | 401 |
| Anti-spoofing (headers `X-User-*` a mano) | 401 |
| AppRole gateway → `jwt/public` | LEE |
| AppRole gateway → `jwt/private` | **Forbidden** |
| AppRole auth → ambas | LEE |
| `docker restart vault` | sellado → el sidecar desella en ≤10 s, **la API respondió 200 durante todo el proceso** |

Esa última fila es la que valida el cambio a Vault persistente: con dev-mode, ese mismo
reinicio habría perdido las llaves y tumbado `auth` y `gateway`.

### Tres fallos encontrados durante la ejecución

**1. Vault en crash-loop: `bind: address already in use`.**
El compose traía `command: ["server", "-config=/vault/config/config.hcl"]`, pero el
`docker-entrypoint.sh` de la imagen ya añade `-config=/vault/config` (el **directorio**).
Vault cargaba `config.hcl` dos veces → dos bloques `listener` en `:8200`.
Fix: `command: ["server"]` a secas.

**2. `invalid role or secret ID` al hacer login del AppRole.**
El filtro que limpia el `.env` era `^(JWT_KEY_BACKEND|VAULT_ROLE_ID_|VAULT_SECRET_ID_)=`.
Ese `=` final exige `VAULT_ROLE_ID_=`, que **nunca** casa con `VAULT_ROLE_ID_GATEWAY=`, así
que las credenciales de intentos previos sobrevivían y quedaban **dos líneas por variable**;
`$(grep ... | cut ...)` devolvía ambas concatenadas. Fix: quitar el `=` tras los prefijos
(aplicado también en [`scripts/vault_recover.sh`](../scripts/vault_recover.sh)).
Al limpiar el `.env` a mano, **verificar que cada variable aparece una sola vez**.

**3. Falso positivo al comprobar `hvac`.**
`hvac` no expone `__version__`; probarlo así da `AttributeError` y parece que falta la
librería. Comprobar con `import hvac` a secas.

### Estado del VPS tras el corte

- `~/proyectos/.vault-init` (chmod 600) — unseal key + root token. **Si se pierde, el Vault
  sellado es irrecuperable.** No está en git ni en backup: es el único ejemplar.
- Backups: `~/backup-compose-precorte-*.yml`, `~/proyectos/.env.bak-*`.
- Volumen `vault_data`. **Nunca `docker compose down -v`** en este stack: borra el par RSA.

---

## Contexto del VPS (ya verificado 2026-07-17)

- Repo en `~/proyectos/salud_prenatal_backend`, rama `cambiosGateway`. Compose activo en `~/proyectos/`.
- DB = Supabase (vía `.env`). No hay postgres local.
- nginx sirve UN solo sitio (`saludprenatal`) → seguro apagarlo. Red Docker = `proyectos_app_network`.
- Certs de certbot en `/etc/letsencrypt/live/saludprenatal.sytes.net/`.
- Strip de prefijo: `/ml` y `/api/v1/admin` NO recortan; `/admin` SÍ (ya reflejado en el compose).

## Requisitos previos

- SSH al VPS con sudo.
- Docker Engine 29 (ya presente). Traefik v3.7 (el compose lo fija — v3.5 NO sirve con Docker 29).

---

## Fase 1 — Preparación (SIN downtime, nginx sigue sirviendo)

```bash
ssh <vps>
cd ~/proyectos

# 1.1 Backups
cp docker-compose.yml ~/backup-compose-$(date +%F).yml
sudo cp -r /etc/nginx ~/backup-nginx-$(date +%F)

# 1.2 Traer el código
cd salud_prenatal_backend && git fetch && git checkout cambiosGateway && git pull && cd ..

# 1.3 Poner el compose nuevo como activo
cp salud_prenatal_backend/docker-compose.vps.yml ~/proyectos/docker-compose.yml

# 1.4 Construir imágenes nuevas (el stack viejo sigue arriba mientras tanto)
docker compose build
```

## Fase 2 — Init + bootstrap de Vault (SIN downtime todavía)

Vault es interno (sin puertos publicados), así que arrancarlo no interfiere con nginx.

```bash
# 2.0 PRE-REQUISITO: crear el archivo de credenciales VACÍO antes del primer `up`.
#   El sidecar lo monta como bind mount; si no existe, Docker crea un DIRECTORIO
#   con ese nombre y el unsealer entra en crash-loop.
touch ~/proyectos/.vault-init && chmod 600 ~/proyectos/.vault-init

# 2.1 Levantar SOLO Vault (crea la red proyectos_app_network + el contenedor vault).
#   Arranca sin inicializar y sellado: es lo esperado.
docker compose up -d vault
sleep 5
docker exec -e VAULT_ADDR=http://127.0.0.1:8200 vault vault status || true   # Initialized=false, Sealed=true

# 2.2 Inicializar y desellar por primera vez. Escribe la unseal key + el root
#   token en ~/proyectos/.vault-init (chmod 600). CORRE UNA SOLA VEZ.
chmod +x salud_prenatal_backend/scripts/vault_init.sh
./salud_prenatal_backend/scripts/vault_init.sh

# 2.2b Comprobar que Vault arrancó bien ANTES de seguir. Debe decir
#   Storage Type: file / Initialized true / Sealed false, y Restarts=0.
#   Si está en crash-loop con "address already in use", revisa que `command:`
#   sea ["server"] a secas (ver fallo 1 del registro de arriba).
docker inspect -f 'Restarts={{.RestartCount}}' vault
docker exec -e VAULT_ADDR=http://127.0.0.1:8200 vault vault status | grep -E 'Storage|Initialized|Sealed'

# 2.3 Bootstrapear con el ROOT TOKEN recién generado (ya NO es "root" como en
#   dev-mode). Genera par RSA + políticas + AppRoles. Imprime 4 credenciales.
export VAULT_TOKEN=$(grep '^VAULT_ROOT_TOKEN=' ~/proyectos/.vault-init | cut -d= -f2-)
docker run --rm --network proyectos_app_network \
  -e VAULT_ADDR=http://vault:8200 -e VAULT_TOKEN="$VAULT_TOKEN" \
  -v ~/proyectos/salud_prenatal_backend/scripts/vault_bootstrap.py:/b.py \
  python:3.11-slim sh -c "pip install -q hvac cryptography && python /b.py"
unset VAULT_TOKEN
```

Copia del output las 4 credenciales (`VAULT_ROLE_ID_AUTH`, `VAULT_SECRET_ID_AUTH`,
`VAULT_ROLE_ID_GATEWAY`, `VAULT_SECRET_ID_GATEWAY`).

```bash
# 2.4 Escribir las credenciales en el .env DEL PROYECTO.
#   OJO: va en ~/proyectos/.env (donde compose resuelve ${...}), NO en
#   salud_prenatal_backend/.env — ese es el `env_file` y compose no interpola
#   desde ahí. Poner las creds en el archivo equivocado = auth/gateway arrancan
#   con VAULT_ROLE_ID vacío y truenan con RuntimeError.
cat >> ~/proyectos/.env <<'EOF'
JWT_KEY_BACKEND=vault
VAULT_ROLE_ID_AUTH=<pega>
VAULT_SECRET_ID_AUTH=<pega>
VAULT_ROLE_ID_GATEWAY=<pega>
VAULT_SECRET_ID_GATEWAY=<pega>
EOF

# 2.4b Si el .env ya traía creds de un intento previo, quedarán DUPLICADAS y el
#   login del AppRole fallará con "invalid role or secret ID". Verificar 1 por variable:
for v in JWT_KEY_BACKEND VAULT_ROLE_ID_AUTH VAULT_SECRET_ID_AUTH VAULT_ROLE_ID_GATEWAY VAULT_SECRET_ID_GATEWAY; do
  printf '%-26s %s\n' "$v" "$(grep -c "^$v=" ~/proyectos/.env)"
done

# 2.5 Levantar el sidecar que mantiene Vault desellado tras cada reinicio.
docker compose up -d vault_unsealer
docker logs vault_unsealer --tail 5      # "arrancado", sin FATAL
```

> Con esto los servicios arrancarán directo en RS256 — nunca HS256 en prod.
> `JWT_KEY_BACKEND` ya trae default `vault` en el compose; la línea del `.env` lo
> deja explícito y es el interruptor del rollback (ponerla vacía → vuelve a HS256).

## Fase 3 — El corte (ventana corta de downtime)

```bash
# 3.1 Liberar el puerto 80/443 (que certbot no pelee con Traefik)
sudo systemctl disable --now certbot.timer
sudo systemctl stop nginx && sudo systemctl disable nginx

# 3.2 Levantar el stack nuevo COMPLETO.
#   NUNCA uses `docker compose down -v` en este stack: el -v borra el volumen
#   vault_data y con él el par RSA de firma (todos los tokens mueren y hay que
#   re-bootstrapear). `down` a secas SÍ es seguro ahora que Vault es persistente.
#   `up -d` reconcilia: recrea los servicios de la app con la config nueva y
#   --remove-orphans limpia contenedores viejos que no estén en este compose.
docker compose up -d --remove-orphans

# 3.3 Verificar arranque
docker compose ps
docker compose logs traefik | grep -iE 'error|too old'   # no debe haber errores
docker compose logs auth gateway | tail -20              # sin errores de Vault
docker exec -e VAULT_ADDR=http://127.0.0.1:8200 vault vault status | grep -E 'Sealed|Initialized'
#   -> Initialized true / Sealed false. Si dice Sealed true, revisa vault_unsealer:
#      docker logs vault_unsealer --tail 20
```

## Fase 4 — Smoke post-corte

```bash
D=https://saludprenatal.sytes.net

# 4.1 TLS + health (el cert es el mismo de certbot)
curl -vI $D/health 2>&1 | grep -E 'HTTP|issuer|subject'

# 4.2 Login → token RS256
curl -s -X POST $D/api/v1/users/login -H 'Content-Type: application/json' \
  -d '{"email":"<un doctor real>","password":"<pass>"}' -o /tmp/l.json -w 'login %{http_code}\n'
TOKEN=$(python3 -c "import json;print(json.load(open('/tmp/l.json'))['access_token'])")
echo $TOKEN | cut -d. -f1 | base64 -d 2>/dev/null   # el header debe decir "alg":"RS256"

# 4.3 Request protegido (gateway valida con la pública de Vault)
curl -s -o /dev/null -w '/subscriptions/me %{http_code}\n' -H "Authorization: Bearer $TOKEN" $D/api/v1/subscriptions/me

# 4.4 Anti-spoofing (DEBE dar 401)
curl -s -o /dev/null -w 'anti-spoof %{http_code}\n' -H "X-User-Id: 999" -H "X-User-Role: doctor" $D/api/v1/chat/inbox

# 4.5 Token inválido 401; ruta pública sin token no-401
curl -s -o /dev/null -w 'basura %{http_code}\n' -H "Authorization: Bearer basura" $D/api/v1/subscriptions/me
curl -s -o /dev/null -w 'publica %{http_code}\n' $D/api/v1/doctors/1

# 4.6 WebSocket, docs, ml/admin, redirect http→https, webhook Stripe de prueba
#   wss://saludprenatal.sytes.net/api/v1/chat/ws?token=$TOKEN   (con la app o wscat)
curl -s -o /dev/null -w 'docs %{http_code}\n' $D/docs
curl -s -o /dev/null -w 'ml %{http_code}\n'   $D/ml/<ruta-conocida>
curl -s -o /dev/null -w 'admin-api %{http_code}\n' $D/api/v1/admin/<ruta>
curl -s -o /dev/null -w 'admin-front %{http_code}\n' $D/admin/
curl -sI http://saludprenatal.sytes.net/health | grep -i location   # 301/308 a https
```

Monitorear 15-30 min: `docker compose logs -f traefik transaccional`.

## Rollback (si algún smoke falla y no se diagnostica rápido)

```bash
cd ~/proyectos
docker compose down
cp ~/backup-compose-<fecha>.yml docker-compose.yml
cd salud_prenatal_backend && git checkout <commit-previo> && cd ..
docker compose up -d --build
sudo systemctl enable --now nginx
sudo systemctl enable --now certbot.timer
```

Los certs de certbot NUNCA se tocaron → servicio restaurado en minutos.

### Rollback parcial: solo apagar Vault (dejar Traefik)

Si Traefik va bien y el problema es únicamente Vault/RS256:

```bash
cd ~/proyectos
sed -i 's/^JWT_KEY_BACKEND=.*/JWT_KEY_BACKEND=/' .env    # vacío -> EnvJwtKeyProvider (HS256)
grep -q '^SECRET_KEY=' salud_prenatal_backend/.env || echo "FALTA SECRET_KEY -> el rollback NO funciona"
docker compose up -d --force-recreate auth gateway
```

`SECRET_KEY` debe seguir presente en `salud_prenatal_backend/.env`: sin ella
`EnvJwtKeyProvider` lanza `RuntimeError` y el rollback deja el sistema igual de caído.
**No la borres del `.env` al activar Vault** — es justo la red de seguridad.

Ojo: volver a HS256 invalida otra vez todos los tokens RS256 emitidos → segundo
deslogueo masivo. Es un rollback real, no gratis.

## Qué pasa ahora en un reinicio (el caso normal)

Vault persistente + `vault_unsealer`: **no hay que hacer nada**. Al reiniciarse el
contenedor (o el host), Vault vuelve sellado, el sidecar lo detecta en ≤10 s y lo
desella con la key de `~/proyectos/.vault-init`. Las llaves y los AppRoles siguen ahí,
así que las credenciales del `.env` **siguen siendo válidas** y nadie se desloguea.

Durante esos segundos `auth`/`gateway` pueden devolver 500 en las peticiones que
toquen llaves. Es transitorio y se recupera solo: `VaultJwtKeyProvider` solo cachea
tras un éxito, así que reintenta en la siguiente petición sin reiniciar nada.

Verificar salud de Vault en cualquier momento:
```bash
docker exec -e VAULT_ADDR=http://127.0.0.1:8200 vault vault status | grep -E 'Sealed|Initialized'
docker logs vault_unsealer --tail 20
```

## Recuperación (Vault sellado y el sidecar no lo levanta)

**Síntoma:** login falla / rutas protegidas dan 500, y `vault status` dice `Sealed true`.

```bash
cd ~/proyectos
docker logs vault_unsealer --tail 30     # ¿FATAL: falta /vault-init? ¿unseal key mala?

# Desellar a mano con la key guardada
KEY=$(grep '^VAULT_UNSEAL_KEY=' ~/proyectos/.vault-init | cut -d= -f2-)
docker exec -e VAULT_ADDR=http://127.0.0.1:8200 vault vault operator unseal "$KEY"
```

Causa típica: `~/proyectos/.vault-init` se quedó como **directorio** (se levantó el
sidecar antes de crear el archivo). Arreglo: `docker compose stop vault_unsealer`,
`rmdir ~/proyectos/.vault-init`, restaurar el archivo con la key, `up -d vault_unsealer`.

## Recuperación catastrófica (se perdió el volumen `vault_data`)

Solo aplica si alguien corrió `down -v` o borró el volumen. Las llaves ya no existen:
hay que re-inicializar, y el nuevo par RSA **desloguea a todos** otra vez.

```bash
cd ~/proyectos
rm -f ~/proyectos/.vault-init && touch ~/proyectos/.vault-init && chmod 600 ~/proyectos/.vault-init
docker compose up -d vault
./salud_prenatal_backend/scripts/vault_init.sh          # nueva unseal key + root token
export VAULT_TOKEN=$(grep '^VAULT_ROOT_TOKEN=' ~/proyectos/.vault-init | cut -d= -f2-)
docker run --rm --network proyectos_app_network \
  -e VAULT_ADDR=http://vault:8200 -e VAULT_TOKEN="$VAULT_TOKEN" \
  -v ~/proyectos/salud_prenatal_backend/scripts/vault_bootstrap.py:/b.py \
  python:3.11-slim sh -c "pip install -q hvac cryptography && python /b.py"
unset VAULT_TOKEN
nano ~/proyectos/.env                                    # pegar las 4 creds NUEVAS
docker compose up -d --force-recreate auth gateway vault_unsealer
```

**Gotchas:** (1) las creds CAMBIAN en cada re-bootstrap → pegarlas es obligatorio, y van en
`~/proyectos/.env` (donde compose lee `${...}`), NO en `salud_prenatal_backend/.env`.
(2) `scripts/` está gitignoreado (los archivos de Vault se commitearon con `git add -f`) →
mantener copia en el VPS; un `git clean` los borraría y te quedas sin recuperación.
(3) `scripts/vault_recover.sh` es el atajo automatizado de esta sección.

## Limitaciones que SIGUEN abiertas (Nivel B restante)

Cerrado con este corte: ~~Vault en dev-mode / storage volátil~~ → ahora persistente.

Pendiente:
- **Sin TLS hacia Vault** (`http://vault:8200`). Mitigación actual: Vault no publica
  puertos y solo es alcanzable dentro de `app_network`.
- **Unseal key en disco** (`~/proyectos/.vault-init`, chmod 600). Es el mismo problema de
  "secret zero" que el `SECRET_ID` del AppRole. Un auto-unseal real delega el sello a un
  KMS externo (AWS KMS / Vault transit) — infraestructura aparte.
- **Sin renovación automática del token AppRole**: login + caché por vida del proceso.
  No muerde hoy porque las llaves se leen una vez y quedan cacheadas.
- **1 sola unseal key** (`key-shares=1`) en vez de repartir 5/3 entre operadores.

Ver `docs/superpowers/specs/2026-07-17-vault-rs256-jwt-keys-design.md`.
