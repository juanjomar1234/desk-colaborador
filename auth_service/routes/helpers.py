from flask_jwt_extended import get_jwt, get_jwt_identity
from .. import db
from ..models.user import User


def get_current_user():
    """Devuelve el usuario autenticado como dict (vacío si no existe en la BD).

    El token guarda el username como identidad y el id en el claim `uid`;
    ambos deben coincidir para que un username reutilizado o el login de
    pruebas no hereden los privilegios de otra cuenta.
    """
    uid = get_jwt().get('uid')
    if uid is None:
        return {}
    user = db.session.get(User, uid)
    if not user or user.username != get_jwt_identity():
        return {}
    return user.to_dict()
