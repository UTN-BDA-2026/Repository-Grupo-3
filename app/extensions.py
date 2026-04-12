# Contenido para app/extensions.py

import os

import redis
from flask_caching import Cache
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
cache = Cache()
jwt = JWTManager()
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))
redis_password = os.getenv('REDIS_PASSWORD', '')
redis_db = int(os.getenv('REDIS_DB', 0))

redis_client = redis.StrictRedis(
    host=redis_host,
    port=redis_port,
    db=redis_db,
    password=redis_password,
    decode_responses=True
)

redis_uri = f"redis://:{redis_password}@{redis_host}:{redis_port}/{redis_db}"
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["10 per minute"],
    storage_uri=redis_uri
)