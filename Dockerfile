FROM python:3.11-slim

WORKDIR /app

# Copiar requerimientos
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el codigo fuente
COPY . .

# Exponer el puerto
EXPOSE 8000

# Comando para iniciar el servicio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
