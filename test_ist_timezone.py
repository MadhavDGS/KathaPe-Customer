#!/usr/bin/env python3
"""
Test script to verify IST timezone implementation
"""

from common_utils import get_ist_now, get_ist_isoformat, format_datetime, convert_to_ist
from datetime import datetime
import pytz

def test_ist_functions():
    print("=== IST Timezone Implementation Test ===\n")
    
    # Test current IST time
    ist_now = get_ist_now()
    print(f"1. Current IST time: {ist_now}")
    print(f"   Timezone: {ist_now.tzinfo}")
    
    # Test IST ISO format
    ist_iso = get_ist_isoformat()
    print(f"\n2. Current IST ISO format: {ist_iso}")
    
    # Test format_datetime with IST time
    formatted_time = format_datetime(ist_iso)
    print(f"\n3. Formatted IST time for display: {formatted_time}")
    
    # Test conversion from UTC to IST
    utc_time = datetime.now(pytz.UTC)
    print(f"\n4. Current UTC time: {utc_time}")
    
    ist_converted = convert_to_ist(utc_time)
    print(f"   Converted to IST: {ist_converted}")
    print(f"   Time difference: {ist_converted.hour - utc_time.hour} hours, {ist_converted.minute - utc_time.minute} minutes")
    
    # Test format_datetime with UTC string (simulating database storage)
    utc_string = utc_time.isoformat()
    print(f"\n5. UTC string from database: {utc_string}")
    formatted_from_utc = format_datetime(utc_string)
    print(f"   Displayed as IST: {formatted_from_utc}")
    
    # Test with naive datetime (no timezone info)
    naive_time = datetime.now()
    print(f"\n6. Naive datetime: {naive_time}")
    converted_naive = convert_to_ist(naive_time)
    print(f"   Converted to IST (assuming UTC): {converted_naive}")
    
    print("\n=== Test completed successfully! ===")

if __name__ == "__main__":
    test_ist_functions()
