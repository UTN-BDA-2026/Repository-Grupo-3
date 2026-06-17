import mimetypes
import os
from datetime import datetime, timedelta

import sentry_sdk
from celery import shared_task
from werkzeug.datastructures import FileStorage

from app.extensions import cache, db
from app.models import Fecha, Reserva
from app.services.push_notification_service import PushNotificationService
from app.utils.storage import upload_file_to_r2


@shared_task
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


@shared_task
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


@shared_task
def procesar_reserva_background(reserva_id: int, ruta_archivo_local: str = None):
    """
    Tarea en segundo plano: Sube el comprobante a R2, actualiza calendarios, 
    limpia cachés y notifica por Telegram.
    """
    try:
        # 1. Buscamos la reserva en la base de datos
        reserva = db.session.get(Reserva, reserva_id)
        if not reserva:
            # Si se elimina la reserva antes de que el worker empiece, limpiamos el archivo residual
            if ruta_archivo_local and os.path.exists(ruta_archivo_local):
                os.remove(ruta_archivo_local)
            return

        # 2. PROCESAMIENTO ASÍNCRONO DEL COMPROBANTE (R2)
        if ruta_archivo_local and os.path.exists(ruta_archivo_local):
            try:
                # Abrimos el archivo local en modo binario
                with open(ruta_archivo_local, 'rb') as archivo_binario:
                    nombre_archivo = os.path.basename(ruta_archivo_local)
                    
                    # Adivinamos el ContentType a partir del nombre para evitar errores en boto3/R2
                    tipo_mime, _ = mimetypes.guess_type(nombre_archivo)
                    if not tipo_mime:
                        tipo_mime = 'application/octet-stream' # Valor por defecto seguro
                    
                    # Envolvemos el archivo en un FileStorage simulando el comportamiento de Flask
                    archivo_flask = FileStorage(
                        stream=archivo_binario,
                        filename=nombre_archivo,
                        content_type=tipo_mime
                    )
                    
                    # Ejecutamos la función de subida pasándole el objeto correcto
                    archivo_url = upload_file_to_r2(archivo_flask, folder=f"comprobantes/fecha_{reserva.fecha_id}")
                    
                    if archivo_url:
                        reserva.comprobante_url = archivo_url
                    else:
                        raise Exception("La función upload_file_to_r2 devolvió una URL vacía")
                        
            except Exception as r2_err:
                print(f"Error al subir comprobante a R2 en background: {r2_err}")
                sentry_sdk.capture_exception(r2_err)
            finally:
                # PASO CRÍTICO: Borramos el archivo local del volumen compartido
                if os.path.exists(ruta_archivo_local):
                    os.remove(ruta_archivo_local)

        # 3. Actualizamos el estado de la fecha en el calendario a 'pendiente'
        fecha = db.session.get(Fecha, reserva.fecha_id)
        if fecha:
            fecha.estado = 'pendiente'
            db.session.add(fecha)

        # 4. Guardamos los cambios definitivos (URL de R2 + Estado de la Fecha)
        db.session.commit()

        # 5. Destruimos la caché para que el calendario de React se actualice al instante
        cache.delete('fechas')
        cache.delete(f'fecha_{fecha.id if fecha else "unknown"}')
        cache.delete('todas_las_fechas')
        cache.delete('fechas_all')

        # 6. Enviamos la notificación a Telegram
        try:
            u = reserva.usuario
            nombre_cliente = f"{u.nombre} {u.apellido}" if u else "Nuevo Cliente"
            telegram = PushNotificationService()
            mensaje = f"👤 *Cliente:* {nombre_cliente}\n📅 *Fecha:* {fecha.dia if fecha else 'N/A'}\n✅ *Reserva solicitada y agendada exitosamente*"
            telegram.send_notification(mensaje, title="🆕 ¡Nueva Reserva!")
        except Exception as tel_err:
            sentry_sdk.capture_exception(tel_err)

    except Exception as e:
        db.session.rollback()
        sentry_sdk.capture_exception(e)
        
        # Limpieza de seguridad en el bloque exterior por si falló algo antes del bloque try/finally interno
        if ruta_archivo_local and os.path.exists(ruta_archivo_local):
            try:
                os.remove(ruta_archivo_local)
            except Exception:
                pass
            
@shared_task
def enviar_contrato_background(reserva_id: int):

    from app.routes.reserva_resource import _enviar_contrato_confirmacion

    """
    Tarea en segundo plano: Genera el PDF y envía el correo 
    cuando un admin confirma o crea una reserva.
    """
    try:
        # Recuperamos la reserva fresca de la base de datos
        reserva = db.session.get(Reserva, reserva_id)
        
        if not reserva:
            return

        # Verificamos de nuevo por seguridad
        if reserva.estado == 'confirmada':
            # Llamamos a tu función original pasándole el objeto
            _enviar_contrato_confirmacion(reserva)
            print(f"Contrato enviado en background para reserva {reserva_id}")

    except Exception as e:
        sentry_sdk.capture_exception(e)
        print(f"Error al enviar contrato en background: {e}")