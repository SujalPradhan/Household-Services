class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data.sqlite3'
    SECRET_KEY = "shhh..secret"
    SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authorization'
    SECURITY_REDIRECT_BEHAVIOR = "spa"
    SECURITY_PASSWORD_SALT = "y"
    SECURITY_FLASH_MESSAGES = False
    WTF_CSRF_ENABLED = False
    SECURITY_JOIN_USER_ROLES = 'role_user'

class localdev(Config):
    DEBUG = True
    CACHE_TYPE = "RedisCache"
    CACHE_DEFAULT_TIMEOUT = 60
    CACHE_KEY_PREFIX = "household_services"
    CACHE_REDIS_HOST = "localhost"
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_DB = 2
    SMTP_HOST = "localhost"
    SMTP_PORT = 1025
    SENDER_EMAIL = "23f2004759@ds.study.iitm.ac.in"
    SENDER_PASSWORD = ""
