"""
WSGI Configuration for Production Deployment

This file is used by WSGI servers like Gunicorn, uWSGI, or mod_wsgi
to serve the Flask application in production.

Usage with Gunicorn:
    gunicorn --bind 0.0.0.0:8000 wsgi:application

Usage with uWSGI:
    uwsgi --http :8000 --wsgi-file wsgi.py --callable application
"""

from app import app, db
import os

# Create database tables
with app.app_context():
    db.create_all()

application = app

if __name__ == "__main__":
    application.run()
