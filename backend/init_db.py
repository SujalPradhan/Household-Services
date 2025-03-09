import argparse
from models import db, user_datastore, Admin
from app import app
from flask_security.utils import hash_password

parser = argparse.ArgumentParser(description='Initialize the database.')
parser.add_argument('--drop', action='store_true', help='Drop all tables before creating them')
args = parser.parse_args()

with app.app_context():
    if args.drop:
        db.drop_all()
    
    # Create all tables
    db.create_all()

    # Ensure roles exist
    for role in ['admin', 'professional', 'customer']:
        if not user_datastore.find_role(role):
            user_datastore.create_role(name=role)
    db.session.commit()

    # Create Admin
    admin_user = user_datastore.find_user(email='admin@abc.com')
    if not admin_user:
        admin_user = user_datastore.create_user(email='admin@abc.com', password=hash_password('admin123'))
        user_datastore.add_role_to_user(admin_user, 'admin')
        db.session.add(Admin(user_id=admin_user.id, name="Admin User"))
        db.session.commit()

    # Create Service Professional
    professional = user_datastore.find_user(email='p1@abc.com')
    if not professional:
        new_professional = user_datastore.create_user(email='p1@abc.com', password=hash_password('p1'))
        user_datastore.add_role_to_user(new_professional, 'professional')
        db.session.commit()

    # Create Customer
    customer = user_datastore.find_user(email='c1@abc.com')
    if not customer:
        new_customer = user_datastore.create_user(email='c1@abc.com', password=hash_password('c1'))
        user_datastore.add_role_to_user(new_customer, 'customer')
        db.session.commit()
