import io
import sentry_sdk
from werkzeug.datastructures import FileStorage
from app.extensions import db, cache

from datetime import datetime, timedelta
from app.models import Reserva
from app.services.push_notification_service import PushNotificationService


def check_pending_reservations():
    """
    Busca reservas pendientes y envía una notificación si encuentra alguna.
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
            
            
def procesar_comprobante_y_notificar(app, reserva_id: int, archivo_bytes: bytes,
                                      filename: str, content_type: str, fecha_id: int):
    """
    Tarea en segundo plano: sube el comprobante a R2, actualiza la bd y manda la noti por Telegram
    """
    from app.utils.storage import upload_file_to_r2
    from app.services.push_notification_service import PushNotificationService

    with app.app_context():
        try:
            # Reconstruye el archivo en memoria para subirlo a R2
            archivo_reconstruido = FileStorage(
                stream=io.BytesIO(archivo_bytes),
                filename=filename,
                content_type=content_type
            )

            # Subo a la nube
            archivo_url = upload_file_to_r2(
                archivo_reconstruido,
                folder=f"comprobantes/fecha_{fecha_id}"
            )

            # Actualizo la base de datos
            reserva = db.session.get(Reserva, reserva_id)
            if not reserva:
                return

            if archivo_url:
                reserva.comprobante_url = archivo_url
                db.session.commit()
                
                # Limpio la cache para que el frontend vea la nueva URL
                cache.delete(f'reserva_{reserva_id}')
                cache.delete('reservas')

            #  Notificacion a Telegram
            try:
                u = reserva.usuario
                nombre_cliente = f"{u.nombre} {u.apellido}" if u else "Nuevo Cliente"
                telegram = PushNotificationService()
                mensaje = (
                    f"👤 *Cliente:* {nombre_cliente}\n"
                    f"📅 *Fecha:* {reserva.fecha.dia}\n"
                    f"📋 *Estado:* {reserva.estado.capitalize()}"
                )
                telegram.send_notification(mensaje, title="🆕 ¡Nueva Solicitud de Reserva!")
            except Exception as e:
                sentry_sdk.capture_exception(e)
                print(f"Error Telegram en background: {e}")

        except Exception as e:
            sentry_sdk.capture_exception(e)
            print(f"Error crítico en tarea procesar_comprobante: {e}")            