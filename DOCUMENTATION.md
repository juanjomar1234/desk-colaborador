# Documentación Técnica: Aplicación Web basada en Microservicios

## 1. Introducción

Esta documentación describe la arquitectura, componentes y funcionamiento de una aplicación web basada en microservicios desarrollada con Python, HTML, JavaScript y CSS. La aplicación está compuesta por dos microservicios principales: un servicio de autenticación (auth-service) y un servicio de frontend (frontend-service), ambos implementados con un tema oscuro para mejorar la experiencia visual del usuario.

## 2. Arquitectura General

### 2.1 Visión General

La aplicación sigue una arquitectura de microservicios, donde cada componente funcional está implementado como un servicio independiente que se comunica con otros servicios a través de APIs REST. Esta arquitectura proporciona varias ventajas:

- **Desacoplamiento**: Cada servicio puede desarrollarse, desplegarse y escalarse de forma independiente.
- **Tecnología heterogénea**: Cada servicio puede utilizar las tecnologías más adecuadas para su función.
- **Resiliencia**: Los fallos en un servicio no afectan necesariamente a otros servicios.
- **Escalabilidad**: Los servicios pueden escalarse individualmente según las necesidades.

### 2.2 Diagrama de Arquitectura

```
+------------------+       +-------------------+
|                  |       |                   |
|  Auth Service    |<----->|  Frontend Service |
|  (Puerto 5000)   |       |  (Puerto 5001)    |
|                  |       |                   |
+------------------+       +-------------------+
         ^                           ^
         |                           |
         v                           v
+------------------+       +-------------------+
|                  |       |                   |
|  Base de Datos   |       |     Usuarios      |
|    SQLite        |       |     Finales       |
|                  |       |                   |
+------------------+       +-------------------+
```

### 2.3 Tecnologías Utilizadas

- **Backend**:
  - Python 3.10
  - Flask 3.1.0 (Framework web)
  - Flask-SQLAlchemy 3.1.1 (ORM)
  - Flask-JWT-Extended 4.7.1 (Autenticación JWT)
  - Flask-CORS 5.0.1 (Manejo de CORS)

- **Frontend**:
  - HTML5
  - CSS3
  - JavaScript (ES6+)
  - Font Awesome (Iconos)

- **Despliegue**:
  - Docker
  - Docker Compose

## 3. Microservicio de Autenticación (auth-service)

### 3.1 Descripción

El servicio de autenticación (auth-service) es responsable de gestionar la autenticación de usuarios, roles y permisos en la aplicación. Proporciona endpoints para registro, inicio de sesión, verificación de tokens y gestión de usuarios y roles.

### 3.2 Estructura de Directorios

```
auth-service/
├── static/
│   ├── css/
│   │   └── auth.css
│   ├── js/
│   │   ├── auth.js
│   │   └── register.js
│   └── img/
├── templates/
│   ├── login.html
│   └── register.html
├── models/
│   ├── user.py
│   └── role.py
├── routes/
│   ├── auth.py
│   ├── user.py
│   ├── role.py
│   ├── permission.py
│   └── views.py
├── __init__.py
├── app.py
├── run.py
├── requirements.txt
└── Dockerfile
```

### 3.3 Modelos de Datos

#### 3.3.1 Modelo de Usuario (user.py)

El modelo de Usuario gestiona la información de los usuarios registrados en el sistema.

**Atributos principales**:
- `id`: Identificador único del usuario
- `username`: Nombre de usuario (único)
- `email`: Correo electrónico del usuario (único)
- `password_hash`: Hash de la contraseña del usuario
- `role`: Rol asignado al usuario (por defecto: 'user')

**Métodos principales**:
- `set_password()`: Establece el hash de la contraseña
- `check_password()`: Verifica si una contraseña coincide con el hash almacenado
- `to_dict()`: Convierte el objeto usuario a un diccionario

#### 3.3.2 Modelo de Rol y Permiso (role.py)

Los modelos de Rol y Permiso gestionan los roles y permisos disponibles en el sistema.

**Modelo de Permiso**:
- `id`: Identificador único del permiso
- `name`: Nombre del permiso (único)
- `description`: Descripción del permiso

**Modelo de Rol**:
- `id`: Identificador único del rol
- `name`: Nombre del rol (único)
- `description`: Descripción del rol
- `permissions`: Relación muchos a muchos con los permisos

### 3.4 Rutas y Endpoints

#### 3.4.1 Rutas de Autenticación (auth.py)

