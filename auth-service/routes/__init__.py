from flask import Blueprint

# Importar blueprints
from .auth import auth_bp
from .user import user_bp
from .role import role_bp
from .permission import permission_bp
from .views import auth_view_bp
