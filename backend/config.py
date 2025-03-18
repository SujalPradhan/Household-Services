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
# class Config():
#   DEBUG = False
#   sql_alchemy_track_modifications = True

# class DevelopmentConfig(Config):
#   # Flask specific
#   DEBUG = True

#   # SQLAlchemy specific
#   SQLALCHEMY_DATABASE_URI = 'sqlite:///database.sqlite3'

#   # Flask-Security specific
#   SECRET_KEY = 'secret_key'
#   SECURITY_PASSWORD_HASH='bcrypt'
#   SECURITY_PASSWORD_SALT='salt'
#   SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authorization'
#   SECURITY_JOIN_USER_ROLES = 'roles_users'
#   SECURITY_TRACKABLE = True
  
#   # cache specific
#   CA
# # Celery specific


#   # flask mail specific
#   MAIL_SERVER = 'localhost'
#   MAIL_PORT = 1025
#   MAIL_DEFAULT_SENDER = 'donot-reply@servicenest.com'