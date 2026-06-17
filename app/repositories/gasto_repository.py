from typing import List
from sqlalchemy import extract, func 

from app.extensions import db
from app.models import Gasto
from .repository import Repository_add, Repository_delete, Repository_get

class GastoRepository(Repository_add, Repository_get, Repository_delete):
    
    def add(self, entity: Gasto) -> Gasto:
        # El repositorio solo añade a la sesión de la BD
        db.session.add(entity)
        return entity

    def get_all(self, month=None, year=None) -> List[Gasto]:
        query = Gasto.query
        if year:
            query = query.filter(extract('year', Gasto.fecha) == year)
        if month:
            query = query.filter(extract('month', Gasto.fecha) == month)

        return query.order_by(Gasto.fecha.desc()).all()

    def get_agrupados_por_categoria(self, month: int, year: int):
        """
        Devuelve una lista de tuplas crudas: (categoria, total_gastado)
        """
        return db.session.query(
            Gasto.categoria, 
            func.sum(Gasto.monto).label('total')
        ).filter(
            extract('year', Gasto.fecha) == year,
            extract('month', Gasto.fecha) == month
        ).group_by(Gasto.categoria).all()

    def get_by_id(self, id: int) -> Gasto:
        return Gasto.query.get(id)

    def delete(self, id: int) -> bool:
        gasto = self.get_by_id(id)
        if gasto:
            db.session.delete(gasto)
            return True
        return False