- `POST /api/auth/register`: Registra un nuevo usuario
- `POST /api/auth/login`: Inicia sesión y devuelve un token JWT
- `GET /api/auth/user`: Devuelve información del usuario autenticado
- `GET /api/auth/check-auth`: Verifica si el token es válido

#### 3.4.2 Rutas de Usuario (user.py)

- `GET /api/users/`: Obtiene todos los usuarios (solo admin)
- `GET /api/users/<id>`: Obtiene un usuario específico
- `PUT /api/users/<id>`: Actualiza un usuario
- `DELETE /api/users/<id>`: Elimina un usuario (solo admin)

#### 3.4.3 Rutas de Rol (role.py)

- `GET /api/roles/`: Obtiene todos los roles (solo admin)
- `POST /api/roles/`: Crea un nuevo rol (solo admin)
- `GET /api/roles/<id>`: Obtiene un rol específico
- `PUT /api/roles/<id>`: Actualiza un rol (solo admin)
- `DELETE /api/roles/<id>`: Elimina un rol (solo admin)

#### 3.4.4 Rutas de Permiso (permission.py)

- `GET /api/permissions/`: Obtiene todos los permisos (solo admin)
- `POST /api/permissions/`: Crea un nuevo permiso (solo admin)
- `GET /api/permissions/<id>`: Obtiene un permiso específico
- `PUT /api/permissions/<id>`: Actualiza un permiso (solo admin)
- `DELETE /api/permissions/<id>`: Elimina un permiso (solo admin)

### 3.5 Flujo de Autenticación

1. El usuario envía credenciales (username/password) al endpoint `/api/auth/login`
2. El servicio verifica las credenciales contra la base de datos
3. Si son válidas, genera un token JWT con la identidad del usuario y su rol
4. El token se devuelve al cliente y se almacena en localStorage
5. Las solicitudes posteriores incluyen el token en el encabezado Authorization
6. El servicio verifica el token en cada solicitud a endpoints protegidos

### 3.6 Seguridad

- Contraseñas almacenadas como hashes usando Werkzeug Security
- Autenticación basada en tokens JWT
- Protección de rutas basada en roles
- Validación de entradas en todas las rutas

## 4. Microservicio Frontend (frontend-service)

### 4.1 Descripción

El servicio frontend (frontend-service) proporciona la interfaz de usuario de la aplicación. Presenta una página principal con tarjetas que representan diferentes aplicaciones o microservicios disponibles para el usuario. Implementa un tema oscuro para mejorar la experiencia visual.

### 4.2 Estructura de Directorios

```
frontend-service/
├── static/
│   ├── css/
│   │   └── main.css
│   ├── js/
│   │   ├── main.js
│   │   └── login.js
│   └── img/
├── templates/
│   ├── index.html
│   └── login.html
├── routes/
│   ├── frontend.py
│   └── __init__.py
├── __init__.py
├── run.py
├── requirements.txt
└── Dockerfile
```

### 4.3 Componentes Principales

#### 4.3.1 Página Principal (index.html)

La página principal muestra una interfaz con tarjetas que representan diferentes aplicaciones o microservicios disponibles para el usuario. Cada tarjeta incluye:

- Icono representativo
- Nombre de la aplicación
- Descripción breve
- Enlace para acceder a la aplicación

#### 4.3.2 Sistema de Tarjetas

El sistema de tarjetas está implementado con CSS Grid para una disposición responsiva que se adapta a diferentes tamaños de pantalla. Las tarjetas tienen efectos de hover para mejorar la interactividad.

#### 4.3.3 Tema Oscuro

El tema oscuro está implementado mediante variables CSS que definen una paleta de colores oscuros para toda la aplicación:

```css
:root {
  --bg-primary: #121212;
  --bg-secondary: #1e1e1e;
  --text-primary: #ffffff;
  --text-secondary: #b3b3b3;
  --accent-color: #bb86fc;
  --error-color: #cf6679;
  --success-color: #03dac6;
  --border-color: #333333;
  --card-bg: #2d2d2d;
}
```

### 4.4 Rutas y Endpoints

- `GET /`: Página principal con tarjetas de aplicaciones
- `GET /login`: Página de inicio de sesión
- `GET /check-auth`: Verifica la autenticación del usuario

### 4.5 Integración con Auth Service

El frontend-service se comunica con el auth-service para:

1. Autenticar usuarios durante el inicio de sesión
2. Verificar tokens de autenticación
3. Obtener información del usuario autenticado

