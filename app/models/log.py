from datetime import datetime
from app.extensions import db


class Log(db.Model):
    __tablename__ = 'log'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    accion = db.Column(db.String(100), nullable=False)
    entidad = db.Column(db.String(50), nullable=True)
    entidad_id = db.Column(db.Integer, nullable=True)
    descripcion = db.Column(db.Text, nullable=True)
    ip = db.Column(db.String(45), nullable=True)
    resultado = db.Column(db.String(20), nullable=False, default='exitoso')
    usuario_id = db.Column(db.Integer, nullable=True)