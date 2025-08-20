#!/usr/bin/env python3
"""
Debug registration issues with real Appwrite credentials
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🔍 Testing Appwrite connection and registration...")
print(f"Endpoint: {os.getenv('APPWRITE_ENDPOINT')}")
print(f"Project ID: {os.getenv('APPWRITE_PROJECT_ID')}")
print(f"Database ID: {os.getenv('APPWRITE_DATABASE_ID')}")

try:
    from appwrite_utils import appwrite_db_instance, register_user, USERS_COLLECTION, CUSTOMERS_COLLECTION
    print("✓ Successfully imported appwrite_utils")
    
    # Test database connection
    print(f"\n📊 Testing database connection...")
    print(f"Users Collection: {USERS_COLLECTION}")
    print(f"Customers Collection: {CUSTOMERS_COLLECTION}")
    
    # Try to list users (to test connection)
    print(f"\n🔍 Testing collection access...")
    users = appwrite_db_instance.list_documents(USERS_COLLECTION)
    print(f"✓ Users collection accessible. Found {len(users)} users.")
    
    customers = appwrite_db_instance.list_documents(CUSTOMERS_COLLECTION)
    print(f"✓ Customers collection accessible. Found {len(customers)} customers.")
    
    # Test registration
    print(f"\n🧪 Testing registration...")
    test_phone = "9999999999"
    
    # Check if test user already exists
    from appwrite.query import Query
    existing = appwrite_db_instance.list_documents(
        USERS_COLLECTION,
        [Query.equal("phone_number", test_phone)]
    )
    
    if existing:
        print(f"⚠️  Test user {test_phone} already exists. Using different number...")
        import random
        test_phone = f"999999{random.randint(1000, 9999)}"
    
    result = register_user("Test User", test_phone, "testpass123")
    print(f"Registration result: {result}")
    
    if 'error' in result:
        print(f"❌ Registration failed: {result['error']}")
    else:
        print(f"✅ Registration successful!")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
