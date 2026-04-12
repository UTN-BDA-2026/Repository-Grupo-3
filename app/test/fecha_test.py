from datetime import date

import pytest

from app import create_app, db
from app.models import Fecha
from app.services import FechaService


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def fecha_service():
    return FechaService()

def test_agregar_fecha(app, fecha_service):
    with app.app_context():
        fecha = Fecha(dia=date(2025, 1, 1))
        agregada = fecha_service.add(fecha)
        assert agregada.id is not None
        assert agregada.estado == 'disponible'

def test_buscar_fecha(app, fecha_service):
    with app.app_context():
        fecha = Fecha(dia=date(2025, 2, 2))
        agregada = fecha_service.add(fecha)
        encontrada = fecha_service.find(agregada.id)
        assert encontrada is not None

def test_eliminar_fecha(app, fecha_service):
    with app.app_context():
        fecha = Fecha(dia=date(2025, 3, 3))
        agregada = fecha_service.add(fecha)

        # Esta llamada ahora usará el contenedor de Redis
        eliminado = fecha_service.delete(agregada.id)
        assert eliminado is True

        buscada = fecha_service.find(agregada.id)
        assert buscada is None