from ctypes import *


STRAT_PARAMS= {
    "obv": {
        "ma_period": {"name": "Moving Average Period", "default": 9, "type": int, "min": 2, "max": 200}

    },
    "ichimoku":{
        "kijun_period": {"name": "Kijun Period", "default": 26, "type": int, "min": 2, "max": 200},
        "tenkan_period": {"name": "Tenkan Period", "default": 9, "type": int, "min": 2, "max": 200}
    },
    "sup_res": {
        "min_points": {"name": "Minimum Points", "default": 3, "type": int, "min": 2, "max": 20},
        "min_diff_points": {"name": "Minimum Difference Between Points", "default": 9, "type": int, "min": 2, "max": 100},
        "rounding_nb": {"name": "Rounding Number", "default": 400, "type": float, "min": 10, "max": 500, "decimals": 2},
        "take_profit": {"name": "Take Profit Percentage", "default": 3, "type": float, "min": 1, "max": 40, "decimals": 2},
        "stop_loss": {"name": "Stop Loss Percentage", "default": 3, "type": float, "min": 1, "max": 40, "decimals": 2}
    },
    "sma":{
        "slow_ma": {"name": "Slow Moving Average", "default": 50, "type": int, "min": 2, "max": 200},
        "fast_ma": {"name": "Fast Moving Average", "default": 9, "type": int, "min": 2, "max": 200}
    },
}


def get_library():
    
    lib= CDLL("backtestingCpp/build/libbacktestingCpp.dll", winmode=0)
    #SMA
    lib.Sma_new.restype= c_void_p
    lib.Sma_new.argtypes=[c_char_p, c_char_p, c_char_p, c_longlong, c_longlong ]

    lib.Sma_execute_backtest.restype= c_void_p
    lib.Sma_execute_backtest.argtypes=[c_void_p, c_int, c_int]

    lib.Sma_get_pnl.restype= c_double
    lib.Sma_get_pnl.argtypes=[c_void_p]

    lib.Sma_get_mdd.restype= c_double
    lib.Sma_get_mdd.argtypes=[c_void_p]

    return lib

