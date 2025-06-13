from typing import *
import requests
import logging

from datetime import datetime, timedelta

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
           

            params= dict()

            params["granularity"]= "60" # 60 seconds granularity
            # maximum number of  requests is 300 candles per request
            params["limit"]= 300
            # if the start and end fields are not provided, both fields are ignored.
            delta= timedelta(seconds= 60) # 60 seconds
            if start_time is not None:
                start_time= end_time - (300 * delta)
                params["start"]= start_time.isoformat()
            if end_time is not None:
                end_time= datetime.now()
                params["end"]= end_time.isoformat()
    
            endpoint= f"/products/{symbol}/candles" # Coinbase API endpoint for historical candles
            raw_candles= self._make_requests(endpoint, params)
            candles=[]
            if raw_candles is None:
                raise ValueError(f"Failed to fetch historical data for {symbol}")
            for c in raw_candles:
                candles.append({
                    "open_time": c[0] * 1000,       # bucket start time in milliseconds since epoch (Unix time in ms)
                    "low": c[1],      # lowesr price during the bucket interval
                    "high": c[2],     # highest price during the bucket interval
                    "open": c[3],     # opening price at the start of the bucket interval
                    "close": c[4],    # closing price at the end of the bucket interval
                    "volume": c[5]    # volume of the asset traded during the bucket interval
                })
            return candles