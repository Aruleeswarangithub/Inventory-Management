#!/usr/bin/env python3
"""
Flask Inventory Management System
Run script for development and production

Usage:
    python run.py                 # Development mode
    python run.py --prod          # Production mode  
    python run.py --host 0.0.0.0  # Accessible from network
"""

import os
import sys
import argparse
from app import app, db

def create_tables():
    """Create database tables if they don't exist"""
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

def main():
    parser = argparse.ArgumentParser(description='Run Flask Inventory Management System')
    parser.add_argument('--prod', action='store_true', help='Run in production mode')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--create-db', action='store_true', help='Create database tables')

    args = parser.parse_args()

    if args.create_db:
        create_tables()
        return

    # Set configuration
    if args.prod:
        app.config['DEBUG'] = False
        print("Running in PRODUCTION mode")
    else:
        app.config['DEBUG'] = True  
        print("Running in DEVELOPMENT mode")

    # Create tables on first run
    create_tables()

    # Run the application
    try:
        print(f"Starting Flask server at http://{args.host}:{args.port}")
        app.run(host=args.host, port=args.port, debug=not args.prod)
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
