import time
from contextlib import contextmanager

from app.extensions import cache, db, redis_client
from app.models import Persona
from app.repositories import PersonaRepository


class PersonaService:
    """
    Servicio para gestionar personas con soporte de caché y bloqueos en Redis para concurrencia.
    """
    CACHE_TIMEOUT = 300  # Tiempo de expiración de caché en segundos
    REDIS_LOCK_TIMEOUT = 10  # Tiempo de bloqueo en Redis en segundos

    def __init__(self, repository=None):
        self.repository = repository or PersonaRepository()

    @contextmanager
    def redis_lock(self, persona_id: int):
        """
        Context manager para gestionar el bloqueo de recursos en Redis.
        """
        lock_key = f"persona_lock_{persona_id}"
        lock_value = str(time.time())

        if redis_client.set(lock_key, lock_value, ex=self.REDIS_LOCK_TIMEOUT, nx=True):
            try:
                yield  # Permite la ejecución del bloque protegido
            finally:
                redis_client.delete(lock_key)
        else:
            raise Exception(f"El recurso está bloqueado para la persona {persona_id}.")

    def all(self) -> list[Persona]:
        """
        Obtiene la lista de todas las personas, con caché.
        """
        cached_personas = cache.get('personas')
        if cached_personas is None:
            personas = self.repository.get_all()
            if personas:
                cache.set('personas', personas, timeout=self.CACHE_TIMEOUT)
            return personas
        return cached_personas

    def add(self, persona: Persona) -> Persona:
        """
        Agrega una nueva persona y actualiza la caché.
        """
        new_persona = self.repository.add(persona)
        cache.set(f'persona_{new_persona.id}', new_persona, timeout=self.CACHE_TIMEOUT)
        cache.delete('personas')
        return new_persona


    def update(self, persona_id: int, updated_persona: Persona) -> Persona:
        """
        Actualiza una persona existente.
        """
        with self.redis_lock(persona_id):
            existing_persona = self.find(persona_id)
            if not existing_persona:
                raise Exception(f"Persona con ID {persona_id} no encontrada.")

            existing_persona.nombre = updated_persona.nombre
            existing_persona.apellido = updated_persona.apellido
            existing_persona.correo = updated_persona.correo
            existing_persona.dni = updated_persona.dni

            # Guardar los cambios en la base de datos
            db.session.commit()

            # Actualizar la caché
            cache.set(f'persona_{persona_id}', existing_persona, timeout=self.CACHE_TIMEOUT)
            cache.delete('personas')

            return existing_persona

    def delete(self, persona_id: int) -> bool:
        """
        Elimina una persona por su ID y actualiza la caché.
        """
        with self.redis_lock(persona_id):
            deleted = self.repository.delete(persona_id)
            if deleted:
                cache.delete(f'persona_{persona_id}')
                cache.delete('personas')
            return deleted

    def find(self, persona_id: int) -> Persona:
        """
        Busca una persona por su ID, con caché.
        """
        cached_persona = cache.get(f'persona_{persona_id}')
        if cached_persona is None:
            persona = self.repository.get_by_id(persona_id)
            if persona:
                cache.set(f'persona_{persona_id}', persona, timeout=self.CACHE_TIMEOUT)
            return persona
        return cached_persona
