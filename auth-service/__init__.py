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
        SQLALCHEMY_DATABASE_URI='sqlite:///auth.sqlite',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY='jwt-secret-key',
    )

    if test_config is None:
        # Cargar la configuración de la instancia, si existe
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Cargar la configuración de prueba si se pasa
        app.config.from_mapping(test_config)

    # Inicializar extensiones con la aplicación
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)

    # Registrar blueprints
    from .routes.auth import auth_bp
    from .routes.user import user_bp
    from .routes.role import role_bp
    from .routes.permission import permission_bp
    from .routes.views import auth_view_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(role_bp)
    app.register_blueprint(permission_bp)
    app.register_blueprint(auth_view_bp)

    # Crear tablas de la base de datos
    with app.app_context():
        db.create_all()
        
        # Crear permisos y roles por defecto si no existen
        from .models.role import Role, Permission
        from .models.user import User
        
        # Verificar si ya existen permisos
        if Permission.query.count() == 0:
            # Crear permisos básicos
            permisos = [
                Permission(name='read_users', description='Leer usuarios'),
                Permission(name='create_users', description='Crear usuarios'),
                Permission(name='update_users', description='Actualizar usuarios'),
                Permission(name='delete_users', description='Eliminar usuarios'),
                Permission(name='manage_roles', description='Gestionar roles')
            ]
            db.session.add_all(permisos)
            db.session.commit()
        
        # Verificar si ya existen roles
        if Role.query.count() == 0:
            # Crear roles básicos
            admin_role = Role(name='admin', description='Administrador con todos los permisos')
            user_role = Role(name='user', description='Usuario estándar')
            
            # Asignar todos los permisos al rol de administrador
            admin_role.permissions = Permission.query.all()
            
            # Asignar permiso de lectura al rol de usuario
            user_role.permissions = [Permission.query.filter_by(name='read_users').first()]
            
            db.session.add_all([admin_role, user_role])
            db.session.commit()
        
        # Crear usuario administrador por defecto si no existe
        if User.query.count() == 0:
            admin_user = User(
                username='admin',
                email='admin@example.com',
                role='admin'
            )
            admin_user.set_password('admin123')
            
            db.session.add(admin_user)
            db.session.commit()

    return app
