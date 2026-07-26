FROM python:3.11-slim
WORKDIR /app

COPY shared_core/ /shared_core/
RUN pip install --no-cache-dir /shared_core

COPY service_gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY service_gateway/ .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
