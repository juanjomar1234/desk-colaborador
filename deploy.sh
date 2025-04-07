#!/bin/bash

echo "=== Iniciando despliegue de la aplicación de microservicios ==="

# Activar entorno virtual en producción
source /path/to/venv/bin/activate

# Instalar/actualizar dependencias
pip install -r requirements.txt

# Reiniciar servicios con gunicorn
echo "Deteniendo servicios anteriores..."
pkill -f gunicorn || true  # No fallar si no hay procesos

echo "Iniciando servicios..."
gunicorn auth_service.wsgi:app -b 0.0.0.0:8000 -D
gunicorn frontend_service.wsgi:app -b 0.0.0.0:8001 -D

# Verificar que los servicios estén funcionando
echo "Verificando servicios..."
sleep 5

AUTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000 || echo "0")
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001 || echo "0")

echo "Estado de los servicios:"
echo "- Auth Service (8000): $AUTH_STATUS"
echo "- Frontend Service (8001): $FRONTEND_STATUS"

echo "=== Despliegue completado ==="
