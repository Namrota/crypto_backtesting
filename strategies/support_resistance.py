import pandas as pd 

import matplotlib.pyplot as plt
import mplfinance as mpf
import numpy as np

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", 1000)

def backtest(df: pd.DataFrame, min_points: int, min_diff_points:int, rounding_nb: float, take_profit: float, stop_loss: float):
    """
    Backtest the support and resistance strategy on the given DataFrame.

    Args:
        df (pd.DataFrame): DataFrame containing OHLCV data with 'open', 'high', 'low', 'close', and 'volume' columns.
        min_points (int): Minimum number of points to consider a level as support or resistance.
        min_diff_points (int): Minimum difference in points between levels.
        rounding_nb (float): multiple to round the prices.
        take_profit (float): Take profit percentage.
        stop_loss (float): Stop loss percentage.

    Returns:
       pnl (float): The total profit or loss from the backtest.
    """
    # difference in milliseconds between each candle
    candle_length= df.iloc[1].name - df.iloc[0].name

    pnl= 0
    trade_side= 0
    entry_price= None

    # nearest support/resistance levels
    df["rounded_high"]= round(df["high"]/rounding_nb)*rounding_nb
    df["rounded_low"]= round(df["low"]/rounding_nb)*rounding_nb
    # dictionary of rounded high and low prices, storing the prices progressively
    price_groups= {"supports": dict(), "resistances": dict()}
    # Storing information for plotting the support and resistance levels
    levels= {"supports": [], "resistances": []}
    # holds last 10 Highs and Lows
    last_h_l= {"supports": [], "resistances": []}
    resistances_supports= {"supports": [], "resistances": []}

    # NumPy Arrays: dataframe converted to NumPy arrays for faster access
    highs= np.array(df["high"])
    lows= np.array(df["low"])
    rounded_highs= np.array(df["rounded_high"])
    rounded_lows= np.array(df["rounded_low"])
    closes= np.array(df["close"])
    times= np.array(df.index)

    row= {"high": highs, "low": lows, "rounded_high": rounded_highs, "rounded_low": rounded_lows, "close": closes}
    # looping through NumPy arrays for faster access
    # using iterrows() to access each row in the DataFrame
    # this is not the most efficient way, but it is easier to understand
    for i in range(len(highs)):
        index= times[i]
        # check for each row if the rounded high or low is already in the price groups
        for side in ["resistances", "supports"]:
            # Determine if we are looking at resistance or support
            h_l= "high" if side== "resistances" else "low" 
            # check if the rounded price is already in the price groups
            # filtering high for resistances and low for supports in each row
            if row["rounded_" + h_l][i] in price_groups[side]:

                grp= price_groups[side][row["rounded_"+ h_l][i]]
                broken_in_last= 0

                if grp["start_time"] is None:
                    # check if the price candles was broken let's say, 3 candles before:
                    
                    for c in last_h_l[side]:
                        if c > row[h_l][i] and side== "resistances":
                            broken_in_last+= 1
                        elif c < row[h_l][i] and side== "supports":
                            broken_in_last+= 1
                    if broken_in_last < 3:
                        grp["start_time"]= index
                   
                # check if the current index is greater than the last index in the group
                # and if the difference between the current index and the last index is greater than the minimum difference
                # in points multiplied by the candle length
                if  broken_in_last < 3 and (grp["last"] is None or index >= grp["last"] + min_diff_points * candle_length):
                    grp["prices"].append(row[h_l][i])

                    if len(grp["prices"]) >= min_points:
                        extreme_price= max(grp["prices"]) if side== "resistances" else min(grp["prices"])
                        levels[side].append([(grp["start_time"], extreme_price), (index, extreme_price)])
                        resistances_supports[side].append({
                            "price": extreme_price,
                            "broken": False
                        })

                    grp["last"]= index
            else:
                # check if the price candles was broken let's say, 3 candles before:
                broken_in_last= 0
                for c in last_h_l[side]:
                    if c > row[h_l][i] and side== "resistances":
                        broken_in_last+= 1
                    elif c < row[h_l][i] and side== "supports":
                        broken_in_last+= 1
                if broken_in_last < 3:
                    price_groups[side][row["rounded_" + h_l][i]]= {"prices": [row[h_l][i]], "start_time": index, "last": index}
            
            #Check whether the price groups are still valid or not
            for key, value in price_groups[side].items():
                # if price is not empty, perform more checks
                if len(value["prices"]) > 0:
                    # check whether the current row's high or low is greater than the maximum or minimum price in the group
                    if side== "resistances" and row[h_l][i] > max(value["prices"]):
                        value["prices"].clear()
                        value["start_time"]= None
                        value["last"]= None
                    elif side== "supports" and row[h_l][i] < min(value["prices"]):
                        value["prices"].clear()
                        value["start_time"]= None
                        value["last"]= None
            
            last_h_l[side].append(row[h_l][i])
            if len(last_h_l[side]) > 10:
                last_h_l[side].pop(0)
            
            #check for new trade

            for sup_res in resistances_supports[side]:
                # if the close price breaks the resistance or support level
                entry_condition= row["close"][i] > sup_res["price"] if side== "resistances" else row["close"][i] < sup_res["price"]

                if entry_condition and not sup_res["broken"]:
                    sup_res["broken"]= True
                    if trade_side == 0:
                        entry_price= row["close"][i]
                        trade_side= 1 if side== "resistances" else -1

            # Check PNL for the trade
            if trade_side == 1:
                if row["close"][i]  >= entry_price * (1 + take_profit / 100) or row["close"][i] <= entry_price * (1 - stop_loss / 100):
                    pnl += (row["close"][i] / entry_price - 1) * 100
                    trade_side= 0
                    entry_price= None
            elif trade_side == -1:
                if row["close"][i]  <= entry_price * (1 - take_profit / 100) or row["close"][i] >= entry_price * (1 + stop_loss / 100):
                    pnl += (entry_price / row["close"][i] - 1) * 100
                    trade_side= 0
                    entry_price= None
            
    resistance_lines= levels["resistances"]
    support_lines= levels["supports"]  

    print(f"Found {len(resistance_lines)} resistance levels and {len(support_lines)} support levels")         
    
    '''mpf.plot(df, 
             type='candle', style='charles', 
             alines=dict(alines=resistance_lines + support_lines,
             linewidths= [0.5]* len(resistance_lines + support_lines), 
             colors= ['green']* len(resistance_lines) + ['red']* len(support_lines)
             ),
             title='Support and Resistance Levels (Green=Resistance, Red=Support)',)
    plt.show()
    '''
    return pnl  # Total PnL in percentage

    