from typing import List

from sqlalchemy import extract

from app.extensions import db
from app.models import Gasto

from .repository import Repository_add, Repository_delete, Repository_get


class GastoRepository(Repository_add, Repository_get, Repository_delete):
    
    def add(self, entity: Gasto) -> Gasto:
        db.session.add(entity)
        db.session.commit()
        return entity

    def get_all(self, month=None, year=None) -> List[Gasto]:
        """
        Obtiene todos los gastos, con filtros opcionales por mes y año.
        """
        query = Gasto.query
        if year:
            query = query.filter(extract('year', Gasto.fecha) == year)
        if month:
            query = query.filter(extract('month', Gasto.fecha) == month)
        
        return query.order_by(Gasto.fecha.desc()).all()


    def get_by_id(self, id: int) -> Gasto:
        return Gasto.query.get(id)

    def delete(self, id: int) -> bool:
        gasto = self.get_by_id(id)
        if gasto:
            db.session.delete(gasto)
            db.session.commit()
            return True
        return False