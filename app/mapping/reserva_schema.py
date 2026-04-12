from marshmallow import Schema, fields, post_load

from app.models import Reserva


class ReservaSchema(Schema):
    id = fields.Int(dump_only=True)
    fecha_creacion = fields.DateTime(dump_only=True)
    estado = fields.Str()
    comprobante_url = fields.Str()
    valor_alquiler = fields.Float()
    ip_aceptacion = fields.Str(dump_only=True)
    fecha_aceptacion = fields.DateTime(dump_only=True)
    version_contrato = fields.Str(dump_only=True)
    cantidad_personas = fields.Int()
    usuario = fields.Nested('UsuarioSchema', only=("id", "nombre", "apellido", "correo", "telefono"), dump_only=True)
    fecha = fields.Nested('FechaSchema', only=("id", "dia"), dump_only=True)
    hora_inicio = fields.Time(format='%H:%M', allow_none=True)
    hora_fin = fields.Time(format='%H:%M', allow_none=True)
    
    pagos = fields.Nested('PagoSchema', many=True, dump_only=True)
    saldo_restante = fields.Float(dump_only=True)

    usuario_id = fields.Int(required=True, load_only=True)
    fecha_id = fields.Int(required=True, load_only=True)

    @post_load
    def make_reserva(self, data, **kwargs):
        return Reserva(**data)