from dataclasses import dataclass
from datetime import datetime

from app.extensions import db


@dataclass
class Gasto(db.Model):
    __tablename__ = 'gasto'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descripcion = db.Column(db.String(200), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(50), nullable=False) # 'Servicios', 'Insumos', 'Otros'
    fecha = db.Column(db.Date, nullable=False, default=datetime.utcnow)