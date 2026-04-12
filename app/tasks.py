from datetime import datetime, timedelta

from app.models import Reserva
from app.services.push_notification_service import PushNotificationService


def check_pending_reservations():
    """
    Busca reservas pendientes y envía una notificación si encuentra alguna.
    IMPORTANTE: Esta función ahora asume que se ejecuta dentro de un contexto de aplicación.
    """
    pending_reservas = Reserva.query.filter_by(estado='pendiente').count()
    
    if pending_reservas > 0:
        push_service = PushNotificationService()
        message = f"Tienes {pending_reservas} reserva(s) pendiente(s) de aprobación."
        push_service.send_notification(message, title="Reservas Pendientes")
        print(f"Tarea 'check_pending_reservations' ejecutada: {pending_reservas} pendientes encontradas.")

def check_upcoming_reservations():
    """
    Busca reservas confirmadas para los próximos días y envía un recordatorio.
    IMPORTANTE: Esta función ahora asume que se ejecuta dentro de un contexto de aplicación.
    """
    today = datetime.utcnow().date()
    
    # Buscamos reservas para mañana
    upcoming_reservas = Reserva.query.join(Reserva.fecha).filter(
        Reserva.estado == 'confirmada',
        Reserva.fecha.has(dia=today + timedelta(days=1))
    ).all()
    
    if upcoming_reservas:
        push_service = PushNotificationService()
        for reserva in upcoming_reservas:
            user = reserva.usuario
            event_date = reserva.fecha.dia.strftime('%d/%m/%Y')
            message = f"Recordatorio: Mañana es el evento de {user.nombre} {user.apellido} ({event_date})."
            push_service.send_notification(message, title="Evento Próximo")
            print(f"Tarea 'check_upcoming_reservations' ejecutada: Notificación enviada para la reserva de {user.nombre}.")