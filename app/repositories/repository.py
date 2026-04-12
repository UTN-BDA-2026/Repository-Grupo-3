from abc import ABC, abstractmethod
from typing import List, TypeVar

from app.extensions import db

T = TypeVar('T')

class Repository_add(ABC):
    @abstractmethod
    def add(self, entity: T) -> T:
        pass
    
class Repository_get(ABC):
    @abstractmethod
    def get_all(self) -> List[T]:
        pass

    @abstractmethod 
    def get_by_id(self, id) -> T:
        pass
    
    
class Repository_create(ABC):
    
    @abstractmethod
    def create(self, entity: T) -> T:
        pass
    
class Repository_update(ABC):
    
    @abstractmethod
    def update(self, id, entity: T) -> T:
        pass
    
class Repository_delete(ABC):
    
    @abstractmethod 
    def delete(self, id) -> bool:
        pass