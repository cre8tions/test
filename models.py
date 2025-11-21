"""
Database models for the Tire Store Inventory Management application.
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model with role-based access control."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='sales')  # admin, sales, accounting
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        """Hash and set user password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash."""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Tire(db.Model):
    """Tire inventory model."""
    __tablename__ = 'tires'
    
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    size = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # All-Season, Winter, Summer, Performance
    
    # Pricing information
    wholesale_price = db.Column(db.Numeric(10, 2), nullable=False)
    retail_price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Supplier information
    supplier = db.Column(db.String(100), nullable=False)
    supplier_contact = db.Column(db.String(100))
    supplier_part_number = db.Column(db.String(50))
    
    # Inventory
    quantity_in_stock = db.Column(db.Integer, default=0)
    reorder_level = db.Column(db.Integer, default=10)
    warehouse_location = db.Column(db.String(100))
    special_order_available = db.Column(db.Boolean, default=False)
    
    # Additional details
    description = db.Column(db.Text)
    warranty_months = db.Column(db.Integer)
    speed_rating = db.Column(db.String(10))
    load_index = db.Column(db.String(10))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def __repr__(self):
        return f'<Tire {self.brand} {self.model} {self.size}>'


class VehicleTireSize(db.Model):
    """Vehicle to tire size mapping."""
    __tablename__ = 'vehicle_tire_sizes'
    
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    tire_size = db.Column(db.String(50), nullable=False)
    
    def __repr__(self):
        return f'<VehicleTireSize {self.year} {self.make} {self.model} - {self.tire_size}>'


class ServiceItem(db.Model):
    """Service items that can be scheduled for appointments."""
    __tablename__ = 'service_items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    duration_minutes = db.Column(db.Integer, nullable=False)  # Base duration in minutes
    price = db.Column(db.Numeric(10, 2), nullable=False)
    max_concurrent = db.Column(db.Integer, nullable=True)  # Max number that can be scheduled simultaneously; None means unlimited
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ServiceItem {self.name}>'


class Appointment(db.Model):
    """Customer appointment for services."""
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    car_make = db.Column(db.String(50), nullable=False)
    car_model = db.Column(db.String(50), nullable=False)
    scheduled_date = db.Column(db.Date, nullable=False)
    scheduled_time = db.Column(db.Time, nullable=False)
    total_duration_minutes = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to appointment items
    items = db.relationship('AppointmentItem', back_populates='appointment', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Appointment {self.customer_name} on {self.scheduled_date} at {self.scheduled_time}>'


class AppointmentItem(db.Model):
    """Join table for appointments and service items (many-to-many)."""
    __tablename__ = 'appointment_items'
    
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    service_item_id = db.Column(db.Integer, db.ForeignKey('service_items.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)  # For items like "New Tires" where quantity matters
    duration_minutes = db.Column(db.Integer, nullable=False)  # Actual duration for this item
    price = db.Column(db.Numeric(10, 2), nullable=False)  # Price at time of booking
    
    # Relationships
    appointment = db.relationship('Appointment', back_populates='items')
    service_item = db.relationship('ServiceItem')
    
    def __repr__(self):
        return f'<AppointmentItem {self.service_item_id} for Appointment {self.appointment_id}>'


class CustomerOrder(db.Model):
    """Customer order for tires and services."""
    __tablename__ = 'customer_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(120))
    customer_phone = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='new')  # new, accepted, in_progress, completed
    total_price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to order items
    items = db.relationship('CustomerOrderItem', back_populates='order', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<CustomerOrder {self.id} - {self.customer_name} - {self.status}>'


class CustomerOrderItem(db.Model):
    """Items in a customer order."""
    __tablename__ = 'customer_order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('customer_orders.id'), nullable=False)
    tire_id = db.Column(db.Integer, db.ForeignKey('tires.id'))
    service_item_id = db.Column(db.Integer, db.ForeignKey('service_items.id'))
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    item_type = db.Column(db.String(20), nullable=False)  # 'tire' or 'service'
    
    # Relationships
    order = db.relationship('CustomerOrder', back_populates='items')
    tire = db.relationship('Tire')
    service_item = db.relationship('ServiceItem')
    
    def __repr__(self):
        return f'<CustomerOrderItem {self.id} for Order {self.order_id}>'
