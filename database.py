from typing import *
import numpy as np
import h5py

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
        # HDF5 daatasets expect data in array-like format, so we convert the list of tuples to a numpy array.
        data_arr= np.array(data)
        # self.hf[symbol]: is the dataset (like a table) for the specified symbol.
        # .shape[0] is the number of existing rows.
        # data_arr.shape[0]: number of new rows to be added.
        # HDF5 datasets can be resized, so we resize the dataset to accommodate the new data.
        # append new n rows at the end of the dataset
        self.hf[symbol].resize(self.hf[symbol].shape[0] + data_arr.shape[0], axis= 0)
        self.hf[symbol][-data_arr.shape[0]:] = data_arr
        self.hf.flush()
    
