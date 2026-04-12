import os

from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.config import ResponseBuilder
from app.mapping import ResponseSchema

Config = Blueprint('Config', __name__)
response_schema = ResponseSchema()

@Config.route('/payment-info', methods=['GET'])
@jwt_required()
def get_payment_info():
    """
    Endpoint seguro que devuelve información de pago desde las variables de entorno.
    """
    response_builder = ResponseBuilder()
    try:
        # Leemos el alias desde las variables de entorno del servidor
        payment_alias = os.getenv('PAYMENT_ALIAS')

        if not payment_alias:
            # Si el alias no está configurado en el servidor, devolvemos un error
            response_builder.add_message("La información de pago no está configurada.").add_status_code(500)
            return response_schema.dump(response_builder.build()), 500

        # Si todo está bien, enviamos el alias
        data = {"alias": payment_alias}
        response_builder.add_message("Información de pago obtenida.").add_status_code(200).add_data(data)
        return response_schema.dump(response_builder.build()), 200

    except Exception as e:
        response_builder.add_message("Error interno del servidor").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500