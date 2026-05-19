from datetime import datetime

from flask import Blueprint, request
from flask_jwt_extended import get_jwt, jwt_required

from app.config.response_builder import ResponseBuilder
from app.services.log_service import LogService

LogBP = Blueprint('LogBP', __name__)


def _solo_admin():
    claims = get_jwt()
    return claims.get('role') == 'administrador'


@LogBP.route('/logs', methods=['GET'])
@jwt_required()
def get_logs():
    response_builder = ResponseBuilder()
    if not _solo_admin():
        return response_builder.add_message("Acceso denegado").add_status_code(403).build(), 403

    try:
        service = LogService()
        limit = int(request.args.get('limit', 200))

        usuario_id = request.args.get('usuario_id')
        accion = request.args.get('accion')
        desde = request.args.get('desde')
        hasta = request.args.get('hasta')

        if usuario_id:
            logs = service.obtener_por_usuario(int(usuario_id), limit)
        elif accion:
            logs = service.obtener_por_accion(accion, limit)
        elif desde and hasta:
            desde_dt = datetime.strptime(desde, '%Y-%m-%d')
            hasta_dt = datetime.strptime(hasta, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            logs = service.obtener_por_rango(desde_dt, hasta_dt, limit)
        else:
            logs = service.obtener_todos(limit)

        data = [
            {
                "id": l.id,
                "fecha": l.fecha.isoformat(),
                "accion": l.accion,
                "entidad": l.entidad,
                "entidad_id": l.entidad_id,
                "descripcion": l.descripcion,
                "ip": l.ip,
                "resultado": l.resultado,
                "usuario_id": l.usuario_id,
            }
            for l in logs
        ]

        return response_builder.add_message("Logs obtenidos").add_data(data).add_status_code(200).build(), 200

    except Exception as e:
        return response_builder.add_message("Error al obtener logs").add_status_code(500).add_data(str(e)).build(), 500


@LogBP.route('/logs/<int:log_id>', methods=['GET'])
@jwt_required()
def get_log(log_id):
    response_builder = ResponseBuilder()
    if not _solo_admin():
        return response_builder.add_message("Acceso denegado").add_status_code(403).build(), 403

    try:
        from app.repositories.log_repository import LogRepository
        log = LogRepository().get_by_id(log_id)
        if not log:
            return response_builder.add_message("Log no encontrado").add_status_code(404).build(), 404

        data = {
            "id": log.id,
            "fecha": log.fecha.isoformat(),
            "accion": log.accion,
            "entidad": log.entidad,
            "entidad_id": log.entidad_id,
            "descripcion": log.descripcion,
            "ip": log.ip,
            "resultado": log.resultado,
            "usuario_id": log.usuario_id,
        }
        return response_builder.add_message("Log encontrado").add_data(data).add_status_code(200).build(), 200

    except Exception as e:
        return response_builder.add_message("Error").add_status_code(500).add_data(str(e)).build(), 500
    