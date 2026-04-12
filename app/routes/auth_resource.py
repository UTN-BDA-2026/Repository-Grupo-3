import os

import sentry_sdk
from flask import Blueprint, request
from flask_jwt_extended import create_access_token

from app.config.response_builder import ResponseBuilder
from app.extensions import db
from app.models import Persona
from app.repositories import PersonaRepository
from app.services import NotificationService

Auth = Blueprint('Auth', __name__)

@Auth.route('/login', methods=['POST'])
def login():
    # Instanciamos dentro para evitar RuntimeError de contexto
    repo = PersonaRepository()
    response_builder = ResponseBuilder()
    
    try:
        data = request.get_json()
        if not data:
            return response_builder.add_message("No se proporcionaron datos").add_status_code(400).build(), 400

        correo = data.get("correo")
        password = data.get("password")

        if not correo or not password:
            return response_builder.add_message("Correo y contraseña son requeridos").add_status_code(400).build(), 400

        user = repo.get_by_email(correo)

        #VALIDACIÓN: Revisar si el usuario existe pero está inactivo (Soft Delete)
        if user and hasattr(user, 'activo') and not user.activo:
            return response_builder.add_message("Tu cuenta ha sido desactivada. Por favor, regístrate de nuevo para reactivarla.").add_status_code(403).build(), 403

        # Si el usuario existe, está activo y la contraseña es correcta
        if user and user.check_password(password):
            # Configuramos el usuario en Sentry para rastreo de errores
            sentry_sdk.set_user({"id": user.id, "email": user.correo, "role": user.tipo})

            additional_claims = {
                "role": user.tipo,
                "email": user.correo,
                "username": f"{user.nombre} {user.apellido}"
            }
            
            # Creamos el token JWT
            access_token = create_access_token(
                identity=str(user.id),
                additional_claims=additional_claims
            )

            return response_builder.add_message("Inicio de sesión exitoso").add_data({"token": access_token}).add_status_code(200).build(), 200

        # Si no existe o la contraseña es mala
        return response_builder.add_message("Credenciales inválidas").add_status_code(401).build(), 401

    except Exception as e:
        db.session.rollback() # Limpia la conexión si algo falló en la consulta
        return response_builder.add_message("Error interno en el login").add_status_code(500).add_data(str(e)).build(), 500
@Auth.route('/forgot-password', methods=['POST'])
def forgot_password():
    repo = PersonaRepository()
    notification_service = NotificationService()
    response_builder = ResponseBuilder()
    
    try:
        data = request.get_json()
        correo = data.get("correo")

        if not correo:
            return response_builder.add_message("El correo es requerido").add_status_code(400).build(), 400

        user = repo.get_by_email(correo)
        if user:
            token = user.get_reset_token()
            frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
            reset_link = f"{frontend_url}/reset-password/{token}"
            
            # Lógica para enviar el email
            notification_service.send_password_reset_email(
                to_email=user.correo,
                user_name=user.nombre,
                reset_link=reset_link
            )

        # Mensaje genérico por seguridad
        return response_builder.add_message(
            "Si existe una cuenta con ese correo, se ha enviado un enlace para restablecer la contraseña."
        ).add_status_code(200).build(), 200
        
    except Exception as e:
        db.session.rollback()
        return response_builder.add_message("Error procesando solicitud de contraseña").add_status_code(500).add_data(str(e)).build(), 500

@Auth.route('/reset-password', methods=['POST'])
def reset_password():
    repo = PersonaRepository()
    response_builder = ResponseBuilder()
    
    try:
        data = request.get_json()
        token = data.get("token")
        new_password = data.get("new_password")

        if not token or not new_password:
            return response_builder.add_message("El token y la nueva contraseña son requeridos.").add_status_code(400).build(), 400

        # Verificamos la validez del token
        user = Persona.verify_reset_token(token)
        if not user:
            return response_builder.add_message("El token es inválido o ha expirado.").add_status_code(400).build(), 400

        # Actualizamos y confirmamos cambios
        user.set_password(new_password)
        repo.commit() # Guardamos los cambios en la base de datos

        return response_builder.add_message("Tu contraseña ha sido actualizada con éxito.").add_status_code(200).build(), 200
        
    except Exception as e:
        db.session.rollback()
        return response_builder.add_message("Error al actualizar la contraseña").add_status_code(500).add_data(str(e)).build(), 500