from typing import List

from app.extensions import db
from app.models import Usuario

from .repository import Repository_add, Repository_delete, Repository_get


class UsuarioRepository(Repository_add, Repository_get, Repository_delete):
    def add(self, entity: Usuario) -> Usuario:
        # El repositorio solo prepara la entidad en la sesión.
        # El commit y manejo de errores se delegan a la capa superior.
        db.session.add(entity)  
        return entity

    def get_all(self):
        return Usuario.query.filter_by(activo=True).order_by(Usuario.id.desc()).limit(100).all()

    def get_by_id(self, id: int) -> Usuario:
        return Usuario.query.get(id)

    def delete(self, id: int) -> bool:
        # Solo buscamos y marcamos para borrar si existe.
        usuario = self.get_by_id(id)
        if usuario:
            db.session.delete(usuario)  
            return True
        return False
    
    def search(self, term: str, limit: int = 10) -> List[Usuario]:
        """Busca usuarios separando la lógica de texto y números para evitar escaneos completos."""
        term = term.strip()
        search_pattern = f"%{term}%"
        
        # Si tipeó SOLO NÚMEROS (Está buscando un DNI)
        if term.isdigit():
            if len(term) >= 7:
                # DNI completo: Búsqueda exacta directa al índice (Instantáneo)
                return Usuario.query.filter(
                    Usuario.activo == True, 
                    Usuario.dni == int(term)
                ).limit(limit).all()
            else:
                # DNI incompleto: Búsqueda parcial solo en la columna DNI
                return Usuario.query.filter(
                    Usuario.activo == True, 
                    db.cast(Usuario.dni, db.String).ilike(search_pattern)
                ).limit(limit).all()
                
        # Si tipeó LETRAS (Está buscando Nombre/Apellido)
        else:
            condiciones = [
                Usuario.nombre.ilike(search_pattern),
                Usuario.apellido.ilike(search_pattern),
                db.func.concat(Usuario.nombre, ' ', Usuario.apellido).ilike(search_pattern),
                db.func.concat(Usuario.apellido, ' ', Usuario.nombre).ilike(search_pattern)
            ]
            return Usuario.query.filter(
                Usuario.activo == True,
                db.or_(*condiciones)
            ).limit(limit).all()