import os

import sentry_sdk
from flask import Flask
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from sentry_sdk.integrations.flask import FlaskIntegration

from app.config import factory
from app.extensions import cache, db, jwt, limiter

def create_app(config_name=None):
    app = Flask(__name__)
    app.config.from_object(factory(config_name))

    # Configuración de Sentry
    sentry_dsn = os.getenv("SENTRY_DSN_BACKEND")
    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[FlaskIntegration()],
            traces_sample_rate=1.0
        )

    # Inicialización de extensiones
    db.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)
    jwt.init_app(app)

    # Middleware de Sentry
    @app.before_request
    def set_sentry_user_context():
        try:
            verify_jwt_in_request(optional=True)
            claims = get_jwt()
            if claims and "email" in claims:
                sentry_sdk.set_user({
                    "id": claims.get("sub"),
                    "email": claims.get("email"),
                    "username": claims.get("username"),
                    "role": claims.get("role")
                })
            else:
                sentry_sdk.set_user(None)
        except Exception:
            sentry_sdk.set_user(None)
    
    # Registro de Blueprints
    from app.routes.administrador_resource import Administrador
    from app.routes.analytics_resource import Analytics
    from app.routes.auth_resource import Auth
    from app.routes.chatbot_resource import ChatbotBP
    from app.routes.config_resource import Config
    from app.routes.fecha_resource import Fecha
    from app.routes.gasto_resource import GastoBP
    from app.routes.pago_resource import PagoBP
    from app.routes.persona_resource import Persona
    from app.routes.reserva_resource import Reserva
    from app.routes.test_notifications_resource import TestNotifications
    from app.routes.usuario_resource import Usuario
    app.register_blueprint(Administrador, url_prefix='/api/v1')
    app.register_blueprint(Usuario, url_prefix='/api/v1')
    app.register_blueprint(Fecha, url_prefix='/api/v1')
    app.register_blueprint(Reserva, url_prefix='/api/v1')
    app.register_blueprint(Persona, url_prefix='/api/v1')
    app.register_blueprint(Auth, url_prefix='/api/v1')
    app.register_blueprint(Config, url_prefix='/api/v1')
    app.register_blueprint(Analytics, url_prefix='/api/v1')
    app.register_blueprint(PagoBP, url_prefix='/api/v1')
    app.register_blueprint(TestNotifications, url_prefix='/api/v1')
    app.register_blueprint(GastoBP, url_prefix='/api/v1')
    app.register_blueprint(ChatbotBP, url_prefix='/api/v1')
    
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()
    return app