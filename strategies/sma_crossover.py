import pandas as pd 
import pandas_ta as ta
import matplotlib.pyplot as plt
import mplfinance as mpf
import numpy as np

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", 1000)
'''

'''
def backtest(df: pd.DataFrame, slow_ma: int, fast_ma: int):
    
    df["slow_ma"]= df["close"].rolling(window= slow_ma).mean()
    df["fast_ma"]= df["close"].rolling(window= fast_ma).mean()
    # dropping the missing values in 'slow_ma' and 'fast_ma' columns:
    # making a copy to suppress the warnings "A value is trying to be set on a copy of a slice from a DataFrame."
    df= df.dropna(subset=['slow_ma', 'fast_ma']).copy()
    df["signal"]= np.where(df["fast_ma"] > df["slow_ma"], 1, -1)
    # Captures the changes in the signal from one time period to the other, position changes then crossover occurred
    df["position"]= df["signal"].diff()
    #calculate the daily returns of the pair:
    df["returns"]= df["close"].pct_change()
    # calculate the strategy returns:
    df["pnl"]= df["returns"]*df["position"].shift(1)

    #Calculating Maximum Drawdown
    df["cum_pnl"]= df["pnl"].cumsum()
    df["max_cum_pnl"]= df["cum_pnl"].cummax()
    df["drawdown"]= df["max_cum_pnl"] - df["cum_pnl"]

    return df["pnl"].sum() * 100, df["drawdown"].max()
    #return pnl