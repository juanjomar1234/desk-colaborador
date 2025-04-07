#!/bin/bash

echo "=== Iniciando despliegue de la aplicación de microservicios ==="

# Configurar rutas para hosting compartido
DEPLOY_PATH="/home/u396608776/domains/uno14.trading/public_html/portalcolaborador"
VENV_PATH="$DEPLOY_PATH/venv"

# Activar entorno virtual
source $VENV_PATH/bin/activate

# Instalar/actualizar dependencias
pip install -r requirements.txt

# Asegurar permisos correctos
chmod 755 $DEPLOY_PATH
find $DEPLOY_PATH -type d -exec chmod 755 {} \;
find $DEPLOY_PATH -type f -exec chmod 644 {} \;
chmod 755 $DEPLOY_PATH/wsgi.py
chmod 755 $DEPLOY_PATH/frontend_service/wsgi.py
chmod 755 $DEPLOY_PATH/auth_service/wsgi.py

# Reiniciar servicios con gunicorn
echo "Deteniendo servicios anteriores..."
pkill -f gunicorn || true

echo "Iniciando servicios..."
$VENV_PATH/bin/gunicorn auth_service.wsgi:app -b 127.0.0.1:8000 -D --pid $DEPLOY_PATH/auth.pid
$VENV_PATH/bin/gunicorn frontend_service.wsgi:app -b 127.0.0.1:8001 -D --pid $DEPLOY_PATH/frontend.pid

# Verificar que los servicios estén funcionando
echo "Verificando servicios..."
sleep 5

AUTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000 || echo "0")
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001 || echo "0")

echo "Estado de los servicios:"
echo "- Auth Service (8000): $AUTH_STATUS"
echo "- Frontend Service (8001): $FRONTEND_STATUS"

echo "=== Despliegue completado ==="
