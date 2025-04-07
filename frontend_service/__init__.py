from flask import Flask
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

def create_app(test_config=None):
    # Crear y configurar la aplicación
    app = Flask(__name__, instance_relative_config=True)
    
    # Configuración por defecto
    app.config.from_mapping(
        SECRET_KEY='dev',
        AUTH_SERVICE_URL='http://localhost:5000',
    )

    if test_config is None:
        # Cargar la configuración de la instancia, si existe
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Cargar la configuración de prueba si se pasa
        app.config.from_mapping(test_config)

    # Configurar proxy para el servicio de autenticación
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Configurar CORS
    CORS(app, supports_credentials=True)

    # Registrar blueprints
    from .routes.views import views_bp
    app.register_blueprint(views_bp)

    return app

# Este archivo vacío marca el directorio como un paquete Python
