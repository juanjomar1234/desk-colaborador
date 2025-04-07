#!/bin/bash

# Script para desplegar la aplicación en producción

echo "=== Iniciando despliegue de la aplicación de microservicios ==="

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "Docker no está instalado. Por favor, instale Docker antes de continuar."
    exit 1
fi

# Verificar si Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose no está instalado. Por favor, instale Docker Compose antes de continuar."
    exit 1
fi

# Construir y levantar los contenedores en modo producción
echo "Construyendo y desplegando los servicios..."
docker-compose -f docker-compose.prod.yml up -d --build

# Verificar que los servicios estén funcionando
echo "Verificando que los servicios estén funcionando..."
sleep 5

AUTH_SERVICE_RUNNING=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 || echo "0")
FRONTEND_SERVICE_RUNNING=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001 || echo "0")

if [ "$AUTH_SERVICE_RUNNING" != "0" ] && [ "$FRONTEND_SERVICE_RUNNING" != "0" ]; then
    echo "¡Despliegue exitoso! Los servicios están funcionando correctamente."
    echo "- Auth Service: http://localhost:5000"
    echo "- Frontend Service: http://localhost:5001"
else
    echo "Error: Uno o ambos servicios no están funcionando correctamente."
    echo "- Auth Service status: $AUTH_SERVICE_RUNNING"
    echo "- Frontend Service status: $FRONTEND_SERVICE_RUNNING"
    echo "Revise los logs para más información:"
    echo "docker-compose -f docker-compose.prod.yml logs"
fi

echo "=== Despliegue completado ==="
