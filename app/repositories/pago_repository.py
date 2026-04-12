from app.extensions import db
from app.models import Pago, Reserva


class PagoRepository:
    def get_by_id(self, pago_id: int) -> Pago:
        return Pago.query.get(pago_id)

    def delete(self, pago: Pago):
        db.session.delete(pago)
        db.session.commit()