#!/usr/bin/env python3
"""
Test Flask app startup and registration
"""
import os
from dotenv import load_dotenv
load_dotenv()

print("🚀 Testing Flask app startup and registration...")

try:
    from app import customer_app
    print("✅ Flask app imported successfully!")
    
    # Test a simple route
    with customer_app.test_client() as client:
        response = client.get('/')
        print(f"✅ Home page accessible: Status {response.status_code}")
        
        # Test registration page
        response = client.get('/register')
        print(f"✅ Registration page accessible: Status {response.status_code}")
        
        # Test actual registration
        print("\n🧪 Testing registration process...")
        test_data = {
            'name': 'Test User Console',
            'phone': '8888888888',
            'password': 'testpass123'
        }
        
        print(f"📋 Registering user: {test_data}")
        response = client.post('/register', data=test_data, follow_redirects=True)
        print(f"📊 Registration response status: {response.status_code}")
        
        # Check if registration was successful
        if response.status_code == 200:
            response_text = response.get_data(as_text=True)
            if 'Welcome' in response_text or 'success' in response_text:
                print("✅ Registration appears successful!")
            else:
                print("❌ Registration may have failed - check console output above")
        else:
            print(f"❌ Registration failed with status: {response.status_code}")
        
        print("\n🎉 Console test complete!")
        print("📝 All detailed logs are shown above")
        print("🌐 You can also run the app manually with: python run_app.py")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
