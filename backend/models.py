from flask_sqlalchemy import SQLAlchemy
from flask_security import RoleMixin, UserMixin, SQLAlchemyUserDatastore
from datetime import datetime
import uuid
from enum import Enum

db = SQLAlchemy()

# Association Table for Many-to-Many Relationship between Users and Roles
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255), nullable=True)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    user = db.relationship('User', backref=db.backref('admin', uselist=False))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=True)
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    fs_uniquifier = db.Column(db.String(64), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    pincode = db.Column(db.String(6))

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    
    user = db.relationship('User', backref=db.backref('customer', uselist=False))
    service_requests = db.relationship('ServiceRequest', backref='customer', lazy=True)

class ServiceTypeEnum(Enum):
    PLUMBING = "PLUMBING"
    ELECTRICAL = "ELECTRICAL"
    CLEANING = "CLEANING"
    CARPENTRY = "CARPENTRY"
    PAINTING = "PAINTING"

class ServiceProfessional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    service_type = db.Column(db.Enum(ServiceTypeEnum), nullable=False)
    experience = db.Column(db.Integer, nullable=True, default=0)
    description = db.Column(db.Text, nullable=True)
    approved = db.Column(db.Boolean, default=False)
    blocked = db.Column(db.Boolean, default=False)
    user = db.relationship('User', backref=db.backref('service_professional', uselist=False))
    service_requests = db.relationship('ServiceRequest', backref='professional', lazy=True)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)  # Base price for the service
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    service_requests = db.relationship('ServiceRequest', backref='service', lazy=True)
    service_type = db.Column(db.Enum(ServiceTypeEnum), nullable=False)

class ServiceStatusEnum(Enum):
    REQUESTED = 'requested'  # Set by customer initially
    ACCEPTED = 'accepted'    # Set by professional when they accept
    COMPLETED = 'completed'  # Set by customer after service is done
    CLOSED = 'closed'        # Set by professional to finalize
    CANCELLED = 'cancelled'  # Either party can cancel

class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_status = db.Column(db.Enum(ServiceStatusEnum), default=ServiceStatusEnum.REQUESTED)
    remarks = db.Column(db.String, nullable=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('service_professional.id'), nullable=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    date_of_request = db.Column(db.DateTime, default=datetime.utcnow)
    preferred_date = db.Column(db.DateTime, nullable=True)  # Customer's preferred service date
    price = db.Column(db.Float, nullable=True)  # Final price for this service request

user_datastore = SQLAlchemyUserDatastore(db, User, Role)

