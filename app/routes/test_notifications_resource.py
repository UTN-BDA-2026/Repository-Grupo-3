from flask import Blueprint, jsonify

from app.tasks import check_pending_reservations, check_upcoming_reservations

# Creamos un nuevo Blueprint para las rutas de prueba
TestNotifications = Blueprint('TestNotifications', __name__)

@TestNotifications.route('/test/pending', methods=['GET'])
def test_pending():
    """
    Endpoint para ejecutar manualmente la tarea que revisa reservas pendientes.
    """
    print("--- EJECUTANDO PRUEBA DE NOTIFICACIÓN PENDIENTE ---")
    try:
        check_pending_reservations()
        return jsonify(message="Tarea de reservas pendientes ejecutada. Revisa tu celular."), 200
    except Exception as e:
        return jsonify(message=f"Error al ejecutar la tarea: {str(e)}"), 500


@TestNotifications.route('/test/upcoming', methods=['GET'])
def test_upcoming():
    """
    Endpoint para ejecutar manually la tarea que revisa reservas próximas.
    """
    print("--- EJECUTANDO PRUEBA DE NOTIFICACIÓN PRÓXIMA ---")
    try:
        check_upcoming_reservations()
        return jsonify(message="Tarea de reservas próximas ejecutada. Revisa tu celular."), 200
    except Exception as e:
        return jsonify(message=f"Error al ejecutar la tarea: {str(e)}"), 500