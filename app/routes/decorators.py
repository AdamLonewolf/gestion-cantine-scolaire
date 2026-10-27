from functools import wraps
from flask import abort
from flask_login import current_user

def role_required(*roles):
    """
    Décorateur vérifiant que l'utilisateur connecté possède l'un des rôles autorisés.
    Renvoie une erreur 403 Forbidden si le rôle n'est pas suffisant.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401) # pragma: no cover
            if not current_user.has_role(*roles):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
