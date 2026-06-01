from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from app import db

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

def transactional(f):
    """
    Decorador que envuelve la función en una transacción de base de datos.
    Hace commit() si todo sale bien, o rollback() si hay cualquier excepción.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            # Ejecuta la función del servicio
            result = f(*args, **kwargs)
            db.session.commit()
            return result
        except Exception as e:
            db.session.rollback()
            # Lanzamos el error hacia arriba para que la ruta lo capture y envíe el status 500
            raise e 
    return wrapper