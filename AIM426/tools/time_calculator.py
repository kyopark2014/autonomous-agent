from strands import tool
from datetime import datetime, timedelta

@tool
def calculate_time_difference(start_time: str, end_time: str) -> str:
    """Calculate the time difference between two times.
    
    Args:
        start_time: Start time in HH:MM format (24-hour)
        end_time: End time in HH:MM format (24-hour)
        
    Returns:
        str: Time difference calculation
    """
    try:
        start = datetime.strptime(start_time, "%H:%M")
        end = datetime.strptime(end_time, "%H:%M")
        
        # Handle case where end time is next day
        if end < start:
            end += timedelta(days=1)
        
        diff = end - start
        hours, remainder = divmod(diff.seconds, 3600)
        minutes = remainder // 60
        
        return f"Time difference: {hours}h {minutes}m"
    except ValueError:
        return "Error: Please use HH:MM format (e.g., '09:30', '14:45')"
