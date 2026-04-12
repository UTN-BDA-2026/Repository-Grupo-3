
from dataclasses import dataclass

from app.extensions import db

from .persona import Persona


@dataclass
class Usuario(Persona):
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, db.ForeignKey('persona.id'), primary_key=True)
    
    reservas = db.relationship('Reserva', back_populates='usuario')

    __mapper_args__ = {
        'polymorphic_identity': 'usuario',
    }