from dataclasses import dataclass
from time import time

import jwt
from flask import current_app
from passlib.hash import pbkdf2_sha256 as sha256

from app.extensions import db


@dataclass
class Persona(db.Model):
    __tablename__ = 'persona'

    id: int = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    apellido: str = db.Column('apellido', db.String, nullable=False, index=True)
    correo: str = db.Column('correo', db.String, unique=True, nullable=False)
    dni: int = db.Column('dni', db.Integer, unique=True, nullable=False)
    nombre: str = db.Column('nombre', db.String, nullable=False, index=True)
    telefono: str = db.Column('telefono', db.String(50), nullable=True)
    password_hash: str = db.Column(db.String(128), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    __mapper_args__ = {
        'polymorphic_identity': 'persona',
        'polymorphic_on': tipo
    }

    def set_password(self, password):
        """Crea un hash seguro de la contraseña."""
        self.password_hash = sha256.hash(password)

    def check_password(self, password):
        """Verifica la contraseña contra el hash almacenado."""
        return sha256.verify(password, self.password_hash)

  
    def get_reset_token(self, expires_in=600):
        """Genera un token de reseteo con tiempo de expiración (600s = 10 min)."""
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['JWT_SECRET_KEY'],
            algorithm='HS256'
        )

    @staticmethod
    def verify_reset_token(token):
        """Verifica el token de reseteo y devuelve la instancia de Persona si es válido."""
        try:
            user_id = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )['reset_password']
            return Persona.query.get(user_id)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None