from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.role import Permission
from .. import db

permission_bp = Blueprint('permission', __name__, url_prefix='/api/permissions')

@permission_bp.route('/', methods=['GET'])
@jwt_required()
def get_permissions():
    # Verificar si el usuario tiene rol de administrador
    current_user = get_jwt_identity()
    if current_user.get('role') != 'admin':
        return jsonify({'message': 'No autorizado'}), 403
    
    # Obtener todos los permisos
    permissions = Permission.query.all()
    return jsonify({
        'permissions': [permission.to_dict() for permission in permissions]
    }), 200

@permission_bp.route('/', methods=['POST'])
@jwt_required()
def create_permission():
    # Verificar si el usuario tiene rol de administrador
    current_user = get_jwt_identity()
    if current_user.get('role') != 'admin':
        return jsonify({'message': 'No autorizado'}), 403
    
    data = request.get_json()
    
    # Verificar si el permiso ya existe
    if Permission.query.filter_by(name=data['name']).first():
        return jsonify({'message': 'El permiso ya existe'}), 409
    
    # Crear nuevo permiso
    new_permission = Permission(
        name=data['name'],
        description=data.get('description', '')
    )
    
    db.session.add(new_permission)
    db.session.commit()
    
    return jsonify({
        'message': 'Permiso creado exitosamente',
        'permission': new_permission.to_dict()
    }), 201

@permission_bp.route('/<int:permission_id>', methods=['GET'])
@jwt_required()
def get_permission(permission_id):
    # Verificar si el usuario tiene rol de administrador
    current_user = get_jwt_identity()
    if current_user.get('role') != 'admin':
        return jsonify({'message': 'No autorizado'}), 403
    
    # Obtener permiso
    permission = Permission.query.get(permission_id)
    if not permission:
        return jsonify({'message': 'Permiso no encontrado'}), 404
    
    return jsonify(permission.to_dict()), 200

@permission_bp.route('/<int:permission_id>', methods=['PUT'])
@jwt_required()
def update_permission(permission_id):
    # Verificar si el usuario tiene rol de administrador
    current_user = get_jwt_identity()
    if current_user.get('role') != 'admin':
        return jsonify({'message': 'No autorizado'}), 403
    
    # Obtener permiso
    permission = Permission.query.get(permission_id)
    if not permission:
        return jsonify({'message': 'Permiso no encontrado'}), 404
    
    data = request.get_json()
    
    # Actualizar campos
    if 'name' in data:
        permission.name = data['name']
    if 'description' in data:
        permission.description = data['description']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Permiso actualizado exitosamente',
        'permission': permission.to_dict()
    }), 200

@permission_bp.route('/<int:permission_id>', methods=['DELETE'])
@jwt_required()
def delete_permission(permission_id):
    # Verificar si el usuario tiene rol de administrador
    current_user = get_jwt_identity()
    if current_user.get('role') != 'admin':
        return jsonify({'message': 'No autorizado'}), 403
    
    # Obtener permiso
    permission = Permission.query.get(permission_id)
    if not permission:
        return jsonify({'message': 'Permiso no encontrado'}), 404
    
    # Eliminar permiso
    db.session.delete(permission)
    db.session.commit()
    
    return jsonify({'message': 'Permiso eliminado exitosamente'}), 200
