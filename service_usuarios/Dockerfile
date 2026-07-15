# service_usuarios — Dockerfile (scaffold, Sesión 0)
FROM python:3.11-slim
WORKDIR /app

# COPY shared_core/ /shared_core/
# RUN pip install --no-cache-dir -e /shared_core

COPY service_usuarios/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY service_usuarios/ .

EXPOSE 8002
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
