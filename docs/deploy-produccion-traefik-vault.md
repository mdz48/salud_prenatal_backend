# Despliegue a producción — Traefik + ForwardAuth + Vault RS256

Runbook del corte del VPS `saludprenatal.sytes.net`. Reemplaza nginx + gateway-proxy por
Traefik como edge, con validación JWT única (ForwardAuth) y firma RS256 desde Vault.

> **Secuencia elegida:** se corta **directo con Vault (RS256)** — los servicios NUNCA
> corren HS256 en producción (Vault se bootstrapea ANTES de apagar nginx). Cert TLS
> reutilizado de certbot (sin ACME). Rate limit replicado del nginx actual.

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

## Fase 2 — Bootstrap de Vault (SIN downtime todavía)

Vault es interno (sin puertos publicados), así que arrancarlo no interfiere con nginx.

```bash
# 2.1 Levantar SOLO Vault (crea la red proyectos_app_network + el contenedor vault)
docker compose up -d vault
sleep 5

# 2.2 Bootstrapear Vault con un contenedor python de un solo uso (genera par RSA,
#     políticas, AppRoles). Imprime las credenciales al final.
docker run --rm --network proyectos_app_network \
  -e VAULT_ADDR=http://vault:8200 -e VAULT_TOKEN=root \
  -v ~/proyectos/salud_prenatal_backend/scripts/vault_bootstrap.py:/b.py \
  python:3.11-slim sh -c "pip install -q hvac cryptography && python /b.py"
```

Copia del output las 4 credenciales (`VAULT_ROLE_ID_AUTH`, `VAULT_SECRET_ID_AUTH`,
`VAULT_ROLE_ID_GATEWAY`, `VAULT_SECRET_ID_GATEWAY`).

```bash
# 2.3 Escribir las credenciales + activar el backend Vault en el .env
cat >> salud_prenatal_backend/.env <<'EOF'
JWT_KEY_BACKEND=vault
VAULT_ROLE_ID_AUTH=<pega>
VAULT_SECRET_ID_AUTH=<pega>
VAULT_ROLE_ID_GATEWAY=<pega>
VAULT_SECRET_ID_GATEWAY=<pega>
EOF
```

> Con esto los servicios arrancarán directo en RS256 — nunca HS256 en prod.

## Fase 3 — El corte (ventana corta de downtime)

```bash
# 3.1 Liberar el puerto 80/443 (que certbot no pelee con Traefik)
sudo systemctl disable --now certbot.timer
sudo systemctl stop nginx && sudo systemctl disable nginx

# 3.2 Levantar el stack nuevo COMPLETO.
#   OJO: NO uses `docker compose down` — mataría el Vault dev-mode que ya
#   bootstrapeaste en la Fase 2 (perdería las llaves y las creds del .env quedarían
#   inválidas). `up -d` reconcilia: recrea los servicios de la app con la config nueva,
#   deja el vault ya corriendo intacto, y --remove-orphans limpia contenedores viejos
#   que no estén en este compose (p. ej. el monolito).
docker compose up -d --remove-orphans

# 3.3 Verificar arranque
docker compose ps
docker compose logs traefik | grep -iE 'error|too old'   # no debe haber errores
docker compose logs auth gateway | tail -20              # sin errores de Vault
docker compose ps vault                                  # vault DEBE seguir Up (no recreado)
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

## Limitación conocida (registrada)

Vault corre en **modo dev**: si el contenedor `vault` se reinicia, pierde las llaves y los
AppRoles → auth/gateway no pueden firmar/validar hasta re-bootstrapear. Aceptado para esta
entrega (Nivel A). El endurecimiento (Vault persistente + TLS + renovación de token) es el
Nivel B, diferido — ver `docs/superpowers/specs/2026-07-17-vault-rs256-jwt-keys-design.md`.

## Recuperación ante reinicio de Vault (dev-mode)

**Síntoma:** login falla / rutas protegidas dan 500. **Confirmar:**
```bash
docker compose ps vault              # uptime bajo = se reinició
docker logs sp_auth 2>&1 | tail -10  # errores de Vault al firmar
```

**Recuperación:**
```bash
cd ~/proyectos

# 1. Re-bootstrap (nuevo par RSA + AppRoles). Imprime 4 credenciales NUEVAS.
docker run --rm --network proyectos_app_network \
  -e VAULT_ADDR=http://vault:8200 -e VAULT_TOKEN=root \
  -v ~/proyectos/salud_prenatal_backend/scripts/vault_bootstrap.py:/b.py \
  python:3.11-slim sh -c "pip install -q hvac cryptography && python /b.py"

# 2. Pegar las 4 creds nuevas en ~/proyectos/.env (el del PROYECTO, no el env_file)
nano ~/proyectos/.env   # VAULT_ROLE_ID_AUTH/SECRET_ID_AUTH, VAULT_ROLE_ID_GATEWAY/SECRET_ID_GATEWAY

# 3. Recrear auth + gateway
docker compose up -d --force-recreate auth gateway

# 4. Verificar (el token debe ser alg:RS256)
curl -s -X POST https://saludprenatal.sytes.net/api/v1/users/login \
  -H 'Content-Type: application/json' -d '{"email":"<doctor>","password":"<pass>"}'
```

**Gotchas:** (1) las creds CAMBIAN en cada re-bootstrap → el paso 2 es obligatorio, y va en
`~/proyectos/.env` (donde compose lee `${...}`), NO en `salud_prenatal_backend/.env`.
(2) `scripts/vault_bootstrap.py` está gitignoreado → mantener una copia en el VPS; un
`git clean`/`checkout` lo borraría y te quedas sin recuperación.