Esta comunicación se realiza mediante solicitudes HTTP a los endpoints del auth-service.

## 5. Integración entre Servicios

### 5.1 Comunicación entre Microservicios

La comunicación entre el frontend-service y el auth-service se realiza mediante solicitudes HTTP REST. El frontend-service envía solicitudes al auth-service para autenticar usuarios y verificar tokens.

### 5.2 Flujo de Datos

1. El usuario accede al frontend-service
2. Si no está autenticado, se redirige a la página de login
3. El usuario introduce credenciales
4. El frontend-service envía las credenciales al auth-service
5. El auth-service verifica las credenciales y devuelve un token JWT
6. El frontend-service almacena el token y lo utiliza para solicitudes posteriores
7. El frontend-service muestra la página principal con las tarjetas de aplicaciones

### 5.3 Gestión de Sesiones

La gestión de sesiones se realiza mediante tokens JWT almacenados en el localStorage del navegador. Esto permite mantener la sesión del usuario entre recargas de página sin necesidad de mantener estado en el servidor.

## 6. Despliegue

### 6.1 Requisitos
- Docker
- Docker Compose

### 6.2 Configuración de Docker

Cada microservicio tiene su propio Dockerfile que define cómo construir la imagen del contenedor:

**auth-service/Dockerfile**:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "run.py"]
```

**frontend-service/Dockerfile**:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5001
CMD ["python", "run.py"]
```

### 6.3 Docker Compose

El archivo docker-compose.yml define cómo se ejecutan y conectan los servicios:

```yaml
version: '3'
services:
  auth-service:
    build: ./auth-service
    ports:
      - "5000:5000"
    volumes:
      - ./auth-service:/app
    environment:
      - FLASK_APP=run.py
      - FLASK_ENV=development
    command: python run.py

  frontend-service:
    build: ./frontend-service
    ports:
      - "5001:5001"
    volumes:
      - ./frontend-service:/app
    environment:
      - FLASK_APP=run.py
      - FLASK_ENV=development
      - AUTH_SERVICE_URL=http://auth-service:5000
    depends_on:
      - auth-service
    command: python run.py
```

Para producción, se utiliza docker-compose.prod.yml con configuraciones específicas para entorno de producción.

### 6.4 Preparación para Repositorio

1. Crear archivo .gitignore:
```bash
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/

# IDEs
.idea/
.vscode/
*.swp
*.swo

# Logs
*.log

# Local environment
.env
.env.local

# Docker
.docker/

# Sistema
.DS_Store
Thumbs.db
```

2. Verificar archivos a ignorar:
```bash
git status
```

3. Limpiar archivos de caché y compilados:
```bash
# Eliminar archivos __pycache__
find . -type d -name "__pycache__" -exec rm -r {} +

# Eliminar archivos .pyc
find . -name "*.pyc" -delete
```

4. Organizar estructura de archivos:
```
microservices-app/
├── auth-service/
│   └── .env.example
├── frontend-service/
│   └── .env.example
├── docker-compose.yml
├── docker-compose.prod.yml
├── .gitignore
├── README.md
└── DOCUMENTATION.md
```

### 6.5 Conexión con Repositorio Remoto

1. Conectar con el repositorio remoto:
```bash
git remote add origin https://github.com/juanjomar1234/desk-colaborador.git
```

2. Verificar la conexión remota:
```bash
git remote -v
```

3. Preparar archivos para el primer commit:
```bash
git add .
git commit -m "Initial commit: Microservices application setup"
```

4. Subir al repositorio:
```bash
git branch -M main
git push -u origin main
```

### 6.6 Configuración de Secretos para GitHub Actions

1. Acceder a la configuración de secretos:
   - Ir al repositorio en GitHub
   - Click en "Settings"
   - En el menú lateral, click en "Secrets and variables" > "Actions"
   - Click en "New repository secret"

2. Configurar los siguientes secretos:
   - `DOCKER_USERNAME`: Usuario de Docker Hub
   - `DOCKER_PASSWORD`: Token de acceso de Docker Hub
   - `SSH_PRIVATE_KEY`: Clave SSH privada para el servidor
   - `SSH_HOST`: Dirección IP o dominio del servidor
   - `SSH_USER`: Usuario SSH del servidor
   - `SSH_PORT`: 65002
   - `DEPLOY_PATH`: /var/www/desk-colaborador

