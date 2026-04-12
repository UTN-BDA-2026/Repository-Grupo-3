import time
from contextlib import contextmanager

from app.extensions import cache, db, redis_client
from app.models import Fecha, Reserva
from app.repositories import ReservaRepository
from app.services.fecha_services import FechaService
from app.services.push_notification_service import PushNotificationService


class ReservaService:
    """
    Servicio para gestionar reservas con soporte de caché y bloqueos en Redis para concurrencia.
    """
    CACHE_TIMEOUT = 300  # Tiempo de expiración de caché en segundos
    REDIS_LOCK_TIMEOUT = 10  # Tiempo de bloqueo en Redis en segundos

    def __init__(self, repository=None):
        self.repository = repository or ReservaRepository()
        self.fecha_service = FechaService() 

    @contextmanager
    def redis_lock(self, reserva_id: int):
        """
        Context manager para gestionar el bloqueo de recursos en Redis.
        """
        lock_key = f"reserva_lock_{reserva_id}"
        lock_value = str(time.time())

        if redis_client.set(lock_key, lock_value, ex=self.REDIS_LOCK_TIMEOUT, nx=True):
            try:
                yield 
            finally:
                redis_client.delete(lock_key)
        else:
            raise Exception(f"El recurso está bloqueado para la reserva {reserva_id}.")

    def all(self) -> list[Reserva]:
        """
        Obtiene la lista de todas las reservas, con caché.
        """
        cached_reservas = cache.get('reservas')
        if cached_reservas is None:
            reservas = self.repository.get_all()
            if reservas:
                cache.set('reservas', reservas, timeout=self.CACHE_TIMEOUT)
            return reservas
        return cached_reservas

    def add(self, reserva: Reserva) -> Reserva:
        """
        Agrega una nueva reserva, verificando la disponibilidad de la fecha
        y actualizando su estado para que coincida con el de la reserva.
        """
        with self.fecha_service.redis_lock(reserva.fecha_id):
            
            fecha_a_reservar = self.fecha_service.find(reserva.fecha_id)

            if not fecha_a_reservar:
                raise Exception(f"La fecha con ID {reserva.fecha_id} no existe.")

            if fecha_a_reservar.estado != 'disponible':
                raise Exception(f"La fecha seleccionada ya no está disponible.")

            try:
                # Ahora el estado de la fecha depende del estado de la reserva
                if reserva.estado == 'confirmada':
                    fecha_a_reservar.estado = 'reservada'
                else:
                    fecha_a_reservar.estado = 'pendiente'
                
                db.session.add(reserva)
                db.session.add(fecha_a_reservar)
                db.session.commit()

                # --- INICIO DE NOTIFICACIÓN TELEGRAM ---
                try:
                    u = reserva.usuario
                    nombre_cliente = f"{u.nombre} {u.apellido}" if u else "Nuevo Cliente"
                    
                    telegram = PushNotificationService()
                    mensaje_alerta = (
                        f"👤 *Cliente:* {nombre_cliente}\n"
                        f"📅 *Fecha:* {fecha_a_reservar.dia}\n"
                        f"📋 *Estado:* {reserva.estado.capitalize()}"
                    )
                    telegram.send_notification(mensaje_alerta, title="🆕 ¡Nueva Solicitud de Reserva!")
                except Exception as e:
                    print(f"Error al enviar notificación push: {e}")
                # --- FIN DE NOTIFICACIÓN ---

                cache.clear() 
                
                cache.set(f'reserva_{reserva.id}', reserva, timeout=self.CACHE_TIMEOUT)
                cache.set(f'fecha_{fecha_a_reservar.id}', fecha_a_reservar, timeout=self.CACHE_TIMEOUT)

                return reserva

            except Exception as e:
                db.session.rollback()
                raise e

    def update(self, reserva_id: int, updated_data: dict) -> Reserva:
        """
        Actualiza una reserva existente con nuevos datos.
        """
        with self.redis_lock(reserva_id):
            reserva_a_actualizar = self.repository.get_by_id(reserva_id)
            
            if not reserva_a_actualizar:
                raise Exception(f"Reserva con ID {reserva_id} no encontrada.")

            estado_anterior = reserva_a_actualizar.estado
            nuevo_estado = updated_data.get('estado')

            for key, value in updated_data.items():
                if hasattr(reserva_a_actualizar, key):
                    setattr(reserva_a_actualizar, key, value)
            
            # Comprobamos los estados para actualizar la fecha
            if nuevo_estado == 'confirmada' and estado_anterior != 'confirmada':
                reserva_a_actualizar.fecha.estado = 'reservada'
            elif nuevo_estado == 'cancelada' and estado_anterior != 'cancelada':
                reserva_a_actualizar.fecha.estado = 'disponible'
            elif nuevo_estado == 'pendiente' and estado_anterior != 'pendiente':
                reserva_a_actualizar.fecha.estado = 'pendiente'

            db.session.add(reserva_a_actualizar)
            if reserva_a_actualizar.fecha:
                db.session.add(reserva_a_actualizar.fecha)

            db.session.commit()
            reserva_fresca = self.repository.get_by_id(reserva_id)

            # Limpieza total de caché
            cache.clear() 

            return reserva_fresca

    def delete(self, reserva_id: int) -> bool:
        """
        Archiva una reserva en lugar de eliminarla permanentemente (soft delete).
        """
        with self.redis_lock(reserva_id):
            reserva_a_archivar = self.repository.get_by_id(reserva_id)

            if not reserva_a_archivar:
                return False

            try:
                reserva_a_archivar.estado = 'archivada'

                # Liberamos la fecha para que vuelva a estar disponible
                fecha_asociada = reserva_a_archivar.fecha
                if fecha_asociada:
                    fecha_asociada.estado = 'disponible'
                    db.session.add(fecha_asociada)

                db.session.commit()
                cache.clear() # Limpieza total

                return True

            except Exception as e:
                db.session.rollback()
                raise e

    def get_all_archived(self) -> list[Reserva]:
        """
        Obtiene la lista de todas las reservas archivadas, con caché.
        """
        cached_reservas = cache.get('reservas_archivadas')
        if cached_reservas is None:
            reservas = self.repository.get_all_archived()
            if reservas:
                cache.set('reservas_archivadas', reservas, timeout=self.CACHE_TIMEOUT)
            return reservas
        return cached_reservas

    def find(self, reserva_id: int) -> Reserva:
        """
        Busca una reserva por su ID, con caché.
        """
        cached_reserva = cache.get(f'reserva_{reserva_id}')
        if cached_reserva is None:
            reserva = self.repository.get_by_id(reserva_id)
            if reserva:
                cache.set(f'reserva_{reserva_id}', reserva, timeout=self.CACHE_TIMEOUT)
            return reserva
        return cached_reserva

    def recalcular_saldo(self, reserva_id: int):
        """
        Invalida la caché para forzar el recálculo del saldo_restante.
        """
        cache.clear()
        
    def get_by_user_id(self, user_id: int) -> list[Reserva]:
        """
        Obtiene todas las reservas de un usuario.
        """
        return self.repository.get_by_user_id(user_id)
    def search(self, term: str) -> list[Reserva]:
        """
        Busca reservas activas por coincidencia de texto en el cliente o estado.
        No utiliza caché para la búsqueda en vivo.
        """
        if not term:
            return []
        
        return self.repository.search(term)