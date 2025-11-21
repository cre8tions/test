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
