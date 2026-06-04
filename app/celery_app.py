import os
from celery import Celery
from app import create_app

# Creo la app de Flask para acceder a la bd
app = create_app(os.getenv('FLASK_ENV', 'development'))

# Config Celery para que use el contenedor de Redis
celery = Celery(
    app.name,
    broker = 'redis://redis_service:6379/0',
    backend = 'redis://redis_service:6379/0'
    )

# cada vez que ejecute celery, lo hace dentro del contexto de app
class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app.context():
            return self.run(*args, **kwargs)
        
celery.Task = ContextTask