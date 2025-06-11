# import necessary files
import logging
from exchanges.binance import BinanceClient

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
    client= BinanceClient(True)