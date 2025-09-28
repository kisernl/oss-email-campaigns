"""
Business hours utility functions for email campaign scheduling.

Provides functions to check if current time is within business hours
and calculate delays to respect business hour restrictions.
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
import pytz


def is_within_business_hours(
    campaign_timezone: str = "UTC",
    business_hours_start: int = 7,
    business_hours_end: int = 17,
    business_days_only: bool = True,
    current_time: Optional[datetime] = None
) -> bool:
    """
    Check if current time is within business hours.
    
    Args:
        campaign_timezone: Timezone string (e.g., "UTC", "US/Pacific")
        business_hours_start: Start hour in 24-hour format (0-23)
        business_hours_end: End hour in 24-hour format (1-24)
        business_days_only: If True, only Monday-Friday are considered business days
        current_time: Optional datetime to check (defaults to now)
    
    Returns:
        True if within business hours, False otherwise
    """
    if current_time is None:
        current_time = datetime.utcnow()
    
    try:
        # Convert to campaign timezone
        tz = pytz.timezone(campaign_timezone)
        local_time = current_time.replace(tzinfo=pytz.UTC).astimezone(tz)
    except pytz.exceptions.UnknownTimeZoneError:
        # Fallback to UTC if timezone is invalid
        local_time = current_time.replace(tzinfo=pytz.UTC)
    
    # Check if it's a business day (Monday=0, Sunday=6)
    if business_days_only:
        weekday = local_time.weekday()
        if weekday >= 5:  # Saturday (5) or Sunday (6)
            return False
    
    # Check if within business hours
    current_hour = local_time.hour
    return business_hours_start <= current_hour < business_hours_end


def calculate_next_business_hour(
    campaign_timezone: str = "UTC",
    business_hours_start: int = 7,
    business_hours_end: int = 17,
    business_days_only: bool = True,
    current_time: Optional[datetime] = None
) -> datetime:
    """
    Calculate the next time that falls within business hours.
    
    Args:
        campaign_timezone: Timezone string
        business_hours_start: Start hour in 24-hour format
        business_hours_end: End hour in 24-hour format
        business_days_only: If True, only Monday-Friday are considered business days
        current_time: Optional datetime to start from (defaults to now)
    
    Returns:
        UTC datetime of next business hour
    """
    if current_time is None:
        current_time = datetime.utcnow()
    
    try:
        tz = pytz.timezone(campaign_timezone)
        local_time = current_time.replace(tzinfo=pytz.UTC).astimezone(tz)
    except pytz.exceptions.UnknownTimeZoneError:
        tz = pytz.UTC
        local_time = current_time.replace(tzinfo=pytz.UTC)
    
    # Start checking from the next minute to avoid immediate retry
    check_time = local_time + timedelta(minutes=1)
    
    # Look ahead up to 7 days to find next business hour
    for _ in range(7 * 24 * 60):  # 7 days worth of minutes
        # Check if it's a business day
        if business_days_only:
            weekday = check_time.weekday()
            if weekday >= 5:  # Weekend
                # Skip to Monday morning
                days_until_monday = (7 - weekday) % 7
                if days_until_monday == 0:  # Already Monday
                    days_until_monday = 1
                check_time = check_time.replace(
                    hour=business_hours_start, 
                    minute=0, 
                    second=0, 
                    microsecond=0
                ) + timedelta(days=days_until_monday)
                continue
        
        # Check if within business hours
        current_hour = check_time.hour
        if business_hours_start <= current_hour < business_hours_end:
            # Convert back to UTC
            utc_time = check_time.astimezone(pytz.UTC).replace(tzinfo=None)
            return utc_time
        
        # If before business hours, jump to start of business hours
        if current_hour < business_hours_start:
            check_time = check_time.replace(
                hour=business_hours_start,
                minute=0,
                second=0,
                microsecond=0
            )
        else:
            # After business hours, jump to next day at start of business hours
            check_time = (check_time + timedelta(days=1)).replace(
                hour=business_hours_start,
                minute=0,
                second=0,
                microsecond=0
            )
    
    # Fallback: return current time + 1 hour if no business hour found
    return current_time + timedelta(hours=1)


def get_business_hours_delay(
    campaign_timezone: str = "UTC",
    business_hours_start: int = 7,
    business_hours_end: int = 17,
    business_days_only: bool = True,
    current_time: Optional[datetime] = None
) -> Tuple[bool, int]:
    """
    Calculate delay needed to wait for business hours.
    
    Args:
        campaign_timezone: Timezone string
        business_hours_start: Start hour in 24-hour format
        business_hours_end: End hour in 24-hour format  
        business_days_only: If True, only Monday-Friday are considered business days
        current_time: Optional datetime to check from (defaults to now)
    
    Returns:
        Tuple of (should_delay, delay_seconds)
        - should_delay: True if we need to wait for business hours
        - delay_seconds: Number of seconds to wait
    """
    if current_time is None:
        current_time = datetime.utcnow()
    
    # Check if already within business hours
    if is_within_business_hours(
        campaign_timezone, business_hours_start, business_hours_end, 
        business_days_only, current_time
    ):
        return False, 0
    
    # Calculate next business hour
    next_business_time = calculate_next_business_hour(
        campaign_timezone, business_hours_start, business_hours_end,
        business_days_only, current_time
    )
    
    # Calculate delay in seconds
    delay_seconds = int((next_business_time - current_time).total_seconds())
    
    return True, max(delay_seconds, 0)


def format_business_hours_info(
    business_hours_start: int,
    business_hours_end: int,
    business_days_only: bool,
    timezone: str
) -> str:
    """
    Format business hours information for display.
    
    Args:
        business_hours_start: Start hour in 24-hour format
        business_hours_end: End hour in 24-hour format
        business_days_only: If True, only Monday-Friday
        timezone: Timezone string
    
    Returns:
        Formatted string describing business hours
    """
    # Convert to 12-hour format for display
    start_12h = f"{business_hours_start % 12 or 12}{'AM' if business_hours_start < 12 else 'PM'}"
    end_12h = f"{business_hours_end % 12 or 12}{'AM' if business_hours_end < 12 else 'PM'}"
    
    days = "Monday-Friday" if business_days_only else "All days"
    
    return f"{start_12h}-{end_12h}, {days} ({timezone})"