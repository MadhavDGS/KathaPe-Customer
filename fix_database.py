#!/usr/bin/env python3
"""
Script to add missing columns to the database
"""
import sys
import os
sys.path.append(os.getcwd())

from common_utils import execute_query

def add_missing_columns():
    try:
        # Add missing columns
        queries = [
            "ALTER TABLE transactions ADD COLUMN IF NOT EXISTS receipt_image_url TEXT;",
            "ALTER TABLE transactions ADD COLUMN IF NOT EXISTS media_url TEXT;",
            "CREATE INDEX IF NOT EXISTS idx_transactions_receipt_image ON transactions(receipt_image_url) WHERE receipt_image_url IS NOT NULL;"
        ]
        
        for query in queries:
            print(f"Executing: {query}")
            result = execute_query(query)
            print(f"Result: {result}")
            
        print("✅ Successfully added missing columns!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    add_missing_columns()
