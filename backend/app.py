from flask import Flask
from flask_security import Security
from flask_restful import Api
from flask_cors import CORS
from flask_security.utils import hash_password

from models import db, user_datastore, Admin
from config import localdev

app = Flask(__name__)
app.config.from_object(localdev)

# Initialize extensions
db.init_app(app)
Security(app, user_datastore)
CORS(app)
api = Api(app)

from routes import (
    SignUp, SignIn, SignOut, CustomerDashboard, adminDashboard, 
    adminService, adminCustomers, adminProfessional, CustomerServices, 
    SearchServices, SearchProfessionals, ProfessionalsByServiceType,
    ProfessionalServiceRequests
)

# Add the registration API endpoint
api.add_resource(SignUp, "/signup")
api.add_resource(SignIn, "/signin")
api.add_resource(SignOut, "/signout")
api.add_resource(CustomerDashboard, "/customer/dashboard")
api.add_resource(CustomerServices, "/customer/services", "/customer/services/<int:request_id>")
api.add_resource(SearchServices, "/customer/search-services")
api.add_resource(SearchProfessionals, "/admin/search-professionals")
api.add_resource(ProfessionalsByServiceType, "/service/<int:service_id>/professionals")  # Add this line
api.add_resource(adminDashboard, "/admin/dashboard")
api.add_resource(adminService, "/admin/service", "/admin/service/<int:service_id>")
api.add_resource(adminCustomers, "/admin/customers", "/admin/customers/<int:user_id>")
api.add_resource(adminProfessional, "/admin/professionals", "/admin/professionals/<int:professional_id>")
api.add_resource(ProfessionalServiceRequests, "/professional/requests", "/professional/requests/<int:request_id>")

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

if __name__ == '__main__':
    create_admin()  # Ensure admin exists before starting the app
    app.run(debug=True)
