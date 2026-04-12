import pytest

from app import create_app, db
from app.models import Administrador
from app.services import AdministradorService


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def administrador_service():
    return AdministradorService()

def test_agregar_administrador(app, administrador_service):
    with app.app_context():
        admin = Administrador(nombre="Admin", apellido="Root", dni=999999, correo="admin@root.com")
        agregado = administrador_service.add(admin)
        assert agregado.id is not None
        assert agregado.nombre == "Admin"

def test_buscar_administrador(app, administrador_service):
    with app.app_context():
        admin = Administrador(nombre="Admin", apellido="Find", dni=111, correo="find@me.com")
        agregado = administrador_service.add(admin)
        encontrado = administrador_service.find(agregado.id)
        assert encontrado is not None
        assert encontrado.dni == 111
def test_eliminar_administrador(app, administrador_service):
    with app.app_context():
        admin = Administrador(nombre="Admin", apellido="Delete", dni=222, correo="delete@me.com")
        agregado = administrador_service.add(admin)

        # Esta llamada ahora usará el contenedor de Redis
        eliminado = administrador_service.delete(agregado.id)
        assert eliminado is True

        buscado = administrador_service.find(agregado.id)
        assert buscado is None