# TireTrack Pro - Tire Store Inventory Management System

A modern tire store inventory management application built with Flask, featuring role-based authentication, comprehensive tire tracking, and a beautiful modern UI.

## Features

### 🔐 Authentication & Access Control
- Secure login system with password hashing
- Role-based access control (Admin, Sales, Accounting)
- Session management with Flask-Login

### 📦 Inventory Management
- Track tire inventory with comprehensive details:
  - Brand, Model, Size, Type
  - Wholesale and Retail pricing
  - Supplier information and contact details
  - Stock levels with automatic reorder alerts
  - Technical specifications (speed rating, load index, warranty)
- Add, edit, and delete tire records (role-based permissions)
- Real-time inventory statistics

### 📊 Dashboard & Analytics
- Overview dashboard with key metrics
- Low stock alerts
- Inventory value tracking
- Quick access to recent inventory

### 🎨 Modern UI Design
- Gradient backgrounds and card-based layouts
- Responsive design for all devices
- Icon integration with Font Awesome
- Smooth animations and transitions
- Color-coded badges for tire types and user roles

## Project Structure

```
.
├── app.py                  # Main Flask application with routes
├── models.py               # Database models (User, Tire)
├── config.py              # Configuration settings
├── requirements.txt        # Python dependencies
├── templates/              # HTML templates
│   ├── base.html          # Base template with navigation
│   ├── index.html         # Landing page
│   ├── login.html         # Login page
│   ├── dashboard.html     # Analytics dashboard
│   ├── inventory.html     # Tire inventory listing
│   ├── add_tire.html      # Add tire form
│   └── edit_tire.html     # Edit tire form
├── static/                 # Static files
│   └── css/
│       └── style.css      # Modern CSS styling
└── README.md              # This file
```

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/cre8tions/test.git
cd test
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- On Windows:
  ```bash
  venv\Scripts\activate
  ```
- On macOS/Linux:
  ```bash
  source venv/bin/activate
  ```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

Start the Flask development server:

```bash
python app.py
```

The application will be available at `http://localhost:5000`

**Note:** The database is automatically initialized with sample data on first run.

## Demo Credentials

Login with one of these demo accounts:

- **Administrator**
  - Username: `admin`
  - Password: `admin123`
  - Full system access, can manage all inventory and delete items

- **Sales**
  - Username: `sales`
  - Password: `sales123`
  - Can view, add, and edit tire inventory

- **Accounting**
  - Username: `accounting`
  - Password: `accounting123`
  - Read-only access to view inventory and pricing data

## Member Levels & Permissions

### Administrator
- Full system access
- Manage all inventory
- User management capabilities
- Delete permissions
- System configuration

### Sales
- View inventory
- Add new tires
- Edit tire details
- Update stock levels
- Check prices

### Accounting
- View inventory
- Access pricing data
- View supplier information
- Read-only access
- Financial reports access

## API Endpoints

- `GET /` - Landing page
- `GET /login` - Login page
- `POST /login` - Process login
- `GET /logout` - Logout user
- `GET /dashboard` - Dashboard (requires authentication)
- `GET /inventory` - Inventory listing (requires authentication)
- `GET /tire/add` - Add tire form (requires admin/sales role)
- `POST /tire/add` - Process add tire (requires admin/sales role)
- `GET /tire/<id>/edit` - Edit tire form (requires admin/sales role)
- `POST /tire/<id>/edit` - Process edit tire (requires admin/sales role)
- `POST /tire/<id>/delete` - Delete tire (requires admin role)
- `GET /api/health` - Health check endpoint

## Development

### Database Models

**User Model:**
- Username, email, password (hashed)
- Role (admin, sales, accounting)
- Active status

**Tire Model:**
- Brand, model, size, type
- Wholesale and retail pricing
- Supplier information
- Inventory levels
- Technical specifications
- Warranty information

### Adding New Features

The application follows Flask best practices:
- Use `@login_required` decorator for protected routes
- Use `@role_required('role1', 'role2')` for role-based access
- Add templates in `templates/` directory
- Add static files in `static/` directory
- Extend `base.html` for consistent layout

## Configuration

Environment variables can be set in a `.env` file:

```
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_APP=app.py
FLASK_DEBUG=true
```

## Technologies Used

- **Backend:** Flask 3.0.0
- **Database:** SQLAlchemy with SQLite
- **Authentication:** Flask-Login
- **Frontend:** HTML5, CSS3, Jinja2 templates
- **Icons:** Font Awesome 6.4.0

## Security Features

- Password hashing with Werkzeug
- Session-based authentication
- Role-based access control
- CSRF protection (built into Flask)
- Secure password storage

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues or questions, please open an issue on GitHub.
