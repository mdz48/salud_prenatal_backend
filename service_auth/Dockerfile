# service_auth — Dockerfile (scaffold, Sesión 0)
# Build context = raíz del monorepo (ver docker-compose.yml) para poder copiar shared_core/.
FROM python:3.11-slim
WORKDIR /app

# Sesión 1+: instalar shared_core como paquete común
# COPY shared_core/ /shared_core/
# RUN pip install --no-cache-dir -e /shared_core

COPY service_auth/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY service_auth/ .

EXPOSE 8001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
