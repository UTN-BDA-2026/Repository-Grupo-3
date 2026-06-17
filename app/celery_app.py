import os
from celery import Celery
from celery.schedules import crontab
from flask import has_app_context

# 1. Creamos la instancia principal de Celery apuntando a Docker
celery = Celery(
    "app",
    broker=os.getenv("CELERY_BROKER_URL", "redis://:1234@redis:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://:1234@redis:6379/0"),
    include=['app.tasks'] # Le decimos dónde buscar las tareas
)

# Configuramos la zona horaria para que el cron se ejecute a tu hora local real
celery.conf.timezone = 'America/Argentina/Buenos_Aires'

# Celery corre en un proceso paralelo. Si no hacemos esto, cuando intente 
# usar db.session.get() para actualizar el calendario, crasheará.
class FlaskTask(celery.Task):
    def __call__(self, *args, **kwargs):
        if has_app_context():
            return self.run(*args, **kwargs)
        else:
            # Si el Worker de Celery lo está ejecutando, levanta el entorno de Flask primero
            from app import create_app
            flask_app = create_app()
            with flask_app.app_context():
                return self.run(*args, **kwargs)

celery.Task = FlaskTask

# 3. Programación de Tareas Periódicas (Celery Beat)
celery.conf.beat_schedule = {
    'notificar-pendientes-9am': {
        'task': 'app.tasks.check_pending_reservations',
        'schedule': crontab(hour=9, minute=0),
    },
    'notificar-proximos-10am': {
        'task': 'app.tasks.check_upcoming_reservations',
        'schedule': crontab(hour=10, minute=0),
    },
}