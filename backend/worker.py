from celery import Celery, Task


def celery_init_app(app):
    celery_app = Celery(app.name)
    celery_app.config_from_object("celery_config")
    return celery_app