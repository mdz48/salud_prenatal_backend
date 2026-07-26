# service_transaccional — Dockerfile (Sesión 7).
# El build context es la RAÍZ del monorepo (ver docker-compose.yml) para poder
# copiar shared_core/ y el propio servicio.
FROM python:3.11-slim
WORKDIR /app

# shared_core: paquete común (Base/ReadModelBase, seguridad JWT, cripto, enums…).
COPY shared_core/ /shared_core/
RUN pip install --no-cache-dir /shared_core

# Deps del servicio
COPY service_transaccional/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código del servicio
COPY service_transaccional/ .

EXPOSE 8004
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]
