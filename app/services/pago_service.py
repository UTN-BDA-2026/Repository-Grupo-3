from app.models import Pago
from app.repositories.pago_repository import PagoRepository
from app.services.reserva_services import ReservaService


class PagoService:
    def __init__(self):
        self.repository = PagoRepository()
        self.reserva_service = ReservaService()
    def create_pago(self, data):
        pago = self.repository.create(data)
        if pago:
            self.reserva_service.recalcular_saldo(pago.reserva_id)
        return pago

    def delete_pago(self, pago_id: int) -> bool:
        pago = self.repository.get_by_id(pago_id)
        if not pago:
            return False
        
        reserva_id = pago.reserva_id
        self.repository.delete(pago)
        
        self.reserva_service.recalcular_saldo(reserva_id)
        
        return True