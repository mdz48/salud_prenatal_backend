# service_pagos — Dockerfile (scaffold, Sesión 0)
FROM python:3.11-slim
WORKDIR /app

# COPY shared_core/ /shared_core/
# RUN pip install --no-cache-dir -e /shared_core

COPY service_pagos/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY service_pagos/ .

EXPOSE 8003
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
