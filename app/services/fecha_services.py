import time
from contextlib import contextmanager
from datetime import date

from app.extensions import cache, db, redis_client
from app.models import Fecha
from app.repositories import FechaRepository


class FechaService:
    """
    Servicio para gestionar fechas con soporte de caché y bloqueos en Redis para concurrencia.
    """
    CACHE_TIMEOUT = 300  # Tiempo de expiración de caché en segundos
    REDIS_LOCK_TIMEOUT = 10  # Tiempo de bloqueo en Redis en segundos

    def __init__(self, repository=None):
        self.repository = repository or FechaRepository()

    @contextmanager
    def redis_lock(self, fecha_id: int):
        """
        Context manager para gestionar el bloqueo de recursos en Redis y evitar colisiones.
        """
        lock_key = f"fecha_lock_{fecha_id}"
        lock_value = str(time.time())

        if redis_client.set(lock_key, lock_value, ex=self.REDIS_LOCK_TIMEOUT, nx=True):
            try:
                yield  # Permite la ejecución del bloque protegido
            finally:
                redis_client.delete(lock_key)
        else:
            raise Exception(f"El recurso para la fecha {fecha_id} está bloqueado por otra operación.")

    def all(self) -> list[Fecha]:
        """
        Obtiene la lista de todas las fechas con soporte de caché.
        """
        cached_fechas = cache.get('fechas')
        if cached_fechas is None:
            fechas = self.repository.get_all()
            if fechas:
                cache.set('fechas', fechas, timeout=self.CACHE_TIMEOUT)
            return fechas
        return cached_fechas

    def add(self, fecha: Fecha) -> Fecha:
        """
        Agrega una nueva fecha, asegura el commit y actualiza la caché.
        """
        new_fecha = self.repository.add(fecha)
        db.session.commit()
        
        fecha_fresca = self.repository.get_by_id(new_fecha.id)
        
        if fecha_fresca:
            cache.set(f'fecha_{fecha_fresca.id}', fecha_fresca, timeout=self.CACHE_TIMEOUT)
        
        # Limpieza profunda de cachés
        cache.delete('fechas')
        cache.delete('fechas_disponibles')
        cache.delete('todas_las_fechas')
        
        return fecha_fresca

    def update(self, fecha_id: int, updated_data: dict) -> Fecha:
        """
        Actualiza una fecha obteniéndola directamente del repositorio para 
        garantizar que esté vinculada a la sesión de SQLAlchemy.
        """
        with self.redis_lock(fecha_id):
            # Buscamos en la BD, no en la caché, para que el objeto sea "trackeable"
            existing_fecha = self.repository.get_by_id(fecha_id)

            if not existing_fecha:
                raise Exception(f"Fecha con ID {fecha_id} no encontrada.")

            # Actualización flexible de campos
            if 'valor_estimado' in updated_data:
                try:
                    val = updated_data['valor_estimado']
                    existing_fecha.valor_estimado = float(val) if val is not None else 0.0
                except (ValueError, TypeError):
                    raise ValueError("El valor_estimado debe ser un número válido.")
            
            if 'estado' in updated_data:
                existing_fecha.estado = updated_data['estado']

            db.session.add(existing_fecha)
            db.session.commit()

            fecha_fresca = self.repository.get_by_id(fecha_id)

            # Sincronizar caché
            if fecha_fresca:
                cache.set(f'fecha_{fecha_id}', fecha_fresca, timeout=self.CACHE_TIMEOUT)
            
            # Limpieza profunda de cachés
            cache.delete('fechas')
            cache.delete('fechas_disponibles')
            cache.delete('todas_las_fechas')

            return fecha_fresca

    def delete(self, fecha_id: int) -> bool:
        """
        Elimina una fecha y limpia las referencias en caché.
        """
        with self.redis_lock(fecha_id):
            deleted = self.repository.delete(fecha_id)
            if deleted:
                db.session.commit()
                cache.delete(f'fecha_{fecha_id}')
                
                # Limpieza profunda
                cache.delete('fechas')
                cache.delete('fechas_disponibles')
                cache.delete('todas_las_fechas')
            return deleted

    def find(self, fecha_id: int) -> Fecha:
        """
        Busca una fecha por ID priorizando la caché.
        """
        cached_fecha = cache.get(f'fecha_{fecha_id}')
        if cached_fecha is None:
            fecha = self.repository.get_by_id(fecha_id)
            if fecha:
                cache.set(f'fecha_{fecha_id}', fecha, timeout=self.CACHE_TIMEOUT)
            return fecha
        return cached_fecha

    def find_by_dia(self, dia: date) -> Fecha:
        """
        Busca una fecha por su día usando el repositorio.
        """
        return self.repository.get_by_dia(dia)

    def get_or_create(self, dia: date) -> Fecha:
        """
        Busca una fecha. Si no existe, la crea con valores por defecto.
        Garantiza que siempre haya un registro para operar.
        """
        fecha = self.find_by_dia(dia)
        if not fecha:
            nueva_fecha = Fecha(dia=dia, estado='disponible', valor_estimado=0.0)
            fecha = self.add(nueva_fecha)
        return fecha