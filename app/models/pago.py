from dataclasses import dataclass
from datetime import datetime

from app.extensions import db


@dataclass
class Pago(db.Model):
    __tablename__ = 'pago'
    __table_args__ = (
        db.Index('idx_pago_reserva_id', 'reserva_id'), 
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    monto = db.Column(db.Float, nullable=False)
    fecha_pago = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relación con Reserva
    reserva_id = db.Column(db.Integer, db.ForeignKey('reserva.id'), nullable=False)
    reserva = db.relationship('Reserva', back_populates='pagos', lazy='select')