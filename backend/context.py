from celery import Task
from celery_instance import celery_app

class FlaskTask(Task):
    def __call__(self, *args, **kwargs):
        # Import app inside method to avoid circular imports
        from app import app
        
        # Ensure we're running within the application context
        with app.app_context():
            return Task.__call__(self, *args, **kwargs)