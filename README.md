# Guía de Despliegue y Uso

## Requisitos Previos
- Docker
- Docker Compose

## Instrucciones de Despliegue

### Método 1: Usando el script de despliegue automatizado
1. Asegúrese de tener Docker y Docker Compose instalados
2. Ejecute el script de despliegue:
   ```bash
   ./deploy.sh
   ```
3. El script verificará que los servicios estén funcionando correctamente

### Método 2: Despliegue manual
1. Construya y despliegue los servicios:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d --build
   ```
2. Verifique que los servicios estén funcionando:
   - Auth Service: http://localhost:5000
   - Frontend Service: http://localhost:5001

## Acceso a la Aplicación
- **URL Frontend**: http://localhost:5001
- **URL Auth Service**: http://localhost:5000

## Credenciales por Defecto
- **Usuario**: admin
- **Contraseña**: admin123

## Estructura de la Aplicación
La aplicación está compuesta por dos microservicios:

1. **Auth Service (Puerto 5000)**
   - Gestión de autenticación
   - Administración de usuarios, roles y permisos
   - API RESTful para operaciones de autenticación

2. **Frontend Service (Puerto 5001)**
   - Interfaz de usuario con tema oscuro
   - Sistema de tarjetas para aplicaciones
   - Integración con el servicio de autenticación

## Mantenimiento

### Ver logs de los servicios
```bash
docker-compose -f docker-compose.prod.yml logs
```

### Reiniciar los servicios
```bash
docker-compose -f docker-compose.prod.yml restart
```

### Detener los servicios
```bash
docker-compose -f docker-compose.prod.yml down
```

## Desarrollo

Para entorno de desarrollo, use el archivo docker-compose.yml estándar:
```bash
docker-compose up -d --build
```

## Pruebas

Para ejecutar las pruebas automatizadas:
```bash
./run_all_tests.sh
```

## Despliegue con GitHub

### 1. Preparación del Repositorio
1. Clonar el repositorio:
   ```bash
   git clone https://github.com/juanjomar1234/desk-colaborador.git
   cd desk-colaborador
   ```

### 2. Configuración de Secretos en GitHub
1. Ir a Settings > Secrets and variables > Actions
2. Añadir los siguientes secretos:
   - SSH_HOST
   - SSH_USER
   - SSH_PRIVATE_KEY
   - SSH_PORT
   - DEPLOY_PATH

### 3. Despliegue
1. Hacer push al repositorio:
   ```bash
   git push origin main
   ```
2. GitHub Actions ejecutará automáticamente el despliegue

### 4. Acceso mediante Subdominio
- Frontend: https://app.tudominio.com
- API Auth: https://app.tudominio.com/api/auth
