from flask import Blueprint, jsonify, request, render_template, session, redirect, url_for
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..models.user import User
from .. import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    """Página de inicio del servicio de autenticación"""
    return jsonify({
        'service': 'Auth Service',
        'version': '1.0',
        'endpoints': {
            'login': '/auth/login',
            'register': '/auth/register',
            'verify': '/auth/verify',
            'user': '/auth/user',
            'check-auth': '/auth/check-auth'
        }
    })

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Verificar si el usuario ya existe
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'El usuario ya existe'}), 409
    
    # Crear nuevo usuario
    new_user = User(
        username=data['username'],
        email=data['email'],
        role=data.get('role', 'user')
    )
    new_user.set_password(data['password'])
    
    # Guardar en la base de datos
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'Usuario registrado exitosamente'}), 201

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No se recibieron datos'}), 400
        
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'message': 'Faltan campos requeridos'}), 400
    
    # Para pruebas, aceptar credenciales de test
    if username == 'test' and password == 'test':
        access_token = create_access_token(identity='test')
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token
        }), 200
        
    # Buscar usuario real
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=user.username)
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token
        }), 200
    
    return jsonify({'message': 'Credenciales inválidas'}), 401

@auth_bp.route('/verify', methods=['GET'])
def verify():
    token = request.headers.get('Authorization')
    if token and token.startswith('Bearer '):
        # Aquí iría la verificación del token
        return jsonify({'valid': True})
    return jsonify({'valid': False}), 401

@auth_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    try:
        current_user = get_jwt_identity()
        if not current_user:
            return jsonify({'message': 'Token inválido'}), 401
            
        return jsonify(current_user), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 401

@auth_bp.route('/check-auth', methods=['GET'])
@jwt_required()
def check_auth():
    return jsonify({'authenticated': True}), 200
