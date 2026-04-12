import datetime
import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, "..", ".env"))

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=2)
    GOOGLE_CREDENTIALS = {
    "type": os.getenv("GOOGLE_TYPE"),
    "project_id": os.getenv("GOOGLE_PROJECT_ID"),
    "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace('\\n', '\n'),
    "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
    "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
    "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("GOOGLE_AUTH_PROVIDER_CERT_URL"),
    "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_CERT_URL"),
    "universe_domain": os.getenv("GOOGLE_UNIVERSE_DOMAIN")
    }
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 20,          # Máximo de conexiones fijas
        "max_overflow": 10,       # Conexiones extra si hay picos
        "pool_timeout": 30,       # Tiempo de espera antes de dar error
        "pool_recycle": 1800,     # Reiniciar conexiones cada 30 min
        "pool_pre_ping": True,
    }
    @staticmethod
    def init_app(app):
        """Método para inicializar configuraciones adicionales si es necesario."""
        pass

    @staticmethod
    def validate_required_env_vars(env_vars):
        """Valida que las variables de entorno críticas estén definidas."""
        missing_vars = [var for var in env_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Las siguientes variables de entorno faltan o están vacías: {', '.join(missing_vars)}")
    

class DevelopmentConfig(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_RECORD_QUERIES = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DATABASE_URI') 
    CACHE_REDIS_HOST = os.getenv('REDIS_HOST')
    CACHE_REDIS_PORT = os.getenv('REDIS_PORT')
    CACHE_REDIS_DB = os.getenv('REDIS_DB')
    CACHE_REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
    CACHE_TYPE = "RedisCache"
    @staticmethod
    def init_app(app):
        """Valida las variables de entorno críticas para desarrollo."""
        Config.validate_required_env_vars(['DEV_DATABASE_URI', 'REDIS_HOST', 'REDIS_PORT'])

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300



class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv("PROD_DATABASE_URI")

    @staticmethod
    def init_app(app):
        """Valida las variables de entorno críticas para producción."""
        Config.validate_required_env_vars(['PROD_DATABASE_URI'])

def factory(env):
    """Devuelve la configuración adecuada según el entorno."""
    envs = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
        "default": DevelopmentConfig
    }
    return envs.get(env, DevelopmentConfig)
