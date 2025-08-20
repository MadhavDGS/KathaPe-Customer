#!/usr/bin/env python3
"""
Test URL generation for debugging 404 errors
"""
import os
from dotenv import load_dotenv
load_dotenv()

try:
    from app import customer_app
    
    with customer_app.test_client() as client:
        with customer_app.app_context():
            from flask import url_for
            
            print("🔍 Testing URL generation...")
            
            # Test business view URL
            test_business_id = "test-business-123"
            try:
                business_url = url_for('business_view', business_id=test_business_id)
                print(f"✅ Business view URL: {business_url}")
            except Exception as e:
                print(f"❌ Business view URL error: {e}")
            
            # Test transaction URLs
            try:
                credit_url = url_for('customer_transaction', transaction_type='credit', business_id=test_business_id)
                print(f"✅ Credit transaction URL: {credit_url}")
            except Exception as e:
                print(f"❌ Credit transaction URL error: {e}")
                
            try:
                payment_url = url_for('customer_transaction', transaction_type='payment', business_id=test_business_id)
                print(f"✅ Payment transaction URL: {payment_url}")
            except Exception as e:
                print(f"❌ Payment transaction URL error: {e}")
            
            # List all routes
            print("\n📋 All available routes:")
            for rule in customer_app.url_map.iter_rules():
                print(f"   {rule.endpoint}: {rule.rule}")
                
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
