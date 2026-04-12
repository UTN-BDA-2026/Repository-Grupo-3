from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app.config.response_builder import ResponseBuilder
from app.extensions import db, limiter
from app.mapping import ResponseSchema, UsuarioSchema
from app.services import UsuarioService
from app.utils.decorators import admin_required

Usuario = Blueprint('Usuario', __name__)

@Usuario.route('/usuario', methods=['GET'])
@jwt_required()
@admin_required()
@limiter.limit("60 per minute")
def all():
    # Instanciación interna para evitar RuntimeError y problemas de contexto
    service = UsuarioService()
    usuario_schema = UsuarioSchema()
    response_schema = ResponseSchema()
    response_builder = ResponseBuilder()
    
    try:
        data = usuario_schema.dump(service.all(), many=True)
        response_builder.add_message("Usuarios encontrados").add_status_code(200).add_data(data)
        return response_schema.dump(response_builder.build()), 200
    except Exception as e:
        db.session.rollback() # Limpia la conexión para que no se bloquee el servidor
        response_builder.add_message("Error al obtener usuarios").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500

@Usuario.route('/usuario/<int:id>', methods=['GET'])
@jwt_required()
@admin_required()
@limiter.limit("60 per minute")
def one(id):
    service = UsuarioService()
    usuario_schema = UsuarioSchema()
    response_schema = ResponseSchema()
    response_builder = ResponseBuilder()
    
    try:
        data = service.find(id)
        if data:
            serialized_data = usuario_schema.dump(data)
            response_builder.add_message("Usuario encontrado").add_status_code(200).add_data(serialized_data)
            return response_schema.dump(response_builder.build()), 200
        else:
            response_builder.add_message("Usuario no encontrado").add_status_code(404).add_data({'id': id})
            return response_schema.dump(response_builder.build()), 404
    except Exception as e:
        db.session.rollback()
        response_builder.add_message("Error al obtener usuario").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500

@Usuario.route('/usuario', methods=['POST'])
@limiter.limit("10 per minute")
def add():
    service = UsuarioService()
    usuario_schema = UsuarioSchema()
    response_schema = ResponseSchema()
    response_builder = ResponseBuilder()
    
    try:
        json_data = request.json
        if not json_data:
            raise ValidationError("No se proporcionaron datos")

        usuario = usuario_schema.load(json_data)
        nuevo_usuario = service.add(usuario)
        data = usuario_schema.dump(nuevo_usuario)
        
        response_builder.add_message("Usuario creado con éxito").add_status_code(201).add_data(data)
        return response_schema.dump(response_builder.build()), 201
    except ValidationError as err:
        db.session.rollback()
        response_builder.add_message("Error de validación").add_status_code(422).add_data(err.messages)
        return response_schema.dump(response_builder.build()), 422
    except Exception as e:
        db.session.rollback()
        response_builder.add_message("Error al crear usuario").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500

@Usuario.route('/usuario/<int:id>', methods=['PUT'])
@jwt_required()
@admin_required()
@limiter.limit("10 per minute")
def update(id):
    service = UsuarioService()
    usuario_schema = UsuarioSchema()
    response_schema = ResponseSchema()
    response_builder = ResponseBuilder()
    
    try:
        json_data = request.json
        if not json_data:
            raise ValidationError("No se proporcionaron datos")

        usuario_data = usuario_schema.load(json_data)
        updated_usuario = service.update(id, usuario_data)
        
        if not updated_usuario:
            response_builder.add_message("Usuario no encontrado").add_status_code(404).add_data({'id': id})
            return response_schema.dump(response_builder.build()), 404

        data = usuario_schema.dump(updated_usuario)
        response_builder.add_message("Usuario actualizado").add_status_code(200).add_data(data)
        return response_schema.dump(response_builder.build()), 200
    except ValidationError as err:
        db.session.rollback()
        response_builder.add_message("Error de validación").add_status_code(422).add_data(err.messages)
        return response_schema.dump(response_builder.build()), 422
    except Exception as e:
        db.session.rollback()
        response_builder.add_message("Error al actualizar usuario").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500

@Usuario.route('/usuario/<int:id>', methods=['DELETE'])
@jwt_required()
@admin_required()
@limiter.limit("10 per minute")
def delete(id):
    service = UsuarioService()
    response_schema = ResponseSchema()
    response_builder = ResponseBuilder()
    
    try:
        if service.delete(id):
            response_builder.add_message("Usuario eliminado").add_status_code(200).add_data({'id': id})
            return response_schema.dump(response_builder.build()), 200
        else:
            response_builder.add_message("Usuario no encontrado").add_status_code(404).add_data({'id': id})
            return response_schema.dump(response_builder.build()), 404
            
    except ValueError as ve:
        db.session.rollback()
        response_builder.add_message(str(ve)).add_status_code(400)
        return response_schema.dump(response_builder.build()), 400
        
    except Exception as e:
        db.session.rollback()
        response_builder.add_message("Error al eliminar usuario").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500

    
@Usuario.route('/usuario/buscar', methods=['GET'])
@jwt_required()
@admin_required()
@limiter.limit("120 per minute") # Límite más alto porque el tipeo en vivo genera más peticiones
def search_live():
    service = UsuarioService()
    usuario_schema = UsuarioSchema()
    response_schema = ResponseSchema()
    response_builder = ResponseBuilder()
    
    try:
        
        termino = request.args.get('q', '').strip()
        
        if not termino:
            data = []
        else:
            usuarios_encontrados = service.search(termino)
            data = usuario_schema.dump(usuarios_encontrados, many=True)
            
        response_builder.add_message("Búsqueda exitosa").add_status_code(200).add_data(data)
        return response_schema.dump(response_builder.build()), 200
        
    except Exception as e:
        db.session.rollback()
        response_builder.add_message("Error en búsqueda en vivo").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500