from flask.json.provider import JSONEncoder  # Updated import path
from models import ServiceTypeEnum, ServiceStatusEnum

class CustomJSONEncoder(JSONEncoder):
    """Custom JSON encoder that can handle our Enum types."""
    
    def default(self, obj):
        if isinstance(obj, (ServiceTypeEnum, ServiceStatusEnum)):
            # Return the enum's name (string representation)
            return obj.name
        # Let the parent class handle anything else
        return super().default(obj)
