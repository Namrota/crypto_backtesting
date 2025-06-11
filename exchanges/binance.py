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
        print(symbols)
        return symbols
