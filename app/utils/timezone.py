from datetime import datetime
import pytz

def convert_to_eat(utc_timestamp: str) -> str:
    """
    Convert ISO timestamp string (UTC) to East Africa Time (EAT).
    """
    utc = pytz.utc
    eat = pytz.timezone("Africa/Nairobi")

    if not utc_timestamp:
        return None

    # Parse timestamp string and ensure it's timezone-aware
    dt_utc = datetime.fromisoformat(utc_timestamp.replace("Z", "+00:00"))
    dt_eat = dt_utc.astimezone(eat)
    return dt_eat.strftime("%Y-%m-%d %H:%M:%S")  # or return dt_eat.isoformat()
