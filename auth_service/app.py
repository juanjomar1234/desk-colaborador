import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Inicialización de extensiones
db = SQLAlchemy()
jwt = JWTManager()

def create_app(test_config=None):
    # Crear y configurar la aplicación
    app = Flask(__name__, instance_relative_config=True)
    
    # Configuración por defecto
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'auth.sqlite'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY='jwt-secret-key',
    )

    if test_config is None:
        # Cargar la configuración de la instancia, si existe
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Cargar la configuración de prueba si se pasa
        app.config.from_mapping(test_config)

    # Asegurar que existe el directorio de la instancia
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Inicializar extensiones con la aplicación
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)

    # Registrar blueprints
    from .routes import auth_bp
    app.register_blueprint(auth_bp)

    # Crear tablas de la base de datos
    with app.app_context():
        db.create_all()

    return app
