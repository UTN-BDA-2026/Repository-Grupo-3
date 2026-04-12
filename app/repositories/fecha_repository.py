from datetime import date
from typing import List

from app.extensions import db
from app.models import Fecha

from .repository import (Repository_add, Repository_delete, Repository_get,
                         Repository_update)


class FechaRepository(Repository_add, Repository_get, Repository_delete):
    def add(self, entity: Fecha) -> Fecha:
        try:
            db.session.add(entity)  
            db.session.commit()  
            return entity
        except Exception as e:
            db.session.rollback()  # Deshace la transacción si hay un error
            raise e  # Propaga la excepción para manejo externo

    def get_all(self) -> List[Fecha]:
        return Fecha.query.all()

    def get_by_id(self, id: int) -> Fecha:
        return Fecha.query.get(id)

    def delete(self, id: int) -> bool:
        try:
            Fecha = self.get_by_id(id)
            if Fecha:
                db.session.delete(Fecha)  
                db.session.commit()  
                return True
            return False
        except Exception as e:
            db.session.rollback()  # Deshace la transacción si hay un error
            raise e  # Propaga la excepción para manejo externo
    def get_by_dia(self, dia: date) -> Fecha:
        """Busca una entidad de Fecha por su campo de día."""
        return Fecha.query.filter_by(dia=dia).first()
