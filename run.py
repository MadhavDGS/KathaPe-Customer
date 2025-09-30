#!/usr/bin/env python3
"""
Run script for Customer Flask Application
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path to access shared modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(parent_dir, 'shared'))

from app import customer_app

if __name__ == '__main__':
    print("Starting KhataPe Customer Application...")
    print("Customer app will be available at: http://localhost:5002")
    print("Press Ctrl+C to stop the application")
    
    # Run the customer app
    port = int(os.environ.get('CUSTOMER_PORT', 5002))
    customer_app.run(
        debug=True,
        host='0.0.0.0',
        port=port,
        threaded=True
    )
