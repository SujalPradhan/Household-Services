from celery import Task
from app import create_app

app, _ = create_app()

class FlaskTask(Task):
    def __call__(self, *args: object, **kwargs: object) -> object:
        with app.app_context():
            return self.run(*args, **kwargs)