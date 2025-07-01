STRAT_PARAMS= {
    "obv": {
        "ma_period": {"name": "Moving Average Period", "default": 9, "type": int}

    },
    "ichimoku":{
        "kijun_period": {"name": "Kijun Period", "default": 26, "type": int},
        "tenkan_period": {"name": "Tenkan Period", "default": 9, "type": int}
    },
    "sup_res": {
        "min_points": {"name": "Minimum Points", "default": 3, "type": int},
        "min_diff_points": {"name": "Minimum Difference Between Points", "default": 9, "type": int},
        "rounding_nb": {"name": "Rounding Number", "default": 400, "type": float},
        "take_profit": {"name": "Take Profit Percentage", "default": 3, "type": float},
        "stop_loss": {"name": "Stop Loss Percentage", "default": 3, "type": float}
    },
}