from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.role import Role, Permission
from .. import db

role_bp = Blueprint('role', __name__, url_prefix='/api/roles')

@role_bp.route('/', methods=['GET'])
@jwt_required()
def get_roles():
    # Verificar si el usuario tiene rol de administrador
    current_user = get_jwt_identity()
    if current_user.get('role') != 'admin':
        return jsonify({'message': 'No autorizado'}), 403
    
    # Obtener todos los roles
    roles = Role.query.all()
    return jsonify({
        'roles': [role.to_dict() for role in roles]
    }), 200

@role_bp.route('/', methods=['POST'])
@jwt_required()
def create_role():
    # Verificar si el usuario tiene rol de administrador
    current_user = get_jwt_identity()
    if current_user.get('role') != 'admin':
        return jsonify({'message': 'No autorizado'}), 403
    
    data = request.get_json()
    
    # Verificar si el rol ya existe
    if Role.query.filter_by(name=data['name']).first():
        return jsonify({'message': 'El rol ya existe'}), 409
    
    # Crear nuevo rol
    new_role = Role(
        name=data['name'],
        description=data.get('description', '')
    )
    
    # Asignar permisos si se proporcionan
    if 'permissions' in data and isinstance(data['permissions'], list):
        for perm_id in data['permissions']:
            permission = Permission.query.get(perm_id)
            if permission:
                new_role.permissions.append(permission)
    
    db.session.add(new_role)
    db.session.commit()
    
    return jsonify({
        'message': 'Rol creado exitosamente',
        'role': new_role.to_dict()
    }), 201

@role_bp.route('/<int:role_id>', methods=['GET'])
@jwt_required()
def get_role(role_id):
    # Verificar si el usuario tiene rol de administrador
    current_user = get_jwt_identity()
    if current_user.get('role') != 'admin':
        return jsonify({'message': 'No autorizado'}), 403
    
    # Obtener rol
    role = Role.query.get(role_id)
    if not role:
        return jsonify({'message': 'Rol no encontrado'}), 404
    
    return jsonify(role.to_dict()), 200

@role_bp.route('/<int:role_id>', methods=['PUT'])
@jwt_required()
def update_role(role_id):
    # Verificar si el usuario tiene rol de administrador
    current_user = get_jwt_identity()
    if current_user.get('role') != 'admin':
        return jsonify({'message': 'No autorizado'}), 403
    
    # Obtener rol
    role = Role.query.get(role_id)
    if not role:
        return jsonify({'message': 'Rol no encontrado'}), 404
    
    data = request.get_json()
    
    # Actualizar campos
    if 'name' in data:
        role.name = data['name']
    if 'description' in data:
        role.description = data['description']
    
    # Actualizar permisos si se proporcionan
    if 'permissions' in data and isinstance(data['permissions'], list):
        # Limpiar permisos actuales
        role.permissions = []
        
        # Asignar nuevos permisos
        for perm_id in data['permissions']:
            permission = Permission.query.get(perm_id)
            if permission:
                role.permissions.append(permission)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Rol actualizado exitosamente',
        'role': role.to_dict()
    }), 200

@role_bp.route('/<int:role_id>', methods=['DELETE'])
@jwt_required()
def delete_role(role_id):
    # Verificar si el usuario tiene rol de administrador
    current_user = get_jwt_identity()
    if current_user.get('role') != 'admin':
        return jsonify({'message': 'No autorizado'}), 403
    
    # Obtener rol
    role = Role.query.get(role_id)
    if not role:
        return jsonify({'message': 'Rol no encontrado'}), 404
    
    # Eliminar rol
    db.session.delete(role)
    db.session.commit()
    
    return jsonify({'message': 'Rol eliminado exitosamente'}), 200
