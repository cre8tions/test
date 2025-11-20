"""
Main Flask application module for the tires web application.
"""
from flask import Flask, render_template, jsonify

app = Flask(__name__)


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
    app.run(debug=True, host='0.0.0.0', port=5000)
