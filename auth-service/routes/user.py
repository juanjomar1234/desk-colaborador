from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.user import User
from .. import db

user_bp = Blueprint('user', __name__, url_prefix='/api/users')

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
