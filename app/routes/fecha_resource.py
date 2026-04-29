from datetime import datetime

import sentry_sdk
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError

from app.config.response_builder import ResponseBuilder
from app.extensions import db, limiter, cache
from app.mapping import FechaSchema, ResponseSchema
from app.services import FechaService
from app.utils.decorators import admin_required

Fecha = Blueprint('Fecha', __name__)

@Fecha.route('/fecha', methods=['GET'])
@limiter.limit("100 per minute") 
@cache.cached(timeout=30, key_prefix='fechas_all')

def all():
    # Instanciación interna para evitar errores de contexto
    service = FechaService()
    fecha_schema = FechaSchema()
    response_builder = ResponseBuilder()
    
    try:
        data = fecha_schema.dump(service.all(), many=True)
        response_builder.add_message("Fechas encontradas").add_status_code(200).add_data(data)
        return response_builder.build(), 200
    except Exception as e:
        db.session.rollback() # Limpia la conexión
        response_builder.add_message("Error al obtener fechas").add_status_code(500).add_data(str(e))
        return response_builder.build(), 500

@Fecha.route('/fecha/<int:id>', methods=['GET'])
@limiter.limit("100 per minute")

def one(id):
    service = FechaService()
    fecha_schema = FechaSchema()
    response_builder = ResponseBuilder()
    
    try:
        data = service.find(id)
        if data:
            serialized_data = fecha_schema.dump(data)
            response_builder.add_message("Fecha encontrada").add_status_code(200).add_data(serialized_data)
            return response_builder.build(), 200
        else:
            response_builder.add_message("Fecha no encontrada").add_status_code(404).add_data({'id': id})
            return response_builder.build(), 404
    except Exception as e:
        db.session.rollback()
        response_builder.add_message("Error al obtener la fecha").add_status_code(500).add_data(str(e))
        return response_builder.build(), 500

@Fecha.route('/fecha', methods=['POST'])
@limiter.limit("50 per minute")
@admin_required()
@jwt_required()

def add():
    service = FechaService()
    fecha_schema = FechaSchema()
    response_builder = ResponseBuilder()
    
    try:
        json_data = request.json
        if not json_data:
            raise ValidationError("No se proporcionaron datos")

        fecha = fecha_schema.load(json_data)
        data = fecha_schema.dump(service.add(fecha))
        cache.delete('fechas_all') #invalida el cache al crear la fecha
        response_builder.add_message("Fecha creada con éxito").add_status_code(201).add_data(data)
        return response_builder.build(), 201
    except ValidationError as err:
        db.session.rollback()
        response_builder.add_message("Error de validación").add_status_code(422).add_data(err.messages)
        return response_builder.build(), 422
    except Exception as e:
        db.session.rollback()
        response_builder.add_message("Error al crear la fecha").add_status_code(500).add_data(str(e))
        return response_builder.build(), 500

@Fecha.route('/fecha/<int:id>', methods=['PUT'])
@limiter.limit("50 per minute")
@admin_required()
@jwt_required()

def update(id):
    service = FechaService()
    fecha_schema = FechaSchema()
    response_builder = ResponseBuilder()
    
    try:
        json_data = request.json
        if not json_data:
            raise ValidationError("No se proporcionaron datos para actualizar.")

        # Buscamos la fecha para obtener el precio anterior antes de actualizar
        fecha_actual = service.find(id)
        if not fecha_actual:
            response_builder.add_message("Fecha no encontrada").add_status_code(404)
            return response_builder.build(), 404
            
        precio_anterior = fecha_actual.valor_estimado
        
        updated_fecha = service.update(id, json_data)
        admin_id = get_jwt_identity()
        nuevo_precio = updated_fecha.valor_estimado
        
        sentry_sdk.capture_message(
            f"Admin ID {admin_id} cambió el precio del día {updated_fecha.dia} de ${precio_anterior} a ${nuevo_precio}.",
            level="info"
        )
        
        data = fecha_schema.dump(updated_fecha)
        cache.delete('fechas_all') #invalida el cache al actualizar la fecha
        response_builder.add_message("Fecha actualizada con éxito").add_status_code(200).add_data(data)
        return response_builder.build(), 200
        
    except (ValidationError, ValueError) as err:
        db.session.rollback()
        response_builder.add_message("Error de validación").add_status_code(422).add_data(str(err))
        return response_builder.build(), 422
    except Exception as e:
        db.session.rollback()
        response_builder.add_message("Error al actualizar la fecha").add_status_code(500).add_data(str(e))
        return response_builder.build(), 500

@Fecha.route('/fecha/<int:id>', methods=['DELETE'])
@limiter.limit("10 per minute")
@admin_required()
@jwt_required()

def delete(id):
    service = FechaService()
    response_builder = ResponseBuilder()
    
    try:
        if service.delete(id):
            cache.delete('fechas_all') #invalida el cache al eliminar la fecha
            response_builder.add_message("Fecha eliminada").add_status_code(200).add_data({'id': id})
            return response_builder.build(), 200
        else:
            response_builder.add_message("Fecha no encontrada").add_status_code(404).add_data({'id': id})
            return response_builder.build(), 404
    except Exception as e:
        db.session.rollback()
        response_builder.add_message("Error al eliminar la fecha").add_status_code(500).add_data(str(e))
        return response_builder.build(), 500

@Fecha.route('/fecha/by-date/<string:date_string>', methods=['GET'])
@limiter.limit("100 per minute")
def get_or_create_by_date(date_string):
    service = FechaService()
    fecha_schema = FechaSchema()
    response_builder = ResponseBuilder()
    
    try:
        dia = datetime.strptime(date_string, '%Y-%m-%d').date()
        fecha_obj = service.get_or_create(dia)
        serialized_data = fecha_schema.dump(fecha_obj)
        response_builder.add_message("Fecha encontrada o creada").add_status_code(200).add_data(serialized_data)
        return response_builder.build(), 200

    except ValueError:
        response_builder.add_message("Formato de fecha inválido. Usar YYYY-MM-DD.").add_status_code(400)
        return response_builder.build(), 400
    except Exception as e:
        db.session.rollback()
        response_builder.add_message("Error procesando la fecha").add_status_code(500).add_data(str(e))
        return response_builder.build(), 500