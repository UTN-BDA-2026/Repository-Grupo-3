from typing import List

from app.extensions import db
from app.models import Administrador

from .repository import (Repository_add, Repository_delete, Repository_get,
                         Repository_update)


class AdministradorRepository(Repository_add, Repository_get, Repository_delete):
    def add(self, entity: Administrador) -> Administrador:
        # Añadimos la entidad a la sesión.
        # El decorador @transactional del servicio hará el commit()
        db.session.add(entity)
        return entity

    def get_all(self) -> List[Administrador]:
        return Administrador.query.all()

    def get_by_id(self, id: int) -> Administrador:
        return Administrador.query.get(id)

    def delete(self, id: int) -> bool:
        # Corregido: 'administrador' en minúscula para no pisar la clase del Modelo
        administrador = self.get_by_id(id)
        if administrador:
            # Marcamos para eliminar en esta sesión
            db.session.delete(administrador)  
            return True
        return False