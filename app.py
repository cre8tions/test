"""
Main Flask application module for the tire store inventory management application.
"""
import os
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Tire
from functools import wraps

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
            description=request.form.get('description'),
            warranty_months=request.form.get('warranty_months'),
            speed_rating=request.form.get('speed_rating'),
            load_index=request.form.get('load_index'),
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
        tire.description = request.form.get('description')
        tire.warranty_months = request.form.get('warranty_months')
        tire.speed_rating = request.form.get('speed_rating')
        tire.load_index = request.form.get('load_index')
        
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
                    description='All-weather tire for year-round performance',
                    warranty_months=60,
                    speed_rating='H',
                    load_index='94',
                    created_by=1
                )
            ]
            
            for tire in sample_tires:
                db.session.add(tire)
            
            db.session.commit()
            print('Database initialized with sample data.')


if __name__ == '__main__':
    init_db()
    # Only enable debug mode if explicitly set in environment
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
