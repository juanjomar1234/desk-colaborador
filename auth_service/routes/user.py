from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from ..models.user import User
from ..models.role import Role
from .. import db

user_bp = Blueprint('user', __name__, url_prefix='/api/users')


def _current_db_user():
    # Solo los tokens emitidos por un login real llevan `uid`; el login de
    # pruebas (test/test) no debe heredar los permisos de un usuario de la BD.
    uid = get_jwt().get('uid')
    if uid is None:
        return None
    user = db.session.get(User, uid)
    if not user or user.username != get_jwt_identity():
        return None
    return user


@user_bp.route('/', methods=['POST'])
@jwt_required()
def create_user():
    """Alta de usuarios por un administrador"""
    current_user = _current_db_user()
    if not current_user or current_user.role != 'admin':
        return jsonify({'message': 'No autorizado'}), 403

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'message': 'Se esperaba un cuerpo JSON'}), 400

    fields = {f: data.get(f) for f in ('username', 'email', 'password')}
    missing = [f for f, v in fields.items() if not isinstance(v, str) or not v.strip()]
    if missing:
        return jsonify({'message': 'Faltan campos requeridos', 'fields': missing}), 400

    username = fields['username'].strip()
    email = fields['email'].strip()
    if '@' not in email:
        return jsonify({'message': 'Email no válido'}), 400

    role = data.get('role', 'user')
    if not isinstance(role, str) or not Role.query.filter_by(name=role).first():
        return jsonify({'message': 'Rol no válido'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'El usuario ya existe'}), 409
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'El email ya está registrado'}), 409

    new_user = User(username=username, email=email, role=role)
    new_user.set_password(fields['password'])
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        'message': 'Usuario creado exitosamente',
        'user': new_user.to_dict()
    }), 201


@user_bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    # Verificar si el usuario tiene rol de administrador
    current_user = get_jwt_identity()
    if current_user.get('role') != 'admin':
        return jsonify({'message': 'No autorizado'}), 403
    
    # Obtener todos los usuarios
    users = User.query.all()
    return jsonify({
        'users': [user.to_dict() for user in users]
    }), 200

@user_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    # Verificar si el usuario tiene rol de administrador o es el mismo usuario
    current_user = get_jwt_identity()
    if current_user.get('role') != 'admin' and current_user.get('id') != user_id:
        return jsonify({'message': 'No autorizado'}), 403
    
    # Obtener usuario
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'Usuario no encontrado'}), 404
    
    return jsonify(user.to_dict()), 200

@user_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    # Verificar si el usuario tiene rol de administrador o es el mismo usuario
    current_user = get_jwt_identity()
    if current_user.get('role') != 'admin' and current_user.get('id') != user_id:
        return jsonify({'message': 'No autorizado'}), 403
    
    # Obtener usuario
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'Usuario no encontrado'}), 404
    
    # Actualizar datos
    data = request.get_json()
    
    # Solo administradores pueden cambiar roles
    if 'role' in data and current_user.get('role') != 'admin':
        return jsonify({'message': 'No autorizado para cambiar roles'}), 403
    
    # Actualizar campos
    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']
    if 'role' in data and current_user.get('role') == 'admin':
        user.role = data['role']
    if 'password' in data:
        user.set_password(data['password'])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Usuario actualizado exitosamente',
        'user': user.to_dict()
    }), 200

@user_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    # Solo administradores pueden eliminar usuarios
    current_user = get_jwt_identity()
    if current_user.get('role') != 'admin':
        return jsonify({'message': 'No autorizado'}), 403
    
    # Obtener usuario
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'Usuario no encontrado'}), 404
    
    # Eliminar usuario
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'Usuario eliminado exitosamente'}), 200
