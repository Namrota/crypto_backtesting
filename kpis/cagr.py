'''
The compound annual growth rate (CAGR) is the rate of return (RoR) 
that would be required for an investment to grow from its beginning balance 
to its ending balance, assuming the profits were reinvested at the end of each 
period of the investment’s life span. 
CAGR is a useful measure of growth over multiple time periods. 
It can be thought of as the rate at which an investment would have grown if it had 
grown at a steady rate.
'''
import pandas as pd
import numpy as np


def kpi(df: pd.DataFrame) -> float:
    """
    Calculate the Compound Annual Growth Rate (CAGR) for a given DataFrame.

    Args:
        df (pd.DataFrame): DataFrame containing 'close' prices and a datetime index.

    Returns:
        float: The CAGR value.
    
    If the dataset has gaps (API limits or downtime), the CAGR calculation may be 
    inaccurate as it assumes continuous compounding over the entire period. Thus, using
    cumulative returns from all trades instead of just the start and end values is preferred.
    
    Note:
        Ensure that the DataFrame index is in datetime format and sorted in ascending order.
    """
    # Ensure the DataFrame is sorted by date
    cagr_df= df.deepcopy().sort_index()

    # Calculate cumulative returns
    cagr_df['returns']= cagr_df['close'].pct_change()
    cagr_df['cumulative_returns']= (1 + cagr_df['returns']).cumprod()

    # Calculate the total number of years in the dataset
    total_seconds = (cagr_df.index[-1] - cagr_df.index[0]).total_seconds()
    total_years = total_seconds / 365.25 * 24 * 3600  # Using 365.25 to account for leap years
    print(f'Total Years for CAGR calculation: {total_years} years')

    # if total years is lesser than or equal to 0, return NaN to avoid division by zero
    if total_years <=0:
        return float('nan')
    

    # Calculate CAGR
    cagr = cagr_df['cumulative_returns'].iloc[-1] ** (1 / total_years) - 1

    return cagr