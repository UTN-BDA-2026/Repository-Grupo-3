from flask import Blueprint, request
from marshmallow import ValidationError

from app.config.response_builder import ResponseBuilder
from app.extensions import limiter
from app.mapping import PersonaSchema, ResponseSchema
from app.services import PersonaService

Persona = Blueprint('Persona', __name__)

@Persona.route('/persona', methods=['GET'])
@limiter.limit("50 per minute")
def all():
    # Instanciación interna para evitar RuntimeError fuera del contexto
    service = PersonaService()
    persona_schema = PersonaSchema()
    response_schema = ResponseSchema()
    response_builder = ResponseBuilder()
    
    try:
        data = persona_schema.dump(service.all(), many=True)
        response_builder.add_message("Persona found").add_status_code(200).add_data(data)
        return response_schema.dump(response_builder.build()), 200
    except Exception as e:
        response_builder.add_message("Error fetching Persona").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500

@Persona.route('/persona/<int:id>', methods=['GET'])
@limiter.limit("50 per minute")
def one(id):
    service = PersonaService()
    persona_schema = PersonaSchema()
    response_schema = ResponseSchema()
    response_builder = ResponseBuilder()
    
    try:
        data = service.find(id)
        if data:
            serialized_data = persona_schema.dump(data)
            response_builder.add_message("Persona found").add_status_code(200).add_data(serialized_data)
            return response_schema.dump(response_builder.build()), 200
        else:
            response_builder.add_message("Persona not found").add_status_code(404).add_data({'id': id})
            return response_schema.dump(response_builder.build()), 404
    except Exception as e:
        response_builder.add_message("Error fetching Persona").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500

@Persona.route('/persona', methods=['POST'])
@limiter.limit("50 per minute")
def add():
    service = PersonaService()
    persona_schema = PersonaSchema()
    response_schema = ResponseSchema()
    response_builder = ResponseBuilder()
    
    try:
        json_data = request.json
        if not json_data:
            raise ValidationError("No data provided")

        persona = persona_schema.load(json_data)
        data = persona_schema.dump(service.add(persona))
        response_builder.add_message("Persona created").add_status_code(201).add_data(data)
        return response_schema.dump(response_builder.build()), 201
    except ValidationError as err:
        response_builder.add_message("Validation error").add_status_code(422).add_data(err.messages)
        return response_schema.dump(response_builder.build()), 422
    except Exception as e:
        response_builder.add_message("Error creating Persona").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500

@Persona.route('/persona/<int:id>', methods=['PUT'])
@limiter.limit("50 per minute")
def update(id):
    service = PersonaService()
    persona_schema = PersonaSchema()
    response_schema = ResponseSchema()
    response_builder = ResponseBuilder()
    
    try:
        json_data = request.json
        if not json_data:
            raise ValidationError("No data provided")

        persona = persona_schema.load(json_data)
        updated_persona = service.update(id, persona)
        if not updated_persona:
            response_builder.add_message("Persona not found").add_status_code(404).add_data({'id': id})
            return response_schema.dump(response_builder.build()), 404

        data = persona_schema.dump(updated_persona)
        response_builder.add_message("Persona updated").add_status_code(200).add_data(data)
        return response_schema.dump(response_builder.build()), 200
    except ValidationError as err:
        response_builder.add_message("Validation error").add_status_code(422).add_data(err.messages)
        return response_schema.dump(response_builder.build()), 422
    except Exception as e:
        response_builder.add_message("Error updating Persona").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500

@Persona.route('/persona/<int:id>', methods=['DELETE'])
@limiter.limit("50 per minute")
def delete(id):
    service = PersonaService()
    response_schema = ResponseSchema()
    response_builder = ResponseBuilder()
    
    try:
        if service.delete(id):
            response_builder.add_message("Persona deleted").add_status_code(200).add_data({'id': id})
            return response_schema.dump(response_builder.build()), 200
        else:
            response_builder.add_message("Persona not found").add_status_code(404).add_data({'id': id})
            return response_schema.dump(response_builder.build()), 404
    except Exception as e:
        response_builder.add_message("Error deleting Persona").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500