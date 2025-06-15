import datetime

def ms_to_datetime(ms: int) -> datetime.datetime:
    """
    Converts milliseconds since epoch to a datetime object in UTC.
    
    Args:
        ms (int): Time in milliseconds since epoch.
        
    Returns:
        datetime.datetime: Corresponding datetime object in UTC.
    
    The code converts a timestamp in milliseconds into a timezone-aware datetime Python object,
    specically in UTC
    """
    return datetime.datetime.fromtimestamp(ms / 1000, tz=datetime.timezone.utc)

def floor_to_minute(dt: datetime.datetime, sec:int) -> datetime.datetime:
    """
    Floors a datetime object to the nearest minute.
    
    Args:
        dt (datetime.datetime): The datetime object to floor.
        
    Returns:
        datetime.datetime: The floored datetime object.
    """
    ts= int(dt.timestamp())
    floored_ts= (ts//sec)*sec
    return dt.fromtimestamp(floored_ts, tz=dt.tzinfo)