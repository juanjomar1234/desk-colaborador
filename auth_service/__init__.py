from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os

# Inicialización de extensiones
db = SQLAlchemy()
jwt = JWTManager()

def create_app(test_config=None):
    # Crear y configurar la aplicación
    app = Flask(__name__, 
                instance_relative_config=True,
                static_url_path='',
                static_folder='static',
                template_folder='templates')
    
    # Obtener la ruta absoluta para la base de datos
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'auth.sqlite')
    
    # Configuración por defecto
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI=f'sqlite:///{db_path}',  # Usar ruta absoluta
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY='jwt-secret-key',  # Clave para JWT
        JWT_ACCESS_TOKEN_EXPIRES=False,  # No expirar tokens en pruebas
        JWT_ERROR_MESSAGE_KEY='message',  # Clave para mensajes de error
        DEBUG=True  # Habilitar modo debug
    )

    if test_config is not None:
        app.config.update(test_config)

    # Inicializar extensiones
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost:8001", "http://web:8001"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Registrar blueprints sin prefijo para auth_bp
    from .routes.auth import auth_bp
    auth_bp.url_prefix = ''
    app.register_blueprint(auth_bp)

    # Registrar otros blueprints con sus prefijos
    from .routes.user import user_bp
    from .routes.role import role_bp
    from .routes.permission import permission_bp
    from .routes.views import auth_view_bp
    
    app.register_blueprint(user_bp)
    app.register_blueprint(role_bp)
    app.register_blueprint(permission_bp)
    app.register_blueprint(auth_view_bp)

    @app.route('/')
    def index():
        """Página de inicio del servicio de autenticación"""
        return jsonify({
            'service': 'Auth Service',
            'version': '1.0',
            'endpoints': {
                'login': '/login',
                'register': '/register',
                'verify': '/verify',
                'user': '/user',
                'check-auth': '/check-auth'
            }
        })

    # Crear tablas y datos iniciales
    with app.app_context():
        db.create_all()
        
        # Importar modelos aquí para evitar circular imports
        from .models.role import Role, Permission
        from .models.user import User
        
        # Crear permisos y roles por defecto si no existen
        with db.session.no_autoflush:
            if Permission.query.count() == 0:
                permisos = [
                    Permission(name='read_users', description='Leer usuarios'),
                    Permission(name='create_users', description='Crear usuarios'),
                    Permission(name='update_users', description='Actualizar usuarios'),
                    Permission(name='delete_users', description='Eliminar usuarios'),
                    Permission(name='manage_roles', description='Gestionar roles')
                ]
                db.session.add_all(permisos)
                db.session.commit()

            if Role.query.count() == 0:
                admin_role = Role(name='admin', description='Administrador')
                user_role = Role(name='user', description='Usuario estándar')
                
                admin_role.permissions = Permission.query.all()
                user_role.permissions = [Permission.query.filter_by(name='read_users').first()]
                
                db.session.add_all([admin_role, user_role])
                db.session.commit()

    return app
