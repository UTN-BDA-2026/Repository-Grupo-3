from app.models import Pago
from app.repositories.pago_repository import PagoRepository
from app.services.reserva_services import ReservaService
from app.utils.decorators import transactional
from app.extensions import db

class PagoService:
    def __init__(self):
        self.repository = PagoRepository()
        self.reserva_service = ReservaService()
        
    @transactional
    def create_pago(self, data):
        pago = self.repository.create(data)
        if pago:
            # Empujamos el cambio a la base de datos (sin cerrar transacción) 
            # para que recalcular_saldo vea este nuevo pago al hacer la suma.
            db.session.flush() 
            self.reserva_service.recalcular_saldo(pago.reserva_id)
            
        # El decorador @transactional hará el commit() final al retornar
        return pago

    @transactional
    def delete_pago(self, pago_id: int) -> bool:
        pago = self.repository.get_by_id(pago_id)
        if not pago:
            return False
        
        reserva_id = pago.reserva_id
        self.repository.delete(pago)
        
        # Empujamos la eliminación a la base de datos 
        # para que recalcular_saldo ya no cuente este pago.
        db.session.flush()
        
        self.reserva_service.recalcular_saldo(reserva_id)
        
        # El decorador @transactional hará el commit() final al retornar
        return True