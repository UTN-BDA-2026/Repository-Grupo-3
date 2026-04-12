from datetime import date

import pytest

from app import create_app, db
from app.models import Fecha, Reserva, Usuario
from app.services import FechaService, ReservaService


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def reserva_service():
    return ReservaService()

@pytest.fixture
def fecha_service():
    return FechaService()

@pytest.fixture
def setup_db(app):
    """Crea un usuario y una fecha y DEVUELVE SUS IDs."""
    with app.app_context():
        usuario = Usuario(nombre="Test", apellido="User", dni=123456, correo="test@user.com")
        fecha_disponible = Fecha(dia=date(2025, 12, 25), estado='disponible')
        db.session.add_all([usuario, fecha_disponible])
        db.session.commit()
        # --- CORRECCIÓN CLAVE: Devolver solo los IDs ---
        return usuario.id, fecha_disponible.id

def test_crear_reserva_exitosa(app, reserva_service, fecha_service, setup_db):
    with app.app_context():
        usuario_id, fecha_id = setup_db

        # Ahora creamos la reserva usando los IDs directamente
        nueva_reserva = Reserva(usuario_id=usuario_id, fecha_id=fecha_id)
        reserva_creada = reserva_service.add(nueva_reserva)
        
        assert reserva_creada is not None
        assert reserva_creada.id is not None
        
        fecha_actualizada = fecha_service.find(fecha_id)
        assert fecha_actualizada.estado == 'reservada'

def test_fallo_al_reservar_fecha_no_disponible(app, reserva_service, setup_db):
    with app.app_context():
        usuario_id, fecha_id = setup_db

        # Ocupamos la fecha con una primera reserva
        reserva_service.add(Reserva(usuario_id=usuario_id, fecha_id=fecha_id))
        
        # Intentamos reservar la misma fecha de nuevo
        segunda_reserva = Reserva(usuario_id=usuario_id, fecha_id=fecha_id)
        
        with pytest.raises(Exception, match="La fecha seleccionada ya no está disponible"):
            reserva_service.add(segunda_reserva)

def test_eliminar_reserva(app, reserva_service, setup_db):
    with app.app_context():
        usuario_id, fecha_id = setup_db
        
        reserva_a_eliminar = reserva_service.add(Reserva(usuario_id=usuario_id, fecha_id=fecha_id))
        
        eliminado = reserva_service.delete(reserva_a_eliminar.id)
        assert eliminado is True
        
        buscada = reserva_service.find(reserva_a_eliminar.id)
        assert buscada is None