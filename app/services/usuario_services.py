import time
from contextlib import contextmanager

from app import db
from app.extensions import cache, db, redis_client
from app.models import Usuario
from app.repositories import UsuarioRepository


class UsuarioService:
    """
    Servicio para gestionar usuarios con soporte de caché y bloqueos en Redis para concurrencia.
    """
    CACHE_TIMEOUT = 300
    REDIS_LOCK_TIMEOUT = 10

    def __init__(self, repository=None):
        self.repository = repository or UsuarioRepository()

    @contextmanager
    def redis_lock(self, usuario_id: int):
        """
        Context manager para gestionar el bloqueo de recursos en Redis.
        """
        lock_key = f"usuario_lock_{usuario_id}"
        lock_value = str(time.time())

        if redis_client.set(lock_key, lock_value, ex=self.REDIS_LOCK_TIMEOUT, nx=True):
            try:
                yield
            finally:
                redis_client.delete(lock_key)
        else:
            raise Exception(f"El recurso está bloqueado para el usuario {usuario_id}.")

    def all(self) -> list[Usuario]:
        """
        Obtiene la lista de todos los usuarios (activos), con caché.
        """
        cached_usuarios = cache.get('usuarios')
        if cached_usuarios is None:
            usuarios = self.repository.get_all()
            if usuarios:
                cache.set('usuarios', usuarios, timeout=self.CACHE_TIMEOUT)
            return usuarios
        return cached_usuarios

    def add(self, usuario: Usuario) -> Usuario:
        """
        Agrega un nuevo usuario o REACTIVA uno que había sido eliminado (Soft Delete).
        """
        # 1. Buscamos si ya existe alguien con ese correo en la base de datos (incluso inactivos)
        usuario_existente = Usuario.query.filter_by(correo=usuario.correo).first()
        
        if usuario_existente:
            if not usuario_existente.activo:
                # El usuario estaba "eliminado", lo reactivamos y actualizamos sus datos
                usuario_existente.activo = True
                usuario_existente.nombre = usuario.nombre
                usuario_existente.apellido = usuario.apellido
                usuario_existente.dni = usuario.dni
              
                if hasattr(usuario, 'contrasena') and usuario.contrasena:
                    usuario_existente.contrasena = usuario.contrasena 
                
                db.session.commit()
                
                # Refrescamos la entidad desde la DB para evitar problemas de caché
                usuario_fresco = self.repository.get_by_id(usuario_existente.id)
                if usuario_fresco:
                    cache.set(f'usuario_{usuario_fresco.id}', usuario_fresco, timeout=self.CACHE_TIMEOUT)
                cache.delete('usuarios')
                return usuario_fresco
            else:
                # Si existe y está activo, es un error normal de correo duplicado
                raise ValueError("Este correo ya está registrado en el sistema.")

        # 2. Si no existe, lo creamos de forma normal
        new_usuario = self.repository.add(usuario)
        db.session.commit()
        
        usuario_fresco = self.repository.get_by_id(new_usuario.id)
        
        if usuario_fresco:
            cache.set(f'usuario_{usuario_fresco.id}', usuario_fresco, timeout=self.CACHE_TIMEOUT)
        cache.delete('usuarios')
        
        return usuario_fresco

    def update(self, usuario_id: int, updated_usuario: Usuario) -> Usuario:
        """
        Actualiza un usuario existente.
        """
        with self.redis_lock(usuario_id):
            existing_usuario = self.repository.get_by_id(usuario_id)
            if not existing_usuario:
                raise Exception(f"Usuario con ID {usuario_id} no encontrada.")

            existing_usuario.nombre = updated_usuario.nombre
            existing_usuario.apellido = updated_usuario.apellido
            existing_usuario.dni = updated_usuario.dni
            existing_usuario.correo = updated_usuario.correo

            db.session.commit()
        
            usuario_fresco = self.repository.get_by_id(usuario_id)
            
            cache.set(f'usuario_{usuario_id}', usuario_fresco, timeout=self.CACHE_TIMEOUT)
            cache.delete('usuarios')

            return usuario_fresco

    def delete(self, usuario_id: int) -> bool:
        """
        Realiza un Borrado Lógico (Soft Delete) apagando al usuario.
        """
        with self.redis_lock(usuario_id):
            usuario_a_eliminar = self.repository.get_by_id(usuario_id)

            if not usuario_a_eliminar:
                return False

            usuario_a_eliminar.activo = False
            db.session.commit()
            cache.delete(f'usuario_{usuario_id}')
            cache.delete('usuarios')
            
            return True

    def find(self, usuario_id: int) -> Usuario:
        """
        Busca un usuario por su ID, con caché.
        """
        cached_usuario = cache.get(f'usuario_{usuario_id}')
        if cached_usuario is None:
            usuario = self.repository.get_by_id(usuario_id)
            # Solo devolvemos si existe y está activo
            if usuario and getattr(usuario, 'activo', True):
                cache.set(f'usuario_{usuario_id}', usuario, timeout=self.CACHE_TIMEOUT)
                return usuario
            return None
        return cached_usuario
    def search(self, term: str) -> list[Usuario]:
        """
        Busca usuarios activos por coincidencia de texto.
        No utiliza caché para evitar saturar Redis con cada pulsación de tecla.
        """
        if not term:
            return []
        
        return self.repository.search(term)