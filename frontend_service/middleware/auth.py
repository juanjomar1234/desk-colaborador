from functools import wraps
from flask import request, redirect, session, current_app, jsonify
import requests
import os
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

def require_auth(f=None):
    if f is None:
        return require_auth

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # No verificar autenticación para rutas de auth y static
        if request.path.startswith('/login') or request.path.startswith('/static/'):
            return f(*args, **kwargs)

        # Verificar token en sesión
        token = session.get('token')
        if not token:
            # Guardar la URL original para redirigir después del login
            session['next_url'] = request.url
            return redirect('/login')  # Ya no es /auth/login

        # Verificar token con auth-service
        auth_url = os.environ.get('AUTH_SERVICE_URL', 'http://auth:8000')
        try:
            response = requests.get(
                f"{auth_url}/verify",
                headers={'Authorization': f'Bearer {token}'},
                timeout=5  # Añadir timeout
            )
            print(f"Auth response: {response.status_code}")  # Debug log
            if response.status_code != 200:
                session.clear()
                return redirect('/login')
        except:
            session.clear()
            return redirect('/login')

        return f(*args, **kwargs)
    return decorated_function

def jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({'message': str(e)}), 401
    return wrapper 