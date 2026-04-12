from dataclasses import dataclass

from app.extensions import db

from .persona import Persona 


@dataclass
class Administrador(Persona):
    __tablename__ = 'administrador'

    id = db.Column(db.Integer, db.ForeignKey('persona.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'administrador',
    }