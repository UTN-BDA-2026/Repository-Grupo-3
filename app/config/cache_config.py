
import os

env = os.getenv("FLASK_ENV", "development")

if env == "testing":
    cache_config = {
        "CACHE_TYPE": "SimpleCache",
        "CACHE_DEFAULT_TIMEOUT": 300
    }
else:
    cache_config = {
        "CACHE_TYPE": "RedisCache",
        "CACHE_DEFAULT_TIMEOUT": 300,
        "CACHE_REDIS_HOST": os.environ.get('REDIS_HOST'),
        "CACHE_REDIS_PORT": os.environ.get('REDIS_PORT'),
        "CACHE_REDIS_DB": os.environ.get('REDIS_DB'),
        "CACHE_REDIS_PASSWORD": os.environ.get('REDIS_PASSWORD'),
        "CACHE_KEY_PREFIX": "flask_"
    }
