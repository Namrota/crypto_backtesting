from typing import *
import requests
import logging
import pytz
from datetime import datetime, timedelta, timezone
from utils.time_convertor import *

# Set up logging
logger= logging.getLogger()
"""Coinbase offers only spot trading, so futures will always be False.
   This class is designed to interact with the Coinbase API for fetching historical data."""
class CoinbaseClient:
    #differentiate between futures and spot, by default Futures will be False
    def __init__(self):
        self.futures= False
        # Coinbase API base URL
        self._base_url= "https://api.exchange.coinbase.com"
        # Fetch and store available trading symbols
        self.symbols= self._get_symbols()
    
    def _make_requests(self, endpoint: str, query_parameters: Dict):
        """
        Sends a GET request to the specified Binance API endpoint with the provided query parameters.

        Args:
            endpoint (str): The API endpoint to send the request to.
            query_parameters (Dict): A dictionary of query parameters to include in the request.

        Returns:
            dict or None: The JSON response from the API if the request is successful, otherwise None.

        Raises:
            Logs errors if the request fails or if the response status code is not 200.

        # Summary:
        # - Constructs the full URL using the base URL and the provided endpoint.
        # - Sends a GET request with the given query parameters.
        # - Handles exceptions during the request and logs errors.
        # - Returns the JSON response if successful, otherwise logs the error and returns None.
        """
        try:
            response= requests.get(self._base_url + endpoint, params= query_parameters)
        except Exception as e:
            logger.error(f"Error making request to Binance {endpoint}: {e}")
            return None
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Error fetching data from Binance {endpoint}: {response.status_code} - {response.text}")
            return None
        

    def _get_symbols(self)-> List[str]:
        """
        Fetches and returns a list of active trading symbols from the Coinbase exchange.
        This method queries the Coinbase API for all available trading products (symbols),
        filters out any products that are currently disabled for trading.

        Returns:
            List[str]: A list of active trading symbols with hyphens removed.

        API Reference:
        https://docs.cdp.coinbase.com/exchange/reference/exchangerestapi_getproducts

        """
        
        params= dict()
        endpoint= "/products"  # Coinbase API endpoint for products (symbols)
        data = self._make_requests(endpoint, params)
        #if trading is not disabled then return the list of all the products
        symbols = [product["id"] for product in data if not product["trading_disabled"]]
        #print(symbols)
        return symbols

    def get_historical_data(self, symbol: str, start_time: Optional[int]= None, end_time: Optional[int]= None):
        
        """
        Fetches historical candlestick (OHLCV) data for a given trading symbol from Coinbase.
        Parameters:
            symbol (str): The trading pair symbol (e.g., 'BTC-USD').
            start_time (Optional[int]): The start time for fetching data as a Unix timestamp (seconds). If not provided, defaults to the latest available data.
            end_time (Optional[int]): The end time for fetching data as a Unix timestamp (seconds). If not provided, defaults to the current time.
        Returns:
            List[dict]: A list of candlestick data, where each entry contains:
                - 'open_time': Start time of the candle in milliseconds since epoch.
                - 'low': Lowest price during the interval.
                - 'high': Highest price during the interval.
                - 'open': Opening price at the start of the interval.
                - 'close': Closing price at the end of the interval.
                - 'volume': Volume traded during the interval.
        Raises:
            ValueError: If historical data could not be fetched for the given symbol.
        Notes:
            - The data granularity is fixed at 60 seconds (1 minute).
            - A maximum of 300 candles can be fetched per request.
            - If start_time and end_time are not provided, the latest 300 candles are returned.
        """
        params= dict()
        params["granularity"]= "60" # 60 seconds granularity
        max_candles= 300 # maximum number of candles to fetch
        result= []

        if end_time is not None:
            end_time_dt = ms_to_datetime(end_time)
           
        else:
            end_time_dt = datetime.datetime.now(timezone.utc)
           

        if start_time is not None:
            start_time_dt= ms_to_datetime(start_time)
            # If start_time is provided, we use it directly
            if (end_time_dt - start_time_dt) > timedelta(minutes= max_candles):
                start_time_dt = end_time_dt - timedelta(minutes= max_candles)
            
        else:
            # If start_time is provided, we calculate it as 300 minutes before the end_time
            start_time_dt = end_time_dt - timedelta(minutes= max_candles)
        
        
        params["start"]= start_time_dt.isoformat()
        params["end"]= end_time_dt.isoformat()

        endpoint= f"/products/{symbol}/candles" # Coinbase API endpoint for historical candles
        raw_candles= self._make_requests(endpoint, params)
        candles=[]
        if raw_candles is None:
            raise ValueError(f"Failed to fetch historical data for {symbol}")
        for c in raw_candles:
            candles.append({
                "open_time": c[0] * 1000,       # bucket start time in milliseconds since epoch (Unix time in ms)
                "low": c[1],      # lowest price during the bucket interval
                "high": c[2],     # highest price during the bucket interval
                "open": c[3],     # opening price at the start of the bucket interval
                "close": c[4],    # closing price at the end of the bucket interval
                "volume": c[5]    # volume of the asset traded during the bucket interval
            })
        # Sort the candles by open_time to ensure ascending order
        return sorted(candles, key= lambda x: x["open_time"])