3. Verificar secretos:
   - En la lista de secretos deben aparecer los 7 secretos configurados
   - Los valores no serán visibles por seguridad
   - Cada secreto mostrará la fecha de última actualización

### 6.7 Configuración de GitHub Actions Workflow

1. Crear directorio y archivo de workflow:
```bash
mkdir -p .github/workflows
touch .github/workflows/deploy.yml
```

2. Configurar punto de entrada Python y CGI:
```bash
# index.py - Punto de entrada principal
from frontend_service.app import app

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

# .htaccess - Configuración del servidor web
Options +ExecCGI
AddHandler cgi-script .py
DirectoryIndex index.py

<Files "index.py">
    Options +ExecCGI
    SetHandler cgi-script
</Files>
```

3. Contenido del archivo deploy.yml:
```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Copy files to server
        uses: appleboy/scp-action@master
        with:
          host: ${{ secrets.SSH_HOST }}
          username: ${{ secrets.SSH_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          port: ${{ secrets.SSH_PORT }}
          source: "auth-service/**,frontend-service/**,*.py,*.md,*.yml,.htaccess"
          target: "${{ secrets.DEPLOY_PATH }}"
          rm: true
          strip_components: 0
          overwrite: true

      - name: Set permissions
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SSH_HOST }}
          username: ${{ secrets.SSH_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          port: ${{ secrets.SSH_PORT }}
          script: |
            chmod -R 755 ${{ secrets.DEPLOY_PATH }}
            find ${{ secrets.DEPLOY_PATH }} -type f -exec chmod 644 {} \;
```

## 7. Pruebas

### 7.1 Pruebas Unitarias

Se han implementado pruebas unitarias para verificar el funcionamiento de cada servicio individualmente:

- **test_services.py**: Pruebas unitarias para auth-service y frontend-service

### 7.2 Pruebas de Integración

Se han implementado pruebas de integración para verificar la comunicación entre servicios:

- **test_integration.py**: Pruebas de integración entre auth-service y frontend-service

### 7.3 Ejecución de Pruebas

Para ejecutar todas las pruebas:

```bash
./run_all_tests.sh
```

## 8. Mantenimiento

### 8.1 Logs

Para ver los logs de los servicios:

```bash
docker-compose logs
```

O en producción:

```bash
docker-compose -f docker-compose.prod.yml logs
```

### 8.2 Reinicio de Servicios

Para reiniciar los servicios:

```bash
docker-compose restart
```

O en producción:

```bash
docker-compose -f docker-compose.prod.yml restart
```

### 8.3 Actualización de Servicios

Para actualizar los servicios después de cambios en el código:

```bash
docker-compose up -d --build
```

O en producción:

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

## 9. Seguridad

### 9.1 Autenticación

- Autenticación basada en tokens JWT
- Almacenamiento seguro de contraseñas mediante hashing
- Expiración de tokens configurable

### 9.2 Autorización

- Sistema de roles y permisos
- Protección de rutas basada en roles
- Verificación de permisos para operaciones sensibles

### 9.3 Comunicación Segura

- Validación de entradas en todas las rutas
- Protección contra ataques CSRF
- Configuración de CORS para controlar el acceso desde diferentes orígenes

## 10. Conclusiones

Esta aplicación web basada en microservicios proporciona una arquitectura moderna, escalable y mantenible. La separación de responsabilidades entre el servicio de autenticación y el servicio frontend permite un desarrollo independiente y facilita el mantenimiento. El tema oscuro implementado en toda la aplicación mejora la experiencia visual del usuario.

La arquitectura elegida permite añadir fácilmente nuevos microservicios en el futuro, extendiendo la funcionalidad de la aplicación sin afectar a los servicios existentes.

## 11. Apéndices

### 11.1 Credenciales por Defecto

- **Usuario**: admin
- **Contraseña**: admin123

### 11.2 URLs de Acceso

- **Frontend Service**: http://localhost:5001
- **Auth Service**: http://localhost:5000

### 11.3 Estructura Completa del Proyecto

```
microservices-app/
├── auth-service/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   ├── templates/
│   ├── models/
│   ├── routes/
│   ├── __init__.py
│   ├── app.py
│   ├── run.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend-service/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   ├── templates/
│   ├── routes/
│   ├── __init__.py
│   ├── run.py
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
├── docker-compose.prod.yml
├── deploy.sh
├── run_tests.sh
├── run_all_tests.sh
├── test_integration.py
├── test_services.py
├── README.md
└── todo.md
```
