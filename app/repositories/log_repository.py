from typing import List

from app.extensions import db
from app.models.log import Log


class LogRepository:

    def add(self, entity: Log) -> Log:
        try:
            db.session.add(entity)
            db.session.commit()
            return entity
        except Exception as e:
            db.session.rollback()
            raise e

    def get_all(self, limit: int = 200) -> List[Log]:
        return Log.query.order_by(Log.fecha.desc()).limit(limit).all()

    def get_by_id(self, id: int) -> Log:
        return Log.query.get(id)

    def get_by_usuario(self, usuario_id: int, limit: int = 100) -> List[Log]:
        return (Log.query
                .filter_by(usuario_id=usuario_id)
                .order_by(Log.fecha.desc())
                .limit(limit)
                .all())

    def get_by_accion(self, accion: str, limit: int = 100) -> List[Log]:
        return (Log.query
                .filter(Log.accion.ilike(f"%{accion}%"))
                .order_by(Log.fecha.desc())
                .limit(limit)
                .all())

    def get_by_rango_fechas(self, desde, hasta, limit: int = 200) -> List[Log]:
        return (Log.query
                .filter(Log.fecha >= desde, Log.fecha <= hasta)
                .order_by(Log.fecha.desc())
                .limit(limit)
                .all())
    
    