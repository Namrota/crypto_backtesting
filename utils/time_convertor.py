import datetime
import pandas as pd

TF_EQUIV={"1m":"1Min", "5m":"5Min", "15m":"15Min", "30m":"30Min", 
          "1h":"1h", "4h":"4h", "12h":"12h", 
          "1d":"1D", "1w":"1W"}

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

def resample_timeframe(data: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    """
    Resamples a DataFrame to a specified timeframe.
    
    Args:
        data (pd.DataFrame): The DataFrame to resample.
        timeframe (str): The new timeframe (e.g., '1T' for 1 minute).
        
    Returns:
        pd.DataFrame: The resampled DataFrame.
        Resamples the data with appropriate aggregation methods for each OHLCV column:
        open: Takes first value in the period
        high: Takes maximum value
        low: Takes minimum value
        close: Takes last value
        volume: Sums all values
    """
    # aggregate the data to the specified timeframe

    return data.resample(TF_EQUIV[timeframe]).agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    })