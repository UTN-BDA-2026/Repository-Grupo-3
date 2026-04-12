from dataclasses import dataclass

from app.extensions import db


@dataclass
class Fecha(db.Model):
    __tablename__ = 'fecha'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dia = db.Column(db.Date, nullable=False, unique=True)
    estado = db.Column(db.String(20), nullable=False, default='disponible')  # 'disponible', 'pendiente', 'reservada'
    valor_estimado = db.Column(db.Float, nullable=False, default=0.0)

    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)

    reserva = db.relationship('Reserva', back_populates='fecha', uselist=False)
