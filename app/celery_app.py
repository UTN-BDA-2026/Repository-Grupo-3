import os
from celery import Celery
from app import create_app

# Creo la app de Flask para acceder a la bd
app = create_app(os.getenv('FLASK_ENV', 'development'))

# 1. Leemos la contraseña de Redis desde tus variables de entorno (.env)
redis_password = os.getenv('REDIS_PASSWORD', '')

# 2. Armamos la URL incluyendo la contraseña)
redis_url = f"redis://:{redis_password}@redis_service:6379/0"

# 3. Config Celery con la URL segura
celery = Celery(
    app.name,
    broker=redis_url,
    backend=redis_url,
    include=['app.tasks'] 
)

# cada vez que ejecute celery, lo hace dentro del contexto de app
class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)
        
celery.Task = ContextTask