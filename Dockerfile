# Usar una imagen base de Python
FROM python:3.13.2-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de requerimientos
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY . .

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Exponer puertos
EXPOSE 8000 8001

# Crear directorio para la base de datos SQLite
RUN mkdir -p /app/instance && \
    chmod 777 /app/instance

# El comando se especifica en docker-compose.yml 