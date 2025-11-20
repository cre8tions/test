"""
Main Flask application module for the tires web application.
"""
import os
from flask import Flask, render_template, jsonify

app = Flask(__name__)
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'


@app.route('/')
def index():
    """Home page route."""
    return render_template('index.html')


@app.route('/api/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'tires'
    })


@app.route('/about')
def about():
    """About page route."""
    return render_template('about.html')


if __name__ == '__main__':
    # Only enable debug mode if explicitly set in environment
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
