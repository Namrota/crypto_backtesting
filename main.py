# import necessary files
"""
Main entry point for the crypto backtesting application.
This script sets up logging to both the terminal and a file, and initializes the Binance client.
It prompts the user to select a program mode: data collection, backtesting, or optimization.
Modules:
    logging: Standard Python logging module for tracking events.
    exchanges.binance.BinanceClient: Custom client for interacting with the Binance exchange.
Logging:
    - Logs are formatted with timestamps, log level, and message.
    - INFO level logs are output to both the terminal and 'info.log' file.
Usage:
    Run the script and follow the prompt to choose the desired program mode.
Attributes:
    root_logger (logging.Logger): The root logger configured for the application.
    formatter (logging.Formatter): Formatter for log messages.
    stream_handler (logging.StreamHandler): Handler for logging to the terminal.
    file_handler (logging.FileHandler): Handler for logging to a file.
Example:
    $ python main.py
    Choose the program mode (data / backtest / optimize): data
"""
import logging
from exchanges.binance import BinanceClient
from exchanges.coinbase import CoinbaseClient

root_logger= logging.getLogger()
root_logger.setLevel(logging.DEBUG)

#Formatter:
formatter= logging.Formatter("%(asctime)s %(levelname)s :: %(message)s")

#show information at the terminal:
stream_handler= logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)

#save the information to a file:
file_handler= logging.FileHandler("info.log")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

#adds the specified Handler to the logger
root_logger.addHandler(stream_handler)
root_logger.addHandler(file_handler)

if __name__== "__main__":
    mode= input("Choose the program mode (data / backtest / optimize): ").lower()
    while True:
        exchange= input("Choose the exchange (binance / coinbase): ").lower()
        if exchange== "binance":
            client= BinanceClient()
            print(client.get_historical_data("BTCUSDT"))
        elif exchange== "coinbase":
            client= CoinbaseClient()
            print(client.get_historical_data("BTC-USDT"))
        else:
            raise ValueError("Invalid exchange selected. Choose 'binance' or 'coinbase'.")
        break
        
    #client= BinanceClient(True)
    #client= CoinbaseClient()
    #print(client.get_historical_data("BTCUSDT"))