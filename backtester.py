from database import Hdf5Client
from utils.time_convertor import *

import strategies.obv
import strategies.ichimoku
import strategies.support_resistance

def run(exchange:str, symbol:str, strategy:str, tf:str, from_time:int, to_time:int):
    """
    Run the backtesting process for the specified exchange and symbol.

    Args:
        exchange (str): The exchange to use (e.g., 'binance', 'coinbase').
        symbol (str): The trading symbol to backtest.
        strategy (str): The trading strategy to apply (e.g., 'obv').
        tf (str): The time frame for the backtest (e.g., '1m', '5m').
        from_time (int): The start time for the backtest in milliseconds.
        to_time (int): The end time for the backtest in milliseconds.
    """
    
    if strategy == "obv":
        h5_db = Hdf5Client(exchange)
        data= h5_db.get_data(symbol, from_time=from_time, to_time=to_time)
        # Resample the data to the specified timeframe
        data= resample_timeframe(data, tf)
   

        print(strategies.obv.backtest(data, 9))
    
    elif strategy== "ichimoku":
        h5_db = Hdf5Client(exchange)
        data= h5_db.get_data(symbol, from_time=from_time, to_time=to_time)
        # Resample the data to the specified timeframe
        data= resample_timeframe(data, tf)
        #strategies.ichimoku.backtest(data, 9, 26)
        print(strategies.ichimoku.backtest(data, tenkan_period= 9, kijun_period= 26))
    

    elif strategy== "sup_res":
        h5_db = Hdf5Client(exchange)
        data= h5_db.get_data(symbol, from_time=from_time, to_time=to_time)
        # Resample the data to the specified timeframe
        data= resample_timeframe(data, tf)
        print(strategies.support_resistance.backtest(data, min_points= 3, min_diff_points= 9, rounding_nb= 400, take_profit= 3, stop_loss= 3))