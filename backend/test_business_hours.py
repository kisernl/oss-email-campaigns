#!/usr/bin/env python3
"""
Test script to verify business hours integration with Cloud Tasks.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from app.utils.business_hours import (
    is_within_business_hours, 
    calculate_next_business_hour,
    get_business_hours_delay
)

def test_business_hours():
    """Test business hours calculations."""
    print("🧪 Testing Business Hours Logic")
    print("=" * 50)
    
    # Test current time
    now = datetime.utcnow()
    print(f"Current UTC time: {now.strftime('%Y-%m-%d %H:%M:%S %A')}")
    
    # Test business hours in different timezones
    timezones = ["UTC", "US/Pacific", "US/Eastern", "Europe/London"]
    
    for tz in timezones:
        print(f"\n📍 Testing timezone: {tz}")
        
        # Check if currently within business hours
        within_hours = is_within_business_hours(
            campaign_timezone=tz,
            business_hours_start=9,
            business_hours_end=17,
            business_days_only=True,
            current_time=now
        )
        
        print(f"   ✅ Within business hours: {within_hours}")
        
        # Calculate next business hour
        next_business = calculate_next_business_hour(
            campaign_timezone=tz,
            business_hours_start=9,
            business_hours_end=17,
            business_days_only=True,
            current_time=now
        )
        
        print(f"   ⏰ Next business hour: {next_business.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        
        # Calculate delay
        should_delay, delay_seconds = get_business_hours_delay(
            campaign_timezone=tz,
            business_hours_start=9,
            business_hours_end=17,
            business_days_only=True,
            current_time=now
        )
        
        delay_hours = delay_seconds // 3600
        delay_minutes = (delay_seconds % 3600) // 60
        
        print(f"   ⏳ Should delay: {should_delay}")
        if should_delay:
            print(f"   ⏳ Delay time: {delay_hours}h {delay_minutes}m")

def test_campaign_scheduling():
    """Test campaign scheduling logic with business hours."""
    print("\n\n🎯 Testing Campaign Scheduling")
    print("=" * 50)
    
    # Simulate scheduling 5 emails with business hours
    email_count = 5
    delay_min = 4
    delay_max = 7
    
    # Business hours settings
    timezone = "US/Pacific"
    business_hours_start = 9
    business_hours_end = 17
    business_days_only = True
    
    print(f"📧 Scheduling {email_count} emails:")
    print(f"   ⏱️  Delay range: {delay_min}-{delay_max} minutes")
    print(f"   🏢 Business hours: {business_hours_start}:00-{business_hours_end}:00 ({timezone})")
    print(f"   📅 Business days only: {business_days_only}")
    
    current_time = datetime.utcnow()
    
    for i in range(email_count):
        if i == 0:
            # First email
            if not is_within_business_hours(
                timezone, business_hours_start, business_hours_end, business_days_only, current_time
            ):
                current_time = calculate_next_business_hour(
                    timezone, business_hours_start, business_hours_end, business_days_only, current_time
                )
                print(f"   📧 Email {i+1}: {current_time.strftime('%Y-%m-%d %H:%M:%S')} UTC (moved to business hours)")
            else:
                print(f"   📧 Email {i+1}: {current_time.strftime('%Y-%m-%d %H:%M:%S')} UTC (immediate)")
        else:
            # Add delay
            import random
            delay = random.randint(delay_min, delay_max)
            next_time = current_time + timedelta(minutes=delay)
            
            # Check business hours
            if not is_within_business_hours(
                timezone, business_hours_start, business_hours_end, business_days_only, next_time
            ):
                next_time = calculate_next_business_hour(
                    timezone, business_hours_start, business_hours_end, business_days_only, next_time
                )
                print(f"   📧 Email {i+1}: {next_time.strftime('%Y-%m-%d %H:%M:%S')} UTC (moved to business hours)")
            else:
                print(f"   📧 Email {i+1}: {next_time.strftime('%Y-%m-%d %H:%M:%S')} UTC (normal delay)")
            
            current_time = next_time

if __name__ == "__main__":
    test_business_hours()
    test_campaign_scheduling()