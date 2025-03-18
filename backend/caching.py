from flask_caching import Cache

# Initialize cache object without binding it to an app yet
# This will be bound to the app in app.py
cache = Cache()