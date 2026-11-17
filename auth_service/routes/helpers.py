from flask_jwt_extended import get_jwt_identity
from ..models.user import User


def get_current_user():
    """Devuelve el usuario autenticado como dict (vacío si no existe en la BD).

    El token JWT guarda el username como identidad; se resuelve contra la BD
    para obtener su id y rol.
    """
    identity = get_jwt_identity()
    if isinstance(identity, dict):
        return identity
    user = User.query.filter_by(username=identity).first()
    return user.to_dict() if user else {}
