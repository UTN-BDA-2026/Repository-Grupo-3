from datetime import datetime

from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app.config.response_builder import ResponseBuilder
from app.extensions import db, limiter
from app.mapping import GastoSchema, ResponseSchema
from app.services.gasto_service import GastoService
from app.utils.decorators import admin_required

GastoBP = Blueprint('Gasto', __name__)

@GastoBP.route('/gasto', methods=['GET'])
@jwt_required()
@admin_required()
@limiter.limit("100 per minute")
def all():
    service = GastoService()
    gasto_schema = GastoSchema()
    response_builder = ResponseBuilder()
    
    try:
        today = datetime.utcnow()
        month = request.args.get('mes', default=today.month, type=int)
        year = request.args.get('anio', default=today.year, type=int)

        gastos = service.get_all(month=month, year=year)
        data = gasto_schema.dump(gastos, many=True)
        
        response_builder.add_data(data).add_status_code(200).add_message("Gastos encontrados")
        return response_builder.build(), 200
    except Exception as e:
        db.session.rollback()
        response_builder.add_message(f"Error al obtener gastos: {str(e)}").add_status_code(500)
        return response_builder.build(), 500

@GastoBP.route('/gasto', methods=['POST'])
@jwt_required()
@admin_required()
def add():
    service = GastoService()
    gasto_schema = GastoSchema()
    response_builder = ResponseBuilder()
    
    try:
        json_data = request.get_json()
        if not json_data:
            raise ValidationError("No data provided")

        gasto = gasto_schema.load(json_data)
        nuevo_gasto = service.add(gasto)
        data = gasto_schema.dump(nuevo_gasto)
        
        response_builder.add_data(data).add_status_code(201).add_message("Gasto registrado")
        return response_builder.build(), 201
    except ValidationError as err:
        db.session.rollback()
        return response_builder.add_message("Error de validación").add_data(err.messages).add_status_code(422).build(), 422
    except Exception as e:
        db.session.rollback()
        return response_builder.add_message(str(e)).add_status_code(500).build(), 500

@GastoBP.route('/gasto/<int:id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete(id):
    service = GastoService()
    response_builder = ResponseBuilder()
    
    try:
        if service.delete(id):
            response_builder.add_message("Gasto eliminado").add_status_code(200)
            return response_builder.build(), 200
        else:
            response_builder.add_message("Gasto no encontrado").add_status_code(404)
            return response_builder.build(), 404
    except Exception as e:
        db.session.rollback()
        return response_builder.add_message(str(e)).add_status_code(500).build(), 500