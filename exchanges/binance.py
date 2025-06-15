from typing import *
import requests
import logging


# Set up logging
logger= logging.getLogger()

class BinanceClient:
    #differentiate between futures and spot, by default Futures will be False
    def __init__(self, futures= False):
        self.futures= futures

        if self.futures:
            self._base_url= "https://fapi.binance.com"
        else:
            self._base_url= "https://api.binance.com"

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
        Retrieves and prints exchange symbol information from Binance.
        Depending on whether the instance is set for futures or spot trading,
        this method constructs the appropriate endpoint and fetches exchange
        information using the internal `_make_requests` method. The retrieved
        data, which contains details about available trading symbols, is then
        printed to the console.
        Returns:
            None
        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Exchange-Information
        """

        params= dict()
        endpoint= "/fapi/v1/exchangeInfo" if self.futures else "/api/v3/exchangeInfo"
        data= self._make_requests(endpoint, params)

        symbols= [x["symbol"] for x in data["symbols"]]
        #print(symbols)
        return symbols

    def get_historical_data(self, symbol: str, start_time: Optional[int]= None, end_time: Optional[int]= None):
            """
            Fetches historical candlestick (kline) data for a given symbol from Binance, supporting both spot and futures markets.
            Args:
                symbol (str): The trading pair symbol (e.g., 'BTCUSDT').
                start_time (Optional[int], optional): The start time in milliseconds since epoch. Defaults to None.
                end_time (Optional[int], optional): The end time in milliseconds since epoch. Defaults to None.
                interval (str, optional): The interval for the candlestick data (e.g., '1m', '5m', '1h'). Defaults
                to '1m'.
                limit (int, optional): The maximum number of candlesticks to retrieve. Defaults to 500, max: 1500
            Returns:
                list: A list of candlestick data, where each entry contains:
                    [
                        open_time,      # int: Kline open time (ms)
                        open,           # str: Open price
                        high,           # str: High price
                        low,            # str: Low price
                        close,          # str: Close price
                        volume,         # str: Volume
                        close_time,     # int: Kline close time (ms)
                        quote_asset_volume, # str: Quote asset volume
                        number_of_trades,   # int: Number of trades
                        taker_buy_base_asset_volume,  # str: Taker buy base asset volume
                        taker_buy_quote_asset_volume, # str: Taker buy quote asset volume
                        ignore           # str: Ignore field
                    ]
            Raises:
                ValueError: If the symbol is invalid or required parameters are missing.
                requests.HTTPError: If the Binance API request fails.
            References:
                - Binance Spot API: https://binance-docs.github.io/apidocs/spot/en/#kline-candlestick-data
                - Binance Futures API: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data
            """

            params= dict()

            params["symbol"]= symbol
            params["interval"]= "1m"
            params["limit"]= 1500

            if start_time is not None:
                params["startTime"]= start_time
            if end_time is not None:
                params["endTime"]= end_time
    
            endpoint= "/fapi/v1/klines" if self.futures else "/api/v3/klines"
            raw_candles= self._make_requests(endpoint, params)
            candles=[]
            if raw_candles is None:
                raise ValueError(f"Failed to fetch historical data for {symbol}")
            for c in raw_candles:
                candles.append({
                    "open_time": c[0],
                    "open": float(c[1]),
                    "high": float(c[2]),
                    "low": float(c[3]),
                    "close": float(c[4]),
                    "volume": float(c[5])
                })
            return candles