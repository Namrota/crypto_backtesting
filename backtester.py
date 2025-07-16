
from ctypes import *
from database import Hdf5Client
from utils.time_convertor import *

import strategies.obv
import strategies.ichimoku
import strategies.support_resistance
import strategies.sma_crossover
from utils.params import *


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

    params_des= STRAT_PARAMS[strategy]

    params= dict()
    for key, value in params_des.items():
        while True:
            try:
                # Prompt the user for input, using the default value if provided
                user_input = input(f"{value['name']} (default: {value['default']}): ")
                # If the user provides no input, use the default value
                if user_input == "":
                    params[key] = value["type"](value["default"])
                else:
                    params[key] = value["type"](user_input)
                break
            except ValueError:
                print(f"Invalid input for {value['name']}. Please enter a valid {value['type'].__name__} value.")
    
    if strategy == "obv":
        h5_db = Hdf5Client(exchange)
        data= h5_db.get_data(symbol, from_time=from_time, to_time=to_time)
        # Resample the data to the specified timeframe
        data= resample_timeframe(data, tf)
   

        pnl, absolute_mdd= strategies.obv.backtest(data, ma_period=params["ma_period"])
        return pnl, absolute_mdd
    
    elif strategy== "ichimoku":
        h5_db = Hdf5Client(exchange)
        data= h5_db.get_data(symbol, from_time=from_time, to_time=to_time)
        # Resample the data to the specified timeframe
        data= resample_timeframe(data, tf)
        #strategies.ichimoku.backtest(data, 9, 26)
        pnl, absolute_mdd= strategies.ichimoku.backtest(data, tenkan_period= params["tenkan_period"], 
                                          kijun_period= params["kijun_period"])
        return pnl, absolute_mdd
    

    elif strategy== "sup_res":
        h5_db = Hdf5Client(exchange)
        data= h5_db.get_data(symbol, from_time=from_time, to_time=to_time)
        # Resample the data to the specified timeframe
        data= resample_timeframe(data, tf)
        pnl, absolute_mdd= strategies.support_resistance.backtest(data, min_points= params["min_points"], 
                                                     min_diff_points= params["min_diff_points"] , 
                                                     rounding_nb= params["rounding_nb"], 
                                                     take_profit= params["take_profit"], 
                                                     stop_loss= params["stop_loss"])
        return pnl, absolute_mdd
    
    elif strategy== "sma":
        #lib= get_library()

        #obj= lib.Sma_new(exchange.encode(), symbol.encode(), tf.encode(), from_time, to_time)
        #lib.Sma_execute_backtest(obj, params["slow_ma"], params["fast_ma"])

        #pnl= lib.Sma_get_pnl(obj)
        #max_dd= lib.Sma_get_mdd(obj)
        h5_db = Hdf5Client(exchange)
        data= h5_db.get_data(symbol, from_time=from_time, to_time=to_time)
        data= resample_timeframe(data, tf)
        pnl, max_dd= strategies.sma_crossover.backtest(data, slow_ma= params["slow_ma"], fast_ma= params["fast_ma"])
        return pnl, max_dd
    

  
