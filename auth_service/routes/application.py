from functools import wraps
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.application import Application
from ..models.user import User
from .. import db

application_bp = Blueprint('application', __name__, url_prefix='/api/applications')

EDITABLE_FIELDS = ('name', 'description', 'icon', 'url', 'active')


def _current_user_is_admin():
    user = User.query.filter_by(username=get_jwt_identity()).first()
    return user is not None and user.role == 'admin'


def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not _current_user_is_admin():
            return jsonify({'message': 'No autorizado'}), 403
        return view(*args, **kwargs)
    return wrapper


def _validate(data, partial=False):
    if not isinstance(data, dict):
        return 'Se esperaba un objeto JSON'
    if not partial or 'name' in data:
        name = data.get('name')
        if not isinstance(name, str) or not name.strip():
            return 'El campo "name" es obligatorio'
    for field in ('description', 'icon', 'url'):
        if field in data and not isinstance(data[field], str):
            return f'El campo "{field}" debe ser texto'
    if 'active' in data and not isinstance(data['active'], bool):
        return 'El campo "active" debe ser booleano'
    return None


@application_bp.route('/', methods=['GET'])
@jwt_required()
def list_applications():
    query = Application.query
    if request.args.get('all', '').lower() not in ('1', 'true') or not _current_user_is_admin():
        query = query.filter_by(active=True)
    applications = query.order_by(Application.id).all()
    return jsonify({
        'applications': [application.to_dict() for application in applications]
    }), 200


@application_bp.route('/<int:application_id>', methods=['GET'])
@jwt_required()
def get_application(application_id):
    application = db.session.get(Application, application_id)
    if not application or (not application.active and not _current_user_is_admin()):
        return jsonify({'message': 'Aplicación no encontrada'}), 404
    return jsonify(application.to_dict()), 200


@application_bp.route('/', methods=['POST'])
@jwt_required()
@admin_required
def create_application():
    data = request.get_json(silent=True)
    error = _validate(data)
    if error:
        return jsonify({'message': error}), 400

    name = data['name'].strip()
    if Application.query.filter_by(name=name).first():
        return jsonify({'message': 'La aplicación ya existe'}), 409

    application = Application(name=name)
    for field in EDITABLE_FIELDS[1:]:
        if field in data:
            setattr(application, field, data[field])

    db.session.add(application)
    db.session.commit()

    return jsonify({
        'message': 'Aplicación creada exitosamente',
        'application': application.to_dict()
    }), 201


@application_bp.route('/<int:application_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_application(application_id):
    application = db.session.get(Application, application_id)
    if not application:
        return jsonify({'message': 'Aplicación no encontrada'}), 404

    data = request.get_json(silent=True)
    error = _validate(data, partial=True)
    if error:
        return jsonify({'message': error}), 400

    if 'name' in data:
        name = data['name'].strip()
        duplicate = Application.query.filter_by(name=name).first()
        if duplicate and duplicate.id != application.id:
            return jsonify({'message': 'La aplicación ya existe'}), 409
        data = {**data, 'name': name}

    for field in EDITABLE_FIELDS:
        if field in data:
            setattr(application, field, data[field])

    db.session.commit()

    return jsonify({
        'message': 'Aplicación actualizada exitosamente',
        'application': application.to_dict()
    }), 200


@application_bp.route('/<int:application_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_application(application_id):
    application = db.session.get(Application, application_id)
    if not application:
        return jsonify({'message': 'Aplicación no encontrada'}), 404

    db.session.delete(application)
    db.session.commit()

    return jsonify({'message': 'Aplicación eliminada exitosamente'}), 200
