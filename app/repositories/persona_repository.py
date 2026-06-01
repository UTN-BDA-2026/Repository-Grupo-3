from typing import List

from app.extensions import db
from app.models import Persona

from .repository import (Repository_add, Repository_delete, Repository_get,
                         Repository_update)


class PersonaRepository(Repository_add, Repository_get, Repository_delete):
    def add(self, entity: Persona) -> Persona:
        # Solo agregamos a la sesión. El decorador en el servicio hará el commit.
        db.session.add(entity)
        return entity

    def get_all(self) -> List[Persona]:
        return Persona.query.all()

    def get_by_id(self, id: int) -> Persona:
        return Persona.query.get(id)

    def delete(self, id: int) -> bool:
        # Buscamos y marcamos para borrar si existe en esta sesión.
        persona = self.get_by_id(id)
        if persona:
            db.session.delete(persona)
            return True
        return False
        
    def get_by_email(self, correo: str) -> Persona:
        return Persona.query.filter_by(correo=correo).first()