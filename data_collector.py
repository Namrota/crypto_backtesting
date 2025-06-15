from typing import *
from utils.time_convertor import *
import time
import logging

from database import Hdf5Client
from exchanges.binance import BinanceClient
from exchanges.coinbase import CoinbaseClient


logger = logging.getLogger()

def collect_all(client: Union[BinanceClient, CoinbaseClient], exchange: str, symbol: str) -> None:
    # This function collects historical data for a given trading symbol from the specified exchange.
    h5_db= Hdf5Client(exchange)
    h5_db.create_dataset(symbol)  # Create a dataset for the symbol if it doesn't exist
    oldest_ts, most_recent_ts= h5_db.get_first_last_timestamp(symbol)
    print(oldest_ts, most_recent_ts)
    #Case 1: initial request to get the historical data

    if oldest_ts is None:
        data= client.get_historical_data(symbol, end_time= int(time.time() * 1000) - 60000) # 60 seconds before the current time
        if len(data)==0:
            logger.warning(f"No historical data found for {symbol} on {exchange}.")
            return
        else:
            #if exchange== "coinbase":
            #    data= list(reversed(data))  # Coinbase returns data in reverse order, so we reverse it to chronological order
            logger.info(f"Collected initial historical data of {len(data)} for {symbol} on {exchange} from {ms_to_datetime(data[0]['open_time'])} to {ms_to_datetime(data[-1]['open_time'])}.")

        oldest_ts= data[0]['open_time']
        most_recent_ts= data[-1]['open_time']

        h5_db.write_data(symbol, [(d['open_time'], d['low'], d['high'], d['open'], d['close'], d['volume']) for d in data])
    
    #Case 2: data already collected, we now need to collect new data
    '''
    This part of the code collects new data based on the most recent timestamp.
    It checks if the most recent timestamp is older than the current time minus 60 seconds.
    If it is, it fetches new data until the most recent timestamp is updated to the latest available data.
    If no new data is found, it pauses for 4 seconds before retrying.
    If new data is found, it logs the number of new data points collected and the time range of the data.
    The loop continues until no more new data is available or the most recent timestamp is updated.
    It also includes a sleep of 1.1 seconds to avoid hitting the rate limit of the exchange API.
    '''

    while True:
        data= client.get_historical_data(symbol, start_time= int(most_recent_ts + 60000)) # 60 seconds before the current time

        if data is None or len(data) == 0:
            time.sleep(4) #Pause for 4 seconds before retrying
            continue

        # collected data until 2 minutes ago; to avoid infinite loop
        if(len(data) < 2):
            break

        data= data[:-1] # Remove the last element because the current candlstick might not be finished yet
        #if exchange== "coinbase":
        #    data= list(reversed(data))
        if data[-1]['open_time'] > most_recent_ts:
            most_recent_ts= data[-1]['open_time']
        logger.info(f"Collected new data of {len(data)} for {symbol} on {exchange} from {ms_to_datetime(data[0]['open_time'])} to {ms_to_datetime(data[-1]['open_time'])}.")
        
        h5_db.write_data(symbol, [(d['open_time'], d['low'], d['high'], d['open'], d['close'], d['volume']) for d in data])
        time.sleep(1.1) # Pause for 1.1 seconds to avoid hitting the rate limit  

    #Case 3: older data
    '''
    This part of the code collects older data based on the oldest timestamp.
    It checks if the oldest timestamp is older than the current time minus 60 seconds.
    If it is, it fetches older data until the oldest timestamp is updated to the earliest available data.
    If no older data is found, it pauses for 4 seconds before retrying.
    If older data is found, it logs the number of older data points collected and the time range of the data.
    The loop continues until no more older data is available or the oldest timestamp is updated.
    It also includes a sleep of 1.1 seconds to avoid hitting the rate limit of the exchange API.
    '''
    while True:
        data= client.get_historical_data(symbol, end_time= int(oldest_ts - 60000)) # 60 seconds before the oldest timestamp

        if data is None or len(data) == 0:
            time.sleep(4) #Pause for 4 seconds before retrying
            continue

        if(len(data) == 0):
            logger.info(f"No more historical data found before {ms_to_datetime(oldest_ts)} for {symbol} on {exchange}.")
            break
        
        #if exchange== "coinbase":
        #    data= list(reversed(data))
        
        if data[0]['open_time'] < oldest_ts:
            oldest_ts= data[0]['open_time']
        
        logger.info(f"Collected older data of {len(data)} for {symbol} on {exchange} from {ms_to_datetime(data[0]['open_time'])} to {ms_to_datetime(data[-1]['open_time'])}.")
        
        h5_db.write_data(symbol, [(d['open_time'], d['low'], d['high'], d['open'], d['close'], d['volume']) for d in data])
        time.sleep(1.1) # Pause for 1.1 seconds to avoid hitting the rate limit  
