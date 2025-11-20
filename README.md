# Tires - Python Web Application

A modern Python web application built with Flask framework.

## Features

- Flask web framework for routing and request handling
- RESTful API endpoints
- HTML template rendering with Jinja2
- Static file serving (CSS, JavaScript)
- Health check endpoint for monitoring
- Clean project structure following best practices

## Project Structure

```
.
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── templates/              # HTML templates
│   ├── index.html         # Home page
│   └── about.html         # About page
├── static/                 # Static files
│   ├── css/
│   │   └── style.css      # Stylesheets
│   └── js/                # JavaScript files
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

## API Endpoints

- `GET /` - Home page
- `GET /about` - About page
- `GET /api/health` - Health check endpoint (returns JSON)

## Development

### Adding New Routes

Edit `app.py` to add new routes:

```python
@app.route('/new-route')
def new_route():
    return render_template('new_template.html')
```

### Creating New Templates

Add HTML templates in the `templates/` directory and reference them in your routes.

### Adding Static Files

Place CSS, JavaScript, and image files in the appropriate subdirectories under `static/`.

## Configuration

The application can be configured by setting environment variables or modifying `app.py`.

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
