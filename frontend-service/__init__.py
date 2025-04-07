from flask import Flask
from flask_cors import CORS

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

    # Habilitar CORS
    CORS(app)

    # Registrar blueprints
    from .routes.frontend import frontend_bp
    app.register_blueprint(frontend_bp)

    return app
