import pandas as pd 

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
    # nearest support/resistance levels
    df["rounded_high"]= round(df["high"]/rounding_nb)*rounding_nb
    df["rounded_low"]= round(df["low"]/rounding_nb)*rounding_nb
    # dictionary of rounded high and low prices, storing the prices progressively
    price_groups= {"supports": dict(), "resistances": dict()}
    resistances_supports= {"supports": [], "resistances": []}
    # looping through the DataFrame to find support and resistance levels
    for index, row in df.iterrows():
        # check for each row if the rounded high or low is already in the price groups
        for side in ["resistances", "supports"]:
            # Determine if we are looking at resistance or support
            h_l= "high" if side== "resistances" else "low" 
            # check if the rounded price is already in the price groups
            # filtering high for resistances and low for supports in each row
            if row["rounded_" + h_l] in price_groups[side]:
                grp= price_groups[side][row["rounded_"+ h_l]]
                # check if the current index is greater than the last index in the group
                # and if the difference between the current index and the last index is greater than the minimum difference
                # in points multiplied by the candle length
                if index >= grp["last"] + min_diff_points * candle_length:
                    grp["prices"].append(row[h_l])

                    if len(grp["prices"]) >= min_points:
                        extreme_price= max(grp["prices"]) if side== "resistances" else min(grp["prices"])
                        resistances_supports[side].append({
                            "price": extreme_price,
                            "broken": False
                        })

                    grp["last"]= index
            else:
                price_groups[side][row["rounded_" + h_l]]= {"prices": [row[h_l]], "start_time": index, "last": index}

    print(df)