from dataclasses import dataclass
from datetime import datetime
from sqlalchemy import select, func # para el SUM en db

from app.extensions import db


@dataclass
class Reserva(db.Model):
    __tablename__ = 'reserva'
    #indices compuestos para optimizar consultas
    __table_args__ = (
        db.Index('idx_reserva_fecha_id', 'fecha_id'),
        db.Index('idx_reserva_usuario_id', 'usuario_id'),
        db.Index('idx_reserva_estado', 'estado'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    fecha_vencimiento = db.Column(db.DateTime, nullable=True)
    estado = db.Column(db.String(20), nullable=False, default='pendiente', index=True)
    comprobante_url = db.Column(db.String(256), nullable=True)
    valor_alquiler = db.Column(db.Float, nullable=True, default=0.0)
    ip_aceptacion = db.Column(db.String(45), nullable=True) 
    fecha_aceptacion = db.Column(db.DateTime, nullable=True) 
    version_contrato = db.Column(db.String(50), nullable=True, default='1.0') 
    cantidad_personas = db.Column(db.Integer, nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False, index=True)
    fecha_id = db.Column(db.Integer, db.ForeignKey('fecha.id'), nullable=False, index=True)
    hora_inicio = db.Column(db.Time, nullable=True)
    hora_fin = db.Column(db.Time, nullable=True)
    
    
    usuario = db.relationship('Usuario', back_populates='reservas', lazy='select')
    fecha   = db.relationship('Fecha',   back_populates='reserva',  lazy='select')
    
    pagos   = db.relationship('Pago',    back_populates='reserva',  lazy='select')

    @property
    def saldo_restante(self):    #ahora hago un solo SELECT SUM 
        from app.models.pago import Pago
        total_pagado = db.session.execute(
            select(func.coalesce(func.sum(Pago.monto), 0))
            .where(Pago.reserva_id == self.id)
        ).scalar()
        return (self.valor_alquiler or 0) - total_pagado