import pandas as pd 
import numpy as np

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", 1000)

def backtest(df: pd.DataFrame, ma_period: int):
    df["obv"] = (np.sign(df["close"].diff()) * df["volume"]).fillna(0).cumsum()
    df["obv_ma"] = df["obv"].rolling(window=ma_period).mean()
    df["signal"] = np.where(df["obv"] > df["obv_ma"], 1, -1)
    df["close_change"]= df["close"].pct_change(fill_method=None)
    df["signal_shift"]= df["signal"].shift(1)
    #returns pnl for each candle
    df["pnl"]= df["signal"].shift(1) * (df["close"].pct_change(fill_method=None))
    return df["pnl"].sum() * 100
    #print(df)