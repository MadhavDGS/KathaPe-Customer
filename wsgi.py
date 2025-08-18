#!/usr/bin/env python3
"""
WSGI entry point for KathaPe Customer Application
This file is used by Waitress to serve the Flask application
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import customer_app

# This is what Waitress will use
application = customer_app

if __name__ == "__main__":
    # For development/testing - use Waitress directly
    from waitress import serve
    print("Starting KathaPe Customer App with Waitress...")
    print("Server will be available at: http://localhost:8080")
    serve(application, host='0.0.0.0', port=8080, threads=4)
