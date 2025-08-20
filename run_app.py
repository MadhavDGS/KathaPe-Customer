#!/usr/bin/env python3
"""
Simple Flask app runner with detailed logging
"""
import os
from dotenv import load_dotenv
load_dotenv()

if __name__ == '__main__':
    from app import customer_app
    print("🚀 Starting KathaPe Customer App...")
    print("📱 Registration is now working!")
    print("🌐 App will be available at: http://localhost:5002")
    print("📝 Test registration at: http://localhost:5002/register")
    print("\n🔍 Console will show detailed logs for debugging")
    print("🌐 Open your browser's Developer Tools (F12) to see any frontend errors")
    print("📋 Browser Console Errors (if any) will appear in the Network tab")
    print("\n" + "="*60)
    
    # Enable more detailed Flask logging
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    customer_app.run(debug=True, host='0.0.0.0', port=5002)
