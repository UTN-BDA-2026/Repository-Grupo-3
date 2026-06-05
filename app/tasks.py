import io
import base64
import sentry_sdk
from werkzeug.datastructures import FileStorage
from app.extensions import db, cache
from app.models import Reserva
from app.celery_app import celery 


@celery.task
def procesar_comprobante_y_notificar(reserva_id: int, archivo_b64: str, filename: str, content_type: str, fecha_id: int):
    # Los imports van aquí ADENTRO de la función para evitar errores circulares
    from app.utils.storage import upload_file_to_r2
    from app.services.push_notification_service import PushNotificationService

    try:
        # 1. Decodificamos el Base64 de vuelta a Bytes
        archivo_bytes = base64.b64decode(archivo_b64)

        # 2. Reconstruir el objeto de archivo
        archivo_reconstruido = FileStorage(
            stream=io.BytesIO(archivo_bytes),
            filename=filename,
            content_type=content_type
        )

        # 3. Subir a R2
        archivo_url = upload_file_to_r2(archivo_reconstruido, folder=f"comprobantes/fecha_{fecha_id}")

        # 4. Actualizar la base de datos
        reserva = db.session.get(Reserva, reserva_id)
        if not reserva:
            return

        if archivo_url:
            reserva.comprobante_url = archivo_url
            db.session.commit()
            cache.delete(f'reserva_{reserva_id}')
            cache.delete('reservas')

        # 5. Telegram
        try:
            u = reserva.usuario
            nombre_cliente = f"{u.nombre} {u.apellido}" if u else "Nuevo Cliente"
            telegram = PushNotificationService()
            mensaje = f"👤 *Cliente:* {nombre_cliente}\n📅 *Fecha:* {reserva.fecha.dia}\n📋 *Estado:* {reserva.estado.capitalize()}"
            telegram.send_notification(mensaje, title="🆕 ¡Nueva Solicitud de Reserva!")
        except Exception as e:
            sentry_sdk.capture_exception(e)
            
    except Exception as e:
        sentry_sdk.capture_exception(e)