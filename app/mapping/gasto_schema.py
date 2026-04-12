from marshmallow import Schema, fields, post_load, validate

from app.models import Gasto


class GastoSchema(Schema):
    id = fields.Int(dump_only=True)
    descripcion = fields.Str(required=True, validate=validate.Length(min=3))
    monto = fields.Float(required=True, validate=validate.Range(min=0.01))
    categoria = fields.Str(required=True, validate=validate.OneOf(['Servicios', 'Insumos', 'Otros']))
    fecha = fields.Date(required=True)

    @post_load
    def make_gasto(self, data, **kwargs):
        return Gasto(**data)