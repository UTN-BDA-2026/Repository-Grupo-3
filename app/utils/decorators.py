from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request


def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            # Verifica que hay un token válido
            verify_jwt_in_request()
            # Obtiene los "claims" (datos adicionales) del token
            claims = get_jwt()
            # Si el rol es 'administrador', permite el acceso
            if claims.get("role") == "administrador":
                return fn(*args, **kwargs)
            else:
                # Si no, deniega el acceso
                return jsonify(message="¡Acceso solo para administradores!"), 403
        return decorator
    return wrapper