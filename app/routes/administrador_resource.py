from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app.config import ResponseBuilder
from app.extensions import limiter  # Usar el limiter global
from app.mapping import AdministradorSchema, ResponseSchema
from app.services import AdministradorService
from app.utils.decorators import admin_required

Administrador = Blueprint('Administrador', __name__)
service = AdministradorService()
administrador_schema = AdministradorSchema()
response_schema = ResponseSchema()

# Aplicar limitadores específicos en las rutas
@Administrador.route('/administrador', methods=['GET'])
@limiter.limit("50 per minute")
@admin_required()
def all():
    response_builder = ResponseBuilder()
    try:
        data = administrador_schema.dump(service.all(), many=True)
        response_builder.add_message("Administrador found").add_status_code(200).add_data(data)
        return response_schema.dump(response_builder.build()), 200
    except Exception as e:
        response_builder.add_message("Error fetching Administrador").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500

@Administrador.route('/administrador/<int:id>', methods=['GET'])
@limiter.limit("50 per minute")
@admin_required()
def one(id):
    response_builder = ResponseBuilder()
    try:
        data = service.find(id)
        if data:
            serialized_data = administrador_schema.dump(data)
            response_builder.add_message("Administrador found").add_status_code(200).add_data(serialized_data)
            return response_schema.dump(response_builder.build()), 200
        else:
            response_builder.add_message("Administrador not found").add_status_code(404).add_data({'id': id})
            return response_schema.dump(response_builder.build()), 404
    except Exception as e:
        response_builder.add_message("Error fetching Administrador").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500

@Administrador.route('/administrador', methods=['POST'])
@limiter.limit("50 per minute")
#@admin_required() comentado para poder agregar admin por primera vez
def add():
    response_builder = ResponseBuilder()
    try:
        json_data = request.json
        if not json_data:
            raise ValidationError("No data provided")

        administrador = administrador_schema.load(json_data)
        data = administrador_schema.dump(service.add(administrador))
        response_builder.add_message("Administrador created").add_status_code(201).add_data(data)
        return response_schema.dump(response_builder.build()), 201
    except ValidationError as err:
        response_builder.add_message("Validation error").add_status_code(422).add_data(err.messages)
        return response_schema.dump(response_builder.build()), 422
    except Exception as e:
        response_builder.add_message("Error creating Administrador").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500

@Administrador.route('/administrador/<int:id>', methods=['PUT'])
@limiter.limit("50 per minute")
@admin_required()
def update(id):
    response_builder = ResponseBuilder()
    try:
        json_data = request.json
        if not json_data:
            raise ValidationError("No data provided")

        administrador = administrador_schema.load(json_data)
        updated_administrador = service.update(id, administrador)
        if not updated_administrador:
            response_builder.add_message("Administrador not found").add_status_code(404).add_data({'id': id})
            return response_schema.dump(response_builder.build()), 404

        data = administrador_schema.dump(updated_administrador)
        response_builder.add_message("Administrador updated").add_status_code(200).add_data(data)
        return response_schema.dump(response_builder.build()), 200
    except ValidationError as err:
        response_builder.add_message("Validation error").add_status_code(422).add_data(err.messages)
        return response_schema.dump(response_builder.build()), 422
    except Exception as e:
        response_builder.add_message("Error updating Administrador").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500

@Administrador.route('/administrador/<int:id>', methods=['DELETE'])
@limiter.limit("30 per minute")
@admin_required()
def delete(id):
    response_builder = ResponseBuilder()
    try:
        if service.delete(id):
            response_builder.add_message("Administrador deleted").add_status_code(200).add_data({'id': id})
            return response_schema.dump(response_builder.build()), 200
        else:
            response_builder.add_message("Administrador not found").add_status_code(404).add_data({'id': id})
            return response_schema.dump(response_builder.build()), 404
    except Exception as e:
        response_builder.add_message("Error deleting Administrador").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500
    
    