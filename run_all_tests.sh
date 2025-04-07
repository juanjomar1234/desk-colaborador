#!/bin/bash

# Script para ejecutar todas las pruebas de la aplicación

echo "=== Iniciando pruebas completas de la aplicación de microservicios ==="

# Verificar si los servicios están en ejecución
echo "Verificando servicios..."
AUTH_SERVICE_RUNNING=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 || echo "0")
FRONTEND_SERVICE_RUNNING=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001 || echo "0")

if [ "$AUTH_SERVICE_RUNNING" = "0" ] || [ "$FRONTEND_SERVICE_RUNNING" = "0" ]; then
    echo "Los servicios no están en ejecución. Iniciando servicios..."
    
    # Iniciar servicios en terminales separados
    echo "Iniciando auth-service en puerto 5000..."
    cd /home/ubuntu/microservices-app/auth-service && python3 run.py &
    AUTH_PID=$!
    
    # Esperar a que el servicio de autenticación esté disponible
    echo "Esperando a que auth-service esté disponible..."
    while [ "$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 || echo "0")" = "0" ]; do
        sleep 1
    done
    
    echo "Iniciando frontend-service en puerto 5001..."
    cd /home/ubuntu/microservices-app/frontend-service && python3 run.py &
    FRONTEND_PID=$!
    
    # Esperar a que el servicio frontend esté disponible
    echo "Esperando a que frontend-service esté disponible..."
    while [ "$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001 || echo "0")" = "0" ]; do
        sleep 1
    done
    
    echo "Ambos servicios están en ejecución."
    
    # Dar tiempo para que los servicios se estabilicen
    sleep 2
fi

echo "=== Ejecutando pruebas unitarias de servicios ==="
python3 /home/ubuntu/microservices-app/test_services.py

echo "=== Ejecutando pruebas de integración ==="
python3 /home/ubuntu/microservices-app/test_integration.py

# Si iniciamos los servicios en este script, los detenemos al finalizar
if [ -n "$AUTH_PID" ] && [ -n "$FRONTEND_PID" ]; then
    echo "Deteniendo servicios..."
    kill $AUTH_PID
    kill $FRONTEND_PID
fi

echo "=== Pruebas completadas ==="
