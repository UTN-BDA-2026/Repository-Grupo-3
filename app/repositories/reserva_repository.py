from typing import List

from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models import Reserva, Usuario

from .repository import (Repository_add, Repository_delete, Repository_get,
                         Repository_update)


class ReservaRepository(Repository_add, Repository_get, Repository_delete):
    def add(self, entity: Reserva) -> Reserva:
        try:
            db.session.add(entity)  
            db.session.commit()  
            return entity
        except Exception as e:
            db.session.rollback()
            raise e
    def get_all_archived(self) -> List[Reserva]:
        """
        Obtiene todas las reservas que han sido marcadas como 'archivada'.
        """
        return Reserva.query.options(
            joinedload(Reserva.usuario),
            joinedload(Reserva.fecha)
        ).filter(Reserva.estado == 'archivada').all()

    def get_by_id(self, id: int) -> Reserva:
        return Reserva.query.options(
            joinedload(Reserva.usuario),
            joinedload(Reserva.fecha)
        ).filter_by(id=id).first()

    def delete(self, id: int) -> bool:
        try:
            reserva = self.get_by_id(id)
            if reserva:
                db.session.delete(reserva)  
                db.session.commit()  
                return True
            return False
        except Exception as e:
            db.session.rollback()
            raise e

    def get_all(self) -> List[Reserva]:
        # Le decimos a la consulta que cargue las relaciones 'usuario' y 'fecha'
        # y que excluya las reservas archivadas.
        return Reserva.query.options(
            joinedload(Reserva.usuario),
            joinedload(Reserva.fecha)
        ).filter(Reserva.estado != 'archivada').all() 

    def get_by_user_id(self, user_id: int) -> List[Reserva]:
        # También excluimos las reservas archivadas de la vista del usuario.
        return Reserva.query.options(
            joinedload(Reserva.usuario),
            joinedload(Reserva.fecha)
        ).filter_by(usuario_id=user_id).filter(Reserva.estado != 'archivada').all() 
        
    def search(self, term: str, limit: int = 15) -> List[Reserva]:
        """Busca reservas filtrando por el nombre, apellido o DNI del cliente asociado, o por estado."""
        search_pattern = f"%{term}%"
        
        # Hacemos un JOIN con Usuario para poder buscar en sus columnas
        return Reserva.query.join(Reserva.usuario).options(
            joinedload(Reserva.usuario),
            joinedload(Reserva.fecha)
        ).filter(
            Reserva.estado != 'archivada', # Omitimos las archivadas en la búsqueda rápida
            db.or_(
                Usuario.nombre.ilike(search_pattern),
                Usuario.apellido.ilike(search_pattern),
                db.cast(Usuario.dni, db.String).ilike(search_pattern),
                Reserva.estado.ilike(search_pattern) # Por si quieres buscar escribiendo "pendiente"
            )
        ).limit(limit).all()