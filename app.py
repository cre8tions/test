"""
Main Flask application module for the tire store inventory management application.
"""
import os
from datetime import datetime, date, time, timedelta
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Tire, VehicleTireSize, ServiceItem, Appointment, AppointmentItem
from functools import wraps
from sqlalchemy import and_, or_

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tire_store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return User.query.get(int(user_id))


def role_required(*roles):
    """Decorator to require specific roles."""
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if current_user.role not in roles:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('index'))
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper


@app.route('/')
def index():
    """Landing page route."""
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page route."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Logout route."""
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard page route."""
    tires = Tire.query.all()
    low_stock_tires = Tire.query.filter(Tire.quantity_in_stock <= Tire.reorder_level).all()
    return render_template('dashboard.html', tires=tires, low_stock_tires=low_stock_tires)


@app.route('/inventory')
@login_required
def inventory():
    """Inventory listing page."""
    tires = Tire.query.order_by(Tire.brand, Tire.model).all()
    return render_template('inventory.html', tires=tires)


@app.route('/tire/add', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'sales')
def add_tire():
    """Add new tire to inventory."""
    if request.method == 'POST':
        tire = Tire(
            brand=request.form.get('brand'),
            model=request.form.get('model'),
            size=request.form.get('size'),
            type=request.form.get('type'),
            wholesale_price=request.form.get('wholesale_price'),
            retail_price=request.form.get('retail_price'),
            supplier=request.form.get('supplier'),
            supplier_contact=request.form.get('supplier_contact'),
            supplier_part_number=request.form.get('supplier_part_number'),
            quantity_in_stock=request.form.get('quantity_in_stock', 0),
            reorder_level=request.form.get('reorder_level', 10),
            warehouse_location=request.form.get('warehouse_location'),
            description=request.form.get('description'),
            warranty_months=request.form.get('warranty_months'),
            speed_rating=request.form.get('speed_rating'),
            load_index=request.form.get('load_index'),
            special_order_available='special_order_available' in request.form,
            created_by=current_user.id
        )
        db.session.add(tire)
        db.session.commit()
        flash('Tire added successfully!', 'success')
        return redirect(url_for('inventory'))
    
    return render_template('add_tire.html')


@app.route('/tire/<int:tire_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'sales')
def edit_tire(tire_id):
    """Edit existing tire."""
    tire = Tire.query.get_or_404(tire_id)
    
    if request.method == 'POST':
        tire.brand = request.form.get('brand')
        tire.model = request.form.get('model')
        tire.size = request.form.get('size')
        tire.type = request.form.get('type')
        tire.wholesale_price = request.form.get('wholesale_price')
        tire.retail_price = request.form.get('retail_price')
        tire.supplier = request.form.get('supplier')
        tire.supplier_contact = request.form.get('supplier_contact')
        tire.supplier_part_number = request.form.get('supplier_part_number')
        tire.quantity_in_stock = request.form.get('quantity_in_stock')
        tire.reorder_level = request.form.get('reorder_level')
        tire.warehouse_location = request.form.get('warehouse_location')
        tire.description = request.form.get('description')
        tire.warranty_months = request.form.get('warranty_months')
        tire.speed_rating = request.form.get('speed_rating')
        tire.load_index = request.form.get('load_index')
        tire.special_order_available = 'special_order_available' in request.form
        
        db.session.commit()
        flash('Tire updated successfully!', 'success')
        return redirect(url_for('inventory'))
    
    return render_template('edit_tire.html', tire=tire)


@app.route('/tire/<int:tire_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_tire(tire_id):
    """Delete tire (admin only)."""
    tire = Tire.query.get_or_404(tire_id)
    db.session.delete(tire)
    db.session.commit()
    flash('Tire deleted successfully!', 'success')
    return redirect(url_for('inventory'))


@app.route('/api/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'tire-store'
    })


@app.route('/order')
def customer_order():
    """Customer tire ordering page."""
    # Get unique makes for the dropdown
    makes = db.session.query(VehicleTireSize.make).distinct().order_by(VehicleTireSize.make).all()
    makes = [make[0] for make in makes]
    return render_template('order.html', makes=makes)


@app.route('/api/vehicle-models/<make>')
def get_vehicle_models(make):
    """API endpoint to get models for a specific make."""
    models = db.session.query(VehicleTireSize.model).filter_by(make=make).distinct().order_by(VehicleTireSize.model).all()
    return jsonify([model[0] for model in models])


@app.route('/api/vehicle-years/<make>/<model>')
def get_vehicle_years(make, model):
    """API endpoint to get years for a specific make and model."""
    years = db.session.query(VehicleTireSize.year).filter_by(make=make, model=model).distinct().order_by(VehicleTireSize.year.desc()).all()
    return jsonify([year[0] for year in years])


@app.route('/api/tire-size/<make>/<model>/<int:year>')
def get_tire_size(make, model, year):
    """API endpoint to get tire size for a specific vehicle."""
    vehicle = VehicleTireSize.query.filter_by(make=make, model=model, year=year).first()
    if vehicle:
        return jsonify({'tire_size': vehicle.tire_size})
    return jsonify({'error': 'Vehicle not found'}), 404


@app.route('/api/tires-by-size/<path:size>')
def get_tires_by_size(size):
    """API endpoint to get all tires matching a specific size."""
    tires = Tire.query.filter_by(size=size).order_by(Tire.brand, Tire.model).all()
    return jsonify([{
        'id': tire.id,
        'brand': tire.brand,
        'model': tire.model,
        'size': tire.size,
        'type': tire.type,
        'retail_price': float(tire.retail_price),
        'quantity_in_stock': tire.quantity_in_stock,
        'in_stock': tire.quantity_in_stock > 0,
        'description': tire.description,
        'warranty_months': tire.warranty_months,
        'speed_rating': tire.speed_rating,
        'load_index': tire.load_index,
        'special_order_available': tire.special_order_available
    } for tire in tires])


@app.route('/appointments')
def appointments():
    """Appointment scheduling page."""
    return render_template('appointments.html')


@app.route('/api/service-items')
def get_service_items():
    """API endpoint to get all active service items."""
    items = ServiceItem.query.filter_by(is_active=True).order_by(ServiceItem.name).all()
    return jsonify([{
        'id': item.id,
        'name': item.name,
        'description': item.description,
        'duration_minutes': item.duration_minutes,
        'price': float(item.price),
        'max_concurrent': item.max_concurrent
    } for item in items])


@app.route('/api/check-availability', methods=['POST'])
def check_availability():
    """Check if a time slot is available for the selected services."""
    data = request.get_json()
    appointment_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    appointment_time = datetime.strptime(data['time'], '%H:%M').time()
    service_ids = data['service_ids']
    
    # Check if date/time is within business hours
    if not is_within_business_hours(appointment_date, appointment_time):
        return jsonify({'available': False, 'reason': 'Outside business hours'})
    
    # Get service items
    services = ServiceItem.query.filter(ServiceItem.id.in_(service_ids)).all()
    if len(services) != len(service_ids):
        return jsonify({'available': False, 'reason': 'Invalid service items'})
    
    # Calculate total duration
    total_duration = sum(s.duration_minutes for s in services)
    
    # Check if appointment would end within business hours
    end_time = (datetime.combine(date.today(), appointment_time) + timedelta(minutes=total_duration)).time()
    if not is_within_business_hours(appointment_date, end_time):
        return jsonify({'available': False, 'reason': 'Appointment would extend beyond business hours'})
    
    # Check for conflicts with existing appointments
    conflicts = check_scheduling_conflicts(appointment_date, appointment_time, services, total_duration)
    
    if conflicts:
        return jsonify({'available': False, 'reason': 'Time slot conflicts with existing appointments'})
    
    return jsonify({'available': True})


@app.route('/api/appointments', methods=['POST'])
def create_appointment():
    """Create a new appointment with multiple service items."""
    data = request.get_json()
    
    # Validate input
    required_fields = ['customer_name', 'customer_phone', 'car_make', 'car_model', 'date', 'time', 'service_items']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
    
    try:
        appointment_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        appointment_time = datetime.strptime(data['time'], '%H:%M').time()
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid date or time format'}), 400
    
    # Validate service items
    service_items_data = data['service_items']
    if not service_items_data:
        return jsonify({'success': False, 'error': 'At least one service item required'}), 400
    
    # Get service items from database
    service_ids = [item['id'] for item in service_items_data]
    services = {s.id: s for s in ServiceItem.query.filter(ServiceItem.id.in_(service_ids)).all()}
    
    if len(services) != len(service_ids):
        return jsonify({'success': False, 'error': 'Invalid service items'}), 400
    
    # Calculate totals
    total_duration = 0
    total_price = 0
    
    for item_data in service_items_data:
        service = services[item_data['id']]
        quantity = item_data.get('quantity', 1)
        
        # For "New Tires", duration is per tire
        if service.name == 'New Tires':
            duration = service.duration_minutes * quantity
        else:
            duration = service.duration_minutes
        
        total_duration += duration
        total_price += float(service.price) * quantity
    
    # Check availability one more time
    if not is_within_business_hours(appointment_date, appointment_time):
        return jsonify({'success': False, 'error': 'Outside business hours'}), 400
    
    end_time = (datetime.combine(date.today(), appointment_time) + timedelta(minutes=total_duration)).time()
    if not is_within_business_hours(appointment_date, end_time):
        return jsonify({'success': False, 'error': 'Appointment would extend beyond business hours'}), 400
    
    conflicts = check_scheduling_conflicts(appointment_date, appointment_time, services.values(), total_duration)
    if conflicts:
        return jsonify({'success': False, 'error': 'Time slot no longer available'}), 400
    
    # Create appointment
    appointment = Appointment(
        customer_name=data['customer_name'],
        customer_phone=data['customer_phone'],
        car_make=data['car_make'],
        car_model=data['car_model'],
        scheduled_date=appointment_date,
        scheduled_time=appointment_time,
        total_duration_minutes=total_duration,
        total_price=total_price,
        notes=data.get('notes', '')
    )
    
    db.session.add(appointment)
    db.session.flush()  # Get the appointment ID
    
    # Create appointment items
    for item_data in service_items_data:
        service = services[item_data['id']]
        quantity = item_data.get('quantity', 1)
        
        # Calculate duration for this specific item
        if service.name == 'New Tires':
            duration = service.duration_minutes * quantity
        else:
            duration = service.duration_minutes
        
        appointment_item = AppointmentItem(
            appointment_id=appointment.id,
            service_item_id=service.id,
            quantity=quantity,
            duration_minutes=duration,
            price=float(service.price) * quantity
        )
        db.session.add(appointment_item)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'appointment_id': appointment.id,
        'message': 'Appointment scheduled successfully!'
    })


def is_within_business_hours(appointment_date, appointment_time):
    """Check if the given date and time are within business hours."""
    # Monday = 0, Saturday = 5, Sunday = 6
    weekday = appointment_date.weekday()
    
    # Closed on Sundays
    if weekday == 6:
        return False
    
    # Convert time to minutes for easier comparison
    time_minutes = appointment_time.hour * 60 + appointment_time.minute
    
    if weekday < 5:  # Monday-Friday: 8:30am - 3:30pm
        open_time = 8 * 60 + 30  # 8:30am
        close_time = 15 * 60 + 30  # 3:30pm
    else:  # Saturday: 8:30am - 11:30am
        open_time = 8 * 60 + 30  # 8:30am
        close_time = 11 * 60 + 30  # 11:30am
    
    return open_time <= time_minutes <= close_time


def check_scheduling_conflicts(appointment_date, appointment_time, services, total_duration):
    """
    Check if scheduling the given services would conflict with existing appointments.
    Returns list of conflicts (empty if no conflicts).
    """
    # Calculate time range for the new appointment
    start_datetime = datetime.combine(appointment_date, appointment_time)
    end_datetime = start_datetime + timedelta(minutes=total_duration)
    
    # Get all appointments on the same date
    existing_appointments = Appointment.query.filter(
        Appointment.scheduled_date == appointment_date,
        Appointment.status == 'scheduled'
    ).all()
    
    conflicts = []
    
    for service in services:
        # Count how many of this service are already scheduled during the time range
        concurrent_count = 0
        
        for existing in existing_appointments:
            existing_start = datetime.combine(appointment_date, existing.scheduled_time)
            existing_end = existing_start + timedelta(minutes=existing.total_duration_minutes)
            
            # Check if time ranges overlap
            if not (end_datetime <= existing_start or start_datetime >= existing_end):
                # Times overlap - check if this service is in the existing appointment
                for item in existing.items:
                    if item.service_item_id == service.id:
                        concurrent_count += 1
                        break
        
        # Check if we've exceeded the max concurrent for this service
        if concurrent_count >= service.max_concurrent:
            conflicts.append(f'{service.name} is fully booked at this time')
    
    return conflicts


def init_db():
    """Initialize database with sample data."""
    with app.app_context():
        db.create_all()
        
        # Create default users if they don't exist
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email='admin@tirestore.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            
            sales = User(username='sales', email='sales@tirestore.com', role='sales')
            sales.set_password('sales123')
            db.session.add(sales)
            
            accounting = User(username='accounting', email='accounting@tirestore.com', role='accounting')
            accounting.set_password('accounting123')
            db.session.add(accounting)
            
            # Add sample tires
            sample_tires = [
                Tire(
                    brand='Michelin',
                    model='Pilot Sport 4S',
                    size='245/40R18',
                    type='Performance',
                    wholesale_price=180.00,
                    retail_price=299.99,
                    supplier='Michelin Distribution',
                    supplier_contact='1-800-MICHELIN',
                    supplier_part_number='MICH-PS4S-245-40-18',
                    quantity_in_stock=24,
                    reorder_level=10,
                    warehouse_location='Warehouse A - Aisle 3 - Shelf B',
                    description='Ultra-high performance summer tire',
                    warranty_months=36,
                    speed_rating='Y',
                    load_index='97',
                    created_by=1
                ),
                Tire(
                    brand='Bridgestone',
                    model='Blizzak WS90',
                    size='225/60R17',
                    type='Winter',
                    wholesale_price=120.00,
                    retail_price=199.99,
                    supplier='Bridgestone Wholesale',
                    supplier_contact='1-800-BRIDGESTONE',
                    supplier_part_number='BS-WS90-225-60-17',
                    quantity_in_stock=36,
                    reorder_level=15,
                    warehouse_location='Warehouse B - Aisle 1 - Shelf A',
                    description='Premium winter tire with excellent ice traction',
                    warranty_months=48,
                    speed_rating='T',
                    load_index='99',
                    created_by=1
                ),
                Tire(
                    brand='Goodyear',
                    model='Assurance WeatherReady',
                    size='215/55R17',
                    type='All-Season',
                    wholesale_price=95.00,
                    retail_price=159.99,
                    supplier='Goodyear Direct',
                    supplier_contact='1-800-GOODYEAR',
                    supplier_part_number='GY-AWR-215-55-17',
                    quantity_in_stock=48,
                    reorder_level=20,
                    warehouse_location='Warehouse A - Aisle 5 - Shelf C',
                    description='All-weather tire for year-round performance',
                    warranty_months=60,
                    speed_rating='H',
                    load_index='94',
                    created_by=1
                )
            ]
            
            for tire in sample_tires:
                db.session.add(tire)
            
            # Add vehicle tire size data for major manufacturers
            vehicle_tire_sizes = [
                # Honda
                VehicleTireSize(make='Honda', model='Accord', year=2023, tire_size='235/45R18'),
                VehicleTireSize(make='Honda', model='Accord', year=2022, tire_size='235/45R18'),
                VehicleTireSize(make='Honda', model='Accord', year=2021, tire_size='235/45R18'),
                VehicleTireSize(make='Honda', model='Civic', year=2023, tire_size='235/40R18'),
                VehicleTireSize(make='Honda', model='Civic', year=2022, tire_size='235/40R18'),
                VehicleTireSize(make='Honda', model='Civic', year=2021, tire_size='215/55R16'),
                VehicleTireSize(make='Honda', model='CR-V', year=2023, tire_size='235/60R18'),
                VehicleTireSize(make='Honda', model='CR-V', year=2022, tire_size='235/60R18'),
                VehicleTireSize(make='Honda', model='CR-V', year=2021, tire_size='235/60R18'),
                
                # Toyota
                VehicleTireSize(make='Toyota', model='Camry', year=2023, tire_size='235/45R18'),
                VehicleTireSize(make='Toyota', model='Camry', year=2022, tire_size='235/45R18'),
                VehicleTireSize(make='Toyota', model='Camry', year=2021, tire_size='215/55R17'),
                VehicleTireSize(make='Toyota', model='Corolla', year=2023, tire_size='225/45R17'),
                VehicleTireSize(make='Toyota', model='Corolla', year=2022, tire_size='225/45R17'),
                VehicleTireSize(make='Toyota', model='Corolla', year=2021, tire_size='215/45R17'),
                VehicleTireSize(make='Toyota', model='RAV4', year=2023, tire_size='225/65R17'),
                VehicleTireSize(make='Toyota', model='RAV4', year=2022, tire_size='225/65R17'),
                VehicleTireSize(make='Toyota', model='RAV4', year=2021, tire_size='225/65R17'),
                
                # Ford
                VehicleTireSize(make='Ford', model='F-150', year=2023, tire_size='275/65R18'),
                VehicleTireSize(make='Ford', model='F-150', year=2022, tire_size='275/65R18'),
                VehicleTireSize(make='Ford', model='F-150', year=2021, tire_size='265/70R17'),
                VehicleTireSize(make='Ford', model='Mustang', year=2023, tire_size='245/40R18'),
                VehicleTireSize(make='Ford', model='Mustang', year=2022, tire_size='245/40R18'),
                VehicleTireSize(make='Ford', model='Mustang', year=2021, tire_size='235/55R17'),
                VehicleTireSize(make='Ford', model='Explorer', year=2023, tire_size='255/55R20'),
                VehicleTireSize(make='Ford', model='Explorer', year=2022, tire_size='255/55R20'),
                VehicleTireSize(make='Ford', model='Explorer', year=2021, tire_size='245/60R18'),
                
                # Chevrolet
                VehicleTireSize(make='Chevrolet', model='Silverado', year=2023, tire_size='275/60R20'),
                VehicleTireSize(make='Chevrolet', model='Silverado', year=2022, tire_size='275/60R20'),
                VehicleTireSize(make='Chevrolet', model='Silverado', year=2021, tire_size='265/65R18'),
                VehicleTireSize(make='Chevrolet', model='Malibu', year=2023, tire_size='225/55R17'),
                VehicleTireSize(make='Chevrolet', model='Malibu', year=2022, tire_size='225/55R17'),
                VehicleTireSize(make='Chevrolet', model='Malibu', year=2021, tire_size='225/55R17'),
                VehicleTireSize(make='Chevrolet', model='Equinox', year=2023, tire_size='225/65R17'),
                VehicleTireSize(make='Chevrolet', model='Equinox', year=2022, tire_size='225/65R17'),
                VehicleTireSize(make='Chevrolet', model='Equinox', year=2021, tire_size='225/65R17'),
                
                # Nissan
                VehicleTireSize(make='Nissan', model='Altima', year=2023, tire_size='235/40R19'),
                VehicleTireSize(make='Nissan', model='Altima', year=2022, tire_size='235/40R19'),
                VehicleTireSize(make='Nissan', model='Altima', year=2021, tire_size='215/60R16'),
                VehicleTireSize(make='Nissan', model='Rogue', year=2023, tire_size='225/65R17'),
                VehicleTireSize(make='Nissan', model='Rogue', year=2022, tire_size='225/65R17'),
                VehicleTireSize(make='Nissan', model='Rogue', year=2021, tire_size='225/65R17'),
                
                # BMW
                VehicleTireSize(make='BMW', model='3 Series', year=2023, tire_size='225/45R18'),
                VehicleTireSize(make='BMW', model='3 Series', year=2022, tire_size='225/45R18'),
                VehicleTireSize(make='BMW', model='3 Series', year=2021, tire_size='225/50R17'),
                VehicleTireSize(make='BMW', model='X5', year=2023, tire_size='275/40R21'),
                VehicleTireSize(make='BMW', model='X5', year=2022, tire_size='275/40R21'),
                VehicleTireSize(make='BMW', model='X5', year=2021, tire_size='275/45R20'),
                
                # Mercedes-Benz
                VehicleTireSize(make='Mercedes-Benz', model='C-Class', year=2023, tire_size='225/50R17'),
                VehicleTireSize(make='Mercedes-Benz', model='C-Class', year=2022, tire_size='225/50R17'),
                VehicleTireSize(make='Mercedes-Benz', model='C-Class', year=2021, tire_size='225/45R18'),
                VehicleTireSize(make='Mercedes-Benz', model='GLE', year=2023, tire_size='275/50R20'),
                VehicleTireSize(make='Mercedes-Benz', model='GLE', year=2022, tire_size='275/50R20'),
                VehicleTireSize(make='Mercedes-Benz', model='GLE', year=2021, tire_size='265/50R19'),
                
                # Tesla
                VehicleTireSize(make='Tesla', model='Model 3', year=2023, tire_size='235/45R18'),
                VehicleTireSize(make='Tesla', model='Model 3', year=2022, tire_size='235/45R18'),
                VehicleTireSize(make='Tesla', model='Model 3', year=2021, tire_size='235/45R18'),
                VehicleTireSize(make='Tesla', model='Model Y', year=2023, tire_size='255/45R19'),
                VehicleTireSize(make='Tesla', model='Model Y', year=2022, tire_size='255/45R19'),
                VehicleTireSize(make='Tesla', model='Model Y', year=2021, tire_size='255/45R19'),
                
                # Jeep
                VehicleTireSize(make='Jeep', model='Wrangler', year=2023, tire_size='245/75R17'),
                VehicleTireSize(make='Jeep', model='Wrangler', year=2022, tire_size='245/75R17'),
                VehicleTireSize(make='Jeep', model='Wrangler', year=2021, tire_size='245/75R17'),
                VehicleTireSize(make='Jeep', model='Grand Cherokee', year=2023, tire_size='265/60R18'),
                VehicleTireSize(make='Jeep', model='Grand Cherokee', year=2022, tire_size='265/60R18'),
                VehicleTireSize(make='Jeep', model='Grand Cherokee', year=2021, tire_size='265/60R18'),
                
                # Subaru
                VehicleTireSize(make='Subaru', model='Outback', year=2023, tire_size='225/65R17'),
                VehicleTireSize(make='Subaru', model='Outback', year=2022, tire_size='225/65R17'),
                VehicleTireSize(make='Subaru', model='Outback', year=2021, tire_size='225/65R17'),
                VehicleTireSize(make='Subaru', model='Forester', year=2023, tire_size='225/55R18'),
                VehicleTireSize(make='Subaru', model='Forester', year=2022, tire_size='225/55R18'),
                VehicleTireSize(make='Subaru', model='Forester', year=2021, tire_size='225/60R17'),
            ]
            
            for vehicle in vehicle_tire_sizes:
                db.session.add(vehicle)
            
            # Add additional tire inventory to match common sizes
            additional_tires = [
                Tire(
                    brand='Continental',
                    model='PureContact LS',
                    size='235/45R18',
                    type='All-Season',
                    wholesale_price=105.00,
                    retail_price=175.99,
                    supplier='Continental Tire',
                    supplier_contact='1-800-CONTINENTAL',
                    supplier_part_number='CONT-PCLS-235-45-18',
                    quantity_in_stock=32,
                    reorder_level=15,
                    warehouse_location='Warehouse A - Aisle 2 - Shelf A',
                    description='Premium all-season touring tire',
                    warranty_months=70,
                    speed_rating='H',
                    load_index='94',
                    created_by=1
                ),
                Tire(
                    brand='Bridgestone',
                    model='Turanza EL450',
                    size='225/45R17',
                    type='All-Season',
                    wholesale_price=95.00,
                    retail_price=159.99,
                    supplier='Bridgestone Wholesale',
                    supplier_contact='1-800-BRIDGESTONE',
                    supplier_part_number='BS-EL450-225-45-17',
                    quantity_in_stock=28,
                    reorder_level=15,
                    warehouse_location='Warehouse B - Aisle 2 - Shelf C',
                    description='Luxury touring all-season tire',
                    warranty_months=65,
                    speed_rating='V',
                    load_index='94',
                    created_by=1
                ),
                Tire(
                    brand='Goodyear',
                    model='Eagle F1 Asymmetric',
                    size='225/45R18',
                    type='Performance',
                    wholesale_price=130.00,
                    retail_price=219.99,
                    supplier='Goodyear Direct',
                    supplier_contact='1-800-GOODYEAR',
                    supplier_part_number='GY-EF1A-225-45-18',
                    quantity_in_stock=0,
                    reorder_level=10,
                    warehouse_location='Warehouse A - Aisle 4 - Shelf A',
                    description='High-performance summer tire',
                    warranty_months=45,
                    speed_rating='Y',
                    load_index='95',
                    special_order_available=True,
                    created_by=1
                ),
                Tire(
                    brand='Pirelli',
                    model='P Zero',
                    size='245/40R18',
                    type='Performance',
                    wholesale_price=175.00,
                    retail_price=289.99,
                    supplier='Pirelli Distribution',
                    supplier_contact='1-800-PIRELLI',
                    supplier_part_number='PIR-PZ-245-40-18',
                    quantity_in_stock=18,
                    reorder_level=8,
                    warehouse_location='Warehouse A - Aisle 3 - Shelf A',
                    description='Ultra-high performance tire',
                    warranty_months=30,
                    speed_rating='Y',
                    load_index='97',
                    created_by=1
                ),
                Tire(
                    brand='Michelin',
                    model='CrossClimate 2',
                    size='225/65R17',
                    type='All-Season',
                    wholesale_price=110.00,
                    retail_price=184.99,
                    supplier='Michelin Distribution',
                    supplier_contact='1-800-MICHELIN',
                    supplier_part_number='MICH-CC2-225-65-17',
                    quantity_in_stock=40,
                    reorder_level=20,
                    warehouse_location='Warehouse B - Aisle 1 - Shelf C',
                    description='All-weather crossover tire',
                    warranty_months=60,
                    speed_rating='H',
                    load_index='102',
                    created_by=1
                ),
            ]
            
            for tire in additional_tires:
                db.session.add(tire)
            
            # Add service items for appointment scheduling
            if not ServiceItem.query.first():
                service_items = [
                    ServiceItem(
                        name='Tire Rotation',
                        description='Professional tire rotation service to extend tire life',
                        duration_minutes=15,
                        price=29.99,
                        max_concurrent=2
                    ),
                    ServiceItem(
                        name='New Tires',
                        description='Installation of new tires (5 minutes per tire)',
                        duration_minutes=5,  # Per tire
                        price=25.00,  # Per tire installation
                        max_concurrent=999  # No limit on tire installations
                    ),
                    ServiceItem(
                        name='Alignment',
                        description='Wheel alignment service for optimal handling',
                        duration_minutes=60,
                        price=79.99,
                        max_concurrent=2
                    ),
                    ServiceItem(
                        name='Inspection',
                        description='Comprehensive vehicle inspection',
                        duration_minutes=60,
                        price=49.99,
                        max_concurrent=1
                    ),
                    ServiceItem(
                        name='Emissions',
                        description='Emissions testing service',
                        duration_minutes=30,
                        price=35.00,
                        max_concurrent=1
                    ),
                ]
                
                for item in service_items:
                    db.session.add(item)
            
            db.session.commit()
            print('Database initialized with sample data.')



if __name__ == '__main__':
    init_db()
    # Only enable debug mode if explicitly set in environment
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
