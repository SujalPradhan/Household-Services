from celery import Celery

# Create a placeholder Celery app - will be configured properly in app.py
celery_app = Celery("household_services")

def configure_celery(app):
    """Configure celery with Flask app context"""
    celery_app.conf.update(app.config)
    
    # Update broker_url and result_backend from config if available
    celery_app.conf.broker_url = app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    celery_app.conf.result_backend = app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    celery_app.conf.broker_connection_retry_on_startup = True
    
    # Properly set the timezone to ensure consistency
    celery_app.conf.timezone = 'Asia/Kolkata'  # Note capitalization of 'Kolkata'
    celery_app.conf.enable_utc = False
    
    # Store the Flask app instance in the Celery app
    celery_app.flask_app = app
    
    class ContextTask(celery_app.Task):
        # Ensure each task gets its own application context
        def __call__(self, *args, **kwargs):
            with celery_app.flask_app.app_context():
                return self.run(*args, **kwargs)
    
    # Override the base task class for all tasks
    celery_app.Task = ContextTask
    return celery_app
