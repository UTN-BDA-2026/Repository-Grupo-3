from flask import request

from app.models.log import Log
from app.repositories.log_repository import LogRepository


class LogService:

    def __init__(self):
        self.repo = LogRepository()

    def registrar(self, accion: str, descripcion: str = None,
                  entidad: str = None, entidad_id: int = None,
                  usuario_id: int = None, resultado: str = 'exitoso') -> Log:
        ip = request.remote_addr if request else None
        log = Log(
            accion=accion,
            descripcion=descripcion,
            entidad=entidad,
            entidad_id=entidad_id,
            usuario_id=usuario_id,
            resultado=resultado,
            ip=ip,
        )
        return self.repo.add(log)

    def obtener_todos(self, limit: int = 200):
        return self.repo.get_all(limit)

    def obtener_por_usuario(self, usuario_id: int, limit: int = 100):
        return self.repo.get_by_usuario(usuario_id, limit)

    def obtener_por_accion(self, accion: str, limit: int = 100):
        return self.repo.get_by_accion(accion, limit)

    def obtener_por_rango(self, desde, hasta, limit: int = 200):
        return self.repo.get_by_rango_fechas(desde, hasta, limit)