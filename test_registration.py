#!/usr/bin/env python3
"""
Test script to debug registration issues
"""
import os
import sys

# Set environment variables for testing
os.environ['APPWRITE_ENDPOINT'] = 'https://cloud.appwrite.io/v1'
os.environ['APPWRITE_PROJECT_ID'] = 'test_project'
os.environ['APPWRITE_API_KEY'] = 'test_key'
os.environ['APPWRITE_DATABASE_ID'] = 'test_db'

try:
    from appwrite_utils import register_user, appwrite_db_instance
    print("✓ Successfully imported appwrite_utils")
    print(f"✓ appwrite_db_instance: {appwrite_db_instance}")
    
    # Test basic functionality
    print("Testing register_user function...")
    result = register_user("Test User", "1234567890", "testpass")
    print(f"Result: {result}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
