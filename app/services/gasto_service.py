from typing import List

from app.models import Gasto
from app.repositories.gasto_repository import GastoRepository
from app.utils.decorators import transactional

class GastoService:
    def __init__(self):
        self.repository = GastoRepository()

    def get_all(self, month=None, year=None) -> List[Gasto]:
        return self.repository.get_all(month=month, year=year)

    def get_desglose_para_grafico(self, month: int, year: int) -> list:
        # 1. Le pide los datos crudos al repositorio
        agrupados = self.repository.get_agrupados_por_categoria(month, year)
        
        # 2. Aplica la lógica de negocio (colores y formato para el frontend)
        PALETA_COLORES = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']
        desglose = []
        for index, row in enumerate(agrupados):
            color = PALETA_COLORES[index % len(PALETA_COLORES)]
            desglose.append({
                "name": row[0] or "Otros", 
                "value": float(row[1]),
                "color": color
            })
            
        return desglose

    @transactional
    def add(self, gasto: Gasto) -> Gasto:
        return self.repository.add(gasto)

    @transactional
    def delete(self, gasto_id: int) -> bool:
        return self.repository.delete(gasto_id)