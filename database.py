from typing import *
import numpy as np
import pandas as pd
import h5py
import logging
import time


logger= logging.getLogger()

class Hdf5Client:
    """"
    Hdf5Client is a class for managing HDF5 files to store trading data.
    It allows creating datasets for trading symbols and writing data to these datasets.
    Attributes:
        hf (h5py.File): The HDF5 file object for storing trading data for a specific exchange.
    Methods:
        __init__(exchange: str): Initializes the Hdf5Client with the specified exchange and opens the HDF5 file.
        create_dataset(symbol: str): Creates a dataset for the specified trading symbol if it does not already exist.
        write_data(symbol: str, data: List[Tuple]): Writes a list of trading data tuples to the dataset for the specified symbol.
    
    """
    def __init__(self, exchange: str):
        self.hf= h5py.File(f"data/{exchange}.h5", "a")
        self.hf.flush()
    
    def create_dataset(self, symbol: str):
        if symbol not in self.hf.keys():
            self.hf.create_dataset(symbol, (0,6), maxshape=(None, 6), dtype='float64')
            self.hf.flush()

    """
    Writes a list of trading data tuples to the dataset for the specified symbol.
    Args:
        symbol (str): The trading symbol for which the data is being written.
        data (List[Tuple]): A list of tuples containing trading data, where each tuple represents a single data point.
    Returns:
        None
    """
    def write_data(self, symbol:str, data: List[Tuple]):

        # stores timestamp in min_ts and max_ts for a symbol
        min_ts, max_ts= self.get_first_last_timestamp(symbol)

        filtered_data= []

        # if min_ts is None then set min_ts as inf and max_ts as 0
        if min_ts is None:
            min_ts= float("inf")
            max_ts= 0

        for d in data:
            if d[0] < min_ts:
                filtered_data.append(d)
            elif d[0] > max_ts:
                filtered_data.append(d)
        
        if len(filtered_data)== 0:
            logger.warning(f"No data to insert for {symbol}")
            return
        # HDF5 daatasets expect data in array-like format, so we convert the list of tuples to a numpy array.
        data_arr= np.array(filtered_data)
        # self.hf[symbol]: is the dataset (like a table) for the specified symbol.
        # .shape[0] is the number of existing rows.
        # data_arr.shape[0]: number of new rows to be added.
        # HDF5 datasets can be resized, so we resize the dataset to accommodate the new data.
        # append new n rows at the end of the dataset
        self.hf[symbol].resize(self.hf[symbol].shape[0] + data_arr.shape[0], axis= 0)
        self.hf[symbol][-data_arr.shape[0]:] = data_arr
        self.hf.flush()
    
    """
    Retrieves the first and last timestamps from the dataset for the specified trading symbol.
            symbol (str): The trading symbol whose dataset is being queried.
            Tuple[None, None]: If the dataset is empty, returns (None, None).
            Tuple[float, float]: If data exists, returns a tuple containing the earliest and latest timestamps (as floats).
    """
    def get_first_last_timestamp(self, symbol: str)-> Union[Tuple[None, None], Tuple[float, float]]:
        
        existing_data= self.hf[symbol][:]

        if len(existing_data) == 0:
            return None, None
        # first_ts and last_ts looks for the min and max timestamp
        first_ts= min(existing_data, key= lambda x: x[0])[0]
        last_ts= max(existing_data, key= lambda x: x[0])[0]

        return first_ts, last_ts

    """
    Retrieves trading data for a specific symbol within a given time range.
    Args:
        symbol (str): The trading symbol for which data is being retrieved.
        from_time (int): The start of the time range (timestamp in milliseconds).
        to_time (int): The end of the time range (timestamp in milliseconds).
    Returns:
        Union[None, pd.DataFrame]: Returns a DataFrame containing the trading data for the specified symbol and time range.
                                    If no data is found, returns None.
    """
    def get_data(self, symbol: str, from_time: int, to_time: int)-> Union[None, pd.DataFrame]:
        
        start_query= time.time()

        existing_data= self.hf[symbol][:]      

        if len(existing_data)== 0:
            return None
        
        data= sorted(existing_data, key= lambda x: x[0])
        data= np.array(data)

        df= pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df= df[(df["timestamp"] >= from_time) & (df["timestamp"] <= to_time)]
        df["timestamp"]= pd.to_datetime(df["timestamp"].values.astype(np.int64), unit= "ms")
        df.set_index("timestamp", drop= True, inplace=False)

        query_time= round((time.time() - start_query),2)
        logger.info(f"Retrieved {len(df.index)} from {symbol} in {query_time} seconds")
        return df