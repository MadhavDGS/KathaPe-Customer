#!/usr/bin/env python3
"""
Test basic Appwrite connection
"""
import os
from dotenv import load_dotenv
load_dotenv()

from appwrite.client import Client
from appwrite.services.databases import Databases

print("🔗 Testing basic Appwrite connection...")

client = Client()
client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
client.set_key(os.getenv('APPWRITE_API_KEY'))

databases = Databases(client)

try:
    # List all databases
    print("📊 Listing all databases...")
    all_databases = databases.list()
    print(f"Found {len(all_databases['databases'])} databases:")
    
    for db in all_databases['databases']:
        print(f"  - {db['name']} (ID: {db['$id']})")
    
    # Test with the configured database ID
    db_id = os.getenv('APPWRITE_DATABASE_ID')
    print(f"\n🎯 Testing configured database ID: {db_id}")
    
    try:
        collections = databases.list_collections(database_id=db_id)
        print(f"✅ Database found! Collections: {len(collections['collections'])}")
        
        for collection in collections['collections']:
            print(f"  - {collection['name']} (ID: {collection['$id']})")
            
    except Exception as e:
        print(f"❌ Database {db_id} not found: {e}")
        
        if all_databases['databases']:
            print(f"💡 Try using one of these database IDs instead:")
            for db in all_databases['databases']:
                print(f"   APPWRITE_DATABASE_ID={db['$id']}")
        
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("\n🔍 Check these settings:")
    print(f"  - Endpoint: {os.getenv('APPWRITE_ENDPOINT')}")
    print(f"  - Project ID: {os.getenv('APPWRITE_PROJECT_ID')}")
    print(f"  - API Key: {os.getenv('APPWRITE_API_KEY')[:20]}...")
