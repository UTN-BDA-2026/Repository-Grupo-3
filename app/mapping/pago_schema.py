from marshmallow import Schema, fields, post_load

from app.models import Pago


class PagoSchema(Schema):
    id = fields.Int(dump_only=True)
    monto = fields.Float(required=True)
    fecha_pago = fields.DateTime(dump_only=True)
    reserva_id = fields.Int(load_only=True)

    @post_load
    def make_pago(self, data, **kwargs):
        return Pago(**data)