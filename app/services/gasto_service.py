from typing import List

from app.models import Gasto
from app.repositories.gasto_repository import GastoRepository
from app.utils.decorators import transactional

class GastoService:
    def __init__(self):
        self.repository = GastoRepository()

    # Operación de solo lectura: NO lleva decorador
    def get_all(self, month=None, year=None) -> List[Gasto]:
        return self.repository.get_all(month=month, year=year)

    # Operación de escritura: LLEVA decorador
    @transactional
    def add(self, gasto: Gasto) -> Gasto:
        # Llama al repositorio, y al salir, el decorador hace el commit()
        return self.repository.add(gasto)

    # Operación de escritura: LLEVA decorador
    @transactional
    def delete(self, gasto_id: int) -> bool:
        # Llama al repositorio, y al salir, el decorador hace el commit()
        return self.repository.delete(gasto_id)