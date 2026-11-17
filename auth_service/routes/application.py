from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from .helpers import get_current_user
from ..models.application import Application
from .. import db

application_bp = Blueprint('application', __name__, url_prefix='/api/apps')

FIELDS = ('name', 'icon', 'description', 'url', 'enabled')


def _is_admin():
    return get_current_user().get('role') == 'admin'


def _validate(data, partial=False):
    """Devuelve un mensaje de error o None si los datos son válidos"""
    if not isinstance(data, dict):
        return 'Se esperaba un objeto JSON'
    if not partial and not data.get('name'):
        return 'El campo name es obligatorio'
    if 'name' in data and (not isinstance(data['name'], str) or not data['name'].strip()):
        return 'El campo name debe ser un texto no vacío'
    for field in ('icon', 'description', 'url'):
        if field in data and not isinstance(data[field], str):
            return f'El campo {field} debe ser texto'
    if 'enabled' in data and not isinstance(data['enabled'], bool):
        return 'El campo enabled debe ser booleano'
    return None


@application_bp.route('/', methods=['GET'])
@jwt_required()
def get_applications():
    """Lista las aplicaciones; los no administradores solo ven las habilitadas"""
    query = Application.query
    if not _is_admin() or request.args.get('all') != 'true':
        query = query.filter_by(enabled=True)
    return jsonify({
        'apps': [app.to_dict() for app in query.order_by(Application.id).all()]
    }), 200


@application_bp.route('/<int:app_id>', methods=['GET'])
@jwt_required()
def get_application(app_id):
    app = db.session.get(Application, app_id)
    if not app or (not app.enabled and not _is_admin()):
        return jsonify({'message': 'Aplicación no encontrada'}), 404
    return jsonify(app.to_dict()), 200


@application_bp.route('/', methods=['POST'])
@jwt_required()
def create_application():
    if not _is_admin():
        return jsonify({'message': 'No autorizado'}), 403

    data = request.get_json(silent=True)
    error = _validate(data)
    if error:
        return jsonify({'message': error}), 400
    if Application.query.filter_by(name=data['name']).first():
        return jsonify({'message': 'La aplicación ya existe'}), 409

    app = Application(**{field: data[field] for field in FIELDS if field in data})
    db.session.add(app)
    db.session.commit()
    return jsonify({
        'message': 'Aplicación creada exitosamente',
        'app': app.to_dict()
    }), 201


@application_bp.route('/<int:app_id>', methods=['PUT'])
@jwt_required()
def update_application(app_id):
    if not _is_admin():
        return jsonify({'message': 'No autorizado'}), 403

    app = db.session.get(Application, app_id)
    if not app:
        return jsonify({'message': 'Aplicación no encontrada'}), 404

    data = request.get_json(silent=True)
    error = _validate(data, partial=True)
    if error:
        return jsonify({'message': error}), 400
    if 'name' in data and Application.query.filter(
            Application.name == data['name'], Application.id != app_id).first():
        return jsonify({'message': 'La aplicación ya existe'}), 409

    for field in FIELDS:
        if field in data:
            setattr(app, field, data[field])
    db.session.commit()
    return jsonify({
        'message': 'Aplicación actualizada exitosamente',
        'app': app.to_dict()
    }), 200


@application_bp.route('/<int:app_id>', methods=['DELETE'])
@jwt_required()
def delete_application(app_id):
    if not _is_admin():
        return jsonify({'message': 'No autorizado'}), 403

    app = db.session.get(Application, app_id)
    if not app:
        return jsonify({'message': 'Aplicación no encontrada'}), 404

    db.session.delete(app)
    db.session.commit()
    return jsonify({'message': 'Aplicación eliminada exitosamente'}), 200
