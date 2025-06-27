import pandas as pd 
import numpy as np

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", 1000)

def backtest(df: pd.DataFrame, tenkan_period: int, kijun_period: int):
    """
    Backtest the Ichimoku strategy on the provided DataFrame.


    Args:
        df (pd.DataFrame): DataFrame containing OHLCV data.
        tenkan_period (int): Period for Tenkan-sen (past 9 periods).
        kijun_period (int): Period for Kijun-sen (past 26 periods)
        

    Returns:
        float: Total profit and loss from the strategy.
    """
    # Calculate Ichimoku components
    # Conversion Line: Tenkan Sen
    df["rolling_min_tenkan"]= df['low'].rolling(window=tenkan_period).min()
    df["rolling_max_tenkan"]= df['high'].rolling(window=tenkan_period).max()
    df['tenkan_sen'] = (df["rolling_min_tenkan"]+ df["rolling_max_tenkan"]) / 2

    df.drop(columns=["rolling_min_tenkan", "rolling_max_tenkan"], axis=1, inplace=True)

    # Base Line: Kijun Sen
    df["rolling_min_kijun"]= df['low'].rolling(window=kijun_period).min()
    df["rolling_max_kijun"]= df['high'].rolling(window=kijun_period).max()
    df['kijun_sen'] = (df["rolling_min_kijun"]+df["rolling_max_kijun"]) / 2

    df.drop(columns=["rolling_min_kijun", "rolling_max_kijun"], axis=1, inplace=True)   

    # Leading Span A: Senkou Span A
    df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(kijun_period)

    # Leading Span B: Senkou Span B
    df['rolling_senkou'] = ((df['high'].rolling(window=kijun_period*2).max()) + (df['low'].rolling(window=kijun_period*2)).min()) / 2
    df['senkou_span_b'] = df['rolling_senkou'].shift(26)

    df.drop(columns=["rolling_senkou"], axis=1, inplace=True)

    # Lagging Span: Chikou Span
    # Chikou Span is the closing price shifted back by 26 periods
    df['chikou_span'] = df['close'].shift(-1 * kijun_period)

    df.dropna(inplace=True)

    #print(df)

    #Signal
    df["tenkan_minus_kijun"]= df["tenkan_sen"] - df["kijun_sen"]
    df["prev_tenkan_minus_kijun"]= df["tenkan_minus_kijun"].shift(1)
    #df["senkou_span_a_minus_senkou_span_b"]= df["senkou_span_a"] - df["senkou_span_b"]
    #df["prev_senkou_span_a_minus_senkou_span_b"]= df["senkou_span_a_minus_senkou_span_b"].shift(1)
    df["prev_senkou_span_a"]= df["senkou_span_a"].shift(1)
    df["prev_senkou_span_b"]= df["senkou_span_b"].shift(1)
    df["signal"]= np.where(
        (df["tenkan_minus_kijun"] > 0)  #tenkan sen and kijun sen crossover
        & (df["prev_tenkan_minus_kijun"] < 0) 
        & (df["close"]> df["senkou_span_a"]) # close price greater than senkou span A
        & (df["close"] > df["senkou_span_b"]) # close price greater than senkou span B
        & (df["close"]> df["chikou_span"]) # close price greater than chikou span
        & (df["senkou_span_a"] > df["senkou_span_b"]) # senkou span A greater than senkou span B
        & (df["prev_senkou_span_a"] < df["prev_senkou_span_b"]), 1,  # bullish or long signal

        np.where(
        (df["tenkan_minus_kijun"] < 0) 
        & (df["prev_tenkan_minus_kijun"] > 0) 
        & (df["close"]< df["senkou_span_a"])
        & (df["close"]< df["senkou_span_b"])
        & (df["close"]< df["chikou_span"])
        & (df["senkou_span_a"] < df["senkou_span_b"])
        & (df["prev_senkou_span_a"] > df["prev_senkou_span_b"]), -1, 0) # bearish or short signal, otherwise no signal
    )  

    # Calculate PnL
    # Dataframe only with 1 or -1 signals
    signal_data= df[df["signal"] != 0].copy()
    # Calculate the percentage change in close price and shift the signal by 1 to align with the previous signal
    signal_data["pnl"]= signal_data["close"].pct_change() * signal_data["signal"].shift(1)
    #return signal_data
    return signal_data['pnl'].sum() * 100  # Total PnL in percentage