from datetime import datetime
import pytz

def format_datetime(dt, timezone='America/Chicago'):
    """
    Convert UTC datetime to specified timezone and format it as a readable string.
    Default timezone is Central Time (America/Chicago).
    """
    if dt.tzinfo is None:
        # Assume the datetime is in UTC if no timezone is specified
        dt = pytz.UTC.localize(dt)
    
    # Convert to specified timezone
    local_tz = pytz.timezone(timezone)
    local_dt = dt.astimezone(local_tz)
    
    # Format the datetime
    return local_dt.strftime('%B %d, %Y at %I:%M %p %Z') 