import datetime

def format_date(timestamp):
    """Formats a timestamp into a readable date string."""
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def log_event(event_type, details):
    """Simple logging function."""
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {event_type}: {details}")