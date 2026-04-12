from marshmallow import Schema, fields, post_load, validate

from app.models import Persona


class PersonaSchema(Schema):
    id = fields.Int(dump_only=True)
    apellido = fields.Str(required=True, validate=validate.Length(min=1))
    correo = fields.Email(required=True)
    dni = fields.Int(required=True, validate=validate.Range(min=1))
    nombre = fields.Str(required=True, validate=validate.Length(min=1))
    tipo = fields.Str(dump_only=True)
    telefono = fields.Str(required=False, allow_none=True) 
    @post_load
    def make_persona(self, data, **kwargs):

        return Persona(**data)

