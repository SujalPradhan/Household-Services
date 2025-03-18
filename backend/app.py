from flask import Flask, jsonify, send_file
from flask_security import Security
from flask_restful import Api
from flask_cors import CORS
from flask_security.utils import hash_password
from json import JSONEncoder
from models import db, user_datastore, Admin, ServiceTypeEnum, ServiceStatusEnum, ServiceRequest , Service, Customer, ServiceProfessional
from config import localdev
from caching import cache
from worker import celery_init_app
import flask_excel as excel
from celery.result import AsyncResult
# Define the JSON encoder directly in this file
class CustomJSONEncoder(JSONEncoder):
    """Custom JSON encoder that can handle our Enum types."""
    
    def default(self, obj):
        if isinstance(obj, (ServiceTypeEnum, ServiceStatusEnum)):
            # Return the enum's name (string representation)
            return obj.name
        # Let the parent class handle anything else
        return super().default(obj)
def create_app():
    app = Flask(__name__)
    app.config.from_object(localdev)
    app.json_encoder = CustomJSONEncoder
    db.init_app(app)
    Security(app, user_datastore)
    CORS(app)
    api = Api(app)
    cache.init_app(app)
    return app, api


app, api = create_app()

# app = Flask(__name__)
# app.config.from_object(localdev)

# # Set the custom JSON encoder for our Flask app
# app.json_encoder = CustomJSONEncoder

# # Initialize extensions
# db.init_app(app)
# Security(app, user_datastore)
# CORS(app)
# api = Api(app)
# cache.init_app(app)

celery_app = celery_init_app(app)
# from tasks import say_hello
from tasks import *


from routes import (
    SignUp, SignIn, SignOut, CustomerDashboard, adminDashboard, 
    adminService, adminCustomers, adminProfessional, CustomerServices, 
    SearchServices, SearchProfessionals, ProfessionalsByServiceType,
    ProfessionalServiceRequests, ProfessionalProfile, ServiceRequests, 
    AllServiceRequests
)

# Add the registration API endpoint
api.add_resource(SignUp, "/signup")
api.add_resource(SignIn, "/signin")
api.add_resource(SignOut, "/signout")
api.add_resource(CustomerDashboard, "/customer/dashboard")
api.add_resource(CustomerServices, "/customer/services", "/customer/services/<int:request_id>")
api.add_resource(SearchServices, "/customer/search-services")
api.add_resource(SearchProfessionals, "/admin/search-professionals")
api.add_resource(ProfessionalsByServiceType, "/service/<int:service_id>/professionals") 
api.add_resource(adminDashboard, "/admin/dashboard")
api.add_resource(adminService, "/admin/service", "/admin/service/<int:service_id>")
api.add_resource(adminCustomers, "/admin/customers", "/admin/customers/<int:customer_id>")
api.add_resource(adminProfessional, "/admin/professionals", "/admin/professionals/<int:professional_id>")
api.add_resource(ProfessionalServiceRequests, "/professional/requests", "/professional/requests/<int:request_id>")
api.add_resource(ProfessionalProfile, "/professional/profile")
api.add_resource(ServiceRequests, "/admin/service/<int:service_id>/requests")
api.add_resource(AllServiceRequests, "/admin/service-requests")

@app.route('/')
def home():
    return {"msg": "Hello!"}

def create_admin():
    """Creates an admin role and user if they don't exist."""
    with app.app_context():
        # Ensure the "admin" role exists
        if not user_datastore.find_role("admin"):
            user_datastore.create_role(name="admin", description="Superuser")
        
        # Ensure the admin user exists
        admin_user = user_datastore.find_user(email="admin@abc.com")
        if not admin_user:
            admin_user = user_datastore.create_user(
                email="admin@abc.com",
                password=hash_password("admin123"),
                active=True
            )
            user_datastore.add_role_to_user(admin_user, "admin")
            db.session.add(Admin(user_id=admin_user.id, name="Admin User"))
        
        db.session.commit()



import csv
from io import StringIO
from flask import Response

from tasks import *
@app.get('/downloadcsv')
def download_csv():
    task = create_resource_csv.delay()
    return {"task_id": task.id}

@app.get('/getcsv/<task_id>')
def get_csv(task_id):
    res = AsyncResult(task_id, app=celery_app)
    if res.ready():
        filename = res.result
        return send_file(filename, as_attachment=True)
    
    else:
        return jsonify({"status": "Task pending"}), 400

if __name__ == '__main__':
    create_admin()  # Ensure admin exists before starting the app
    app.run(debug=True)
