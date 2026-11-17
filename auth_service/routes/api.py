from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import text
from .helpers import get_current_user
from .. import db

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/health', methods=['GET'])
def health():
    """Estado del servicio y de la conexión a la base de datos"""
    try:
        db.session.execute(text('SELECT 1'))
        database = 'ok'
    except Exception:
        database = 'error'
    status = 'ok' if database == 'ok' else 'degraded'
    return jsonify({
        'service': 'Auth Service',
        'version': '1.0',
        'status': status,
        'database': database
    }), 200 if status == 'ok' else 503


@api_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    """Perfil del usuario autenticado"""
    user = get_current_user()
    if not user:
        return jsonify({'message': 'Usuario no encontrado'}), 404
    return jsonify(user), 200
