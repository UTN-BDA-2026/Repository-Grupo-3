from typing import List

from app.extensions import db
from app.models import Administrador

from .repository import (Repository_add, Repository_delete, Repository_get,
                         Repository_update)


class AdministradorRepository(Repository_add, Repository_get, Repository_delete):
    def add(self, entity: Administrador) -> Administrador:
        try:
            db.session.add(entity)
            db.session.commit()
            return entity
        except Exception as e:
            db.session.rollback()  # Deshace la transacción si hay un error
            raise e  # Propaga la excepción para manejo externo

    def get_all(self) -> List[Administrador]:
        return Administrador.query.all()

    def get_by_id(self, id: int) -> Administrador:
        return Administrador.query.get(id)

    def delete(self, id: int) -> bool:
        try:
            Administrador = self.get_by_id(id)
            if Administrador:
                db.session.delete(Administrador)  
                db.session.commit()  
                return True
            return False
        except Exception as e:
            db.session.rollback()  # Deshace la transacción si hay un error
            raise e  # Propaga la excepción para manejo externo
