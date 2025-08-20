#!/usr/bin/env python3
"""
Test the credit/payment button functionality
"""
import os
from dotenv import load_dotenv
load_dotenv()

try:
    from app import customer_app
    
    with customer_app.test_client() as client:
        print("🔍 Testing credit/payment button URLs...")
        
        # Register and login
        print("📝 Registering test user...")
        register_data = {
            'name': 'Test User Button',
            'phone': '7777777777',
            'password': 'testpass123'
        }
        
        response = client.post('/register', data=register_data, follow_redirects=True)
        
        if response.status_code == 200:
            print("✅ Registration successful")
            
            # Test a business view URL with a real business ID
            print("🏢 Testing business view access...")
            
            # Get a business ID from the database
            from appwrite_utils import appwrite_db_instance, BUSINESSES_COLLECTION
            businesses = appwrite_db_instance.list_documents(BUSINESSES_COLLECTION)
            
            if businesses:
                business_id = businesses[0]['$id']
                print(f"📋 Using business ID: {business_id}")
                
                # Access business view
                response = client.get(f'/business/{business_id}')
                print(f"📊 Business view response: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ Business view accessible")
                    
                    # Test credit transaction URL
                    response = client.get(f'/transaction/credit/{business_id}')
                    print(f"💳 Credit transaction response: {response.status_code}")
                    
                    # Test payment transaction URL
                    response = client.get(f'/transaction/payment/{business_id}')
                    print(f"💰 Payment transaction response: {response.status_code}")
                    
                    if response.status_code == 200:
                        print("✅ Transaction pages accessible - 404 issue should be fixed!")
                    else:
                        print(f"❌ Transaction pages still showing {response.status_code}")
                else:
                    print(f"❌ Business view returned {response.status_code}")
            else:
                print("⚠️  No businesses found in database")
        else:
            print(f"❌ Registration failed: {response.status_code}")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
