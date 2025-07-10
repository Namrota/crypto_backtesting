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

import backtester
import datetime
import optimizer

from utils.time_convertor import *
from exchanges.binance import BinanceClient
from exchanges.coinbase import CoinbaseClient
from data_collector import collect_all


# Set up logging
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
        if exchange in ["binance", "coinbase"]:
            break
            
            

    if exchange in ["binance", "coinbase"]:
        client= BinanceClient()
        #print(client.get_historical_data("BTCUSDT"))
    elif exchange== "coinbase":
        client= CoinbaseClient()
        #print(client.get_historical_data("BTC-USDT"))

    while True:
        symbol= input("Enter the trading symbol (e.g., BTCUSDT for Binance, BTC-USDT for Coinbase): ").upper()
        if symbol in client.symbols:
            break
    
    if mode== "data":
        collect_all(client, exchange, symbol)
    
    elif mode in ["backtest", "optimize"]:
        #strategy
        available_strategies= ["obv", "ichimoku", "sup_res", "sma"]
        while True:
            strategy= input(f"Choose a strategy- ({', '.join(available_strategies)}): ").lower()
            if strategy in available_strategies:
                break
                
        #timeframe
        while True:
            tf= input(f"Choose the timeframe({', '.join(TF_EQUIV.keys())}): ").lower()
            if tf in TF_EQUIV.keys():
                break
        
        #from
        while True:
            from_time= input("Backtest from (yyyy-mm-dd or Press Enter): ")
            if from_time== "":
                from_time= 0
                break

            try:
                from_time= int(datetime.datetime.strptime(from_time, "%Y-%m-%d").timestamp() * 1000)
                break
            except ValueError:
                continue
        
        #to
        while True:
            to_time= input("Backtest to (yyyy-mm-dd or Press Enter): ")
            if to_time== "":
                to_time= int(datetime.datetime.now().timestamp() * 1000)
                break

            try:
                to_time= int(datetime.datetime.strptime(to_time, "%Y-%m-%d").timestamp() * 1000)
                break
            except ValueError:
                continue
    
        if mode == "backtest":
            print(backtester.run(exchange, symbol, strategy, tf, from_time, to_time))

        elif mode== "optimize":
            #Population Size
            while True:
                try:
                    pop_size= int(input(f"Choose a Population Size: "))
                    break
                except ValueError:
                    continue
            

             #Iterations: One generation of the population corresponds to one iteration
            while True:
                try:
                    generations= int(input(f"Choose a number of generations: "))
                    break
                except ValueError:
                    continue
            

            nsga2= optimizer.Nsga2(exchange= exchange, symbol= symbol,
                                   strategy= strategy, tf= tf,
                                   from_time= from_time, to_time= to_time,
                                   population_size= pop_size)

            p_population= nsga2.create_initial_population()
            p_population= nsga2.evaluate_population(p_population)
            # we only wnat to proceed with the data having trades that is PNL !=0:
            all_individuals= p_population.copy()
            real_trades=[i for i in all_individuals if i.pnl != 0]
            no_trade_individuals= [i for i in all_individuals if i.pnl == 0]

            p_population= real_trades
            p_population= nsga2.crowding_distance(p_population)

            # Counter to calculate the number of generations:
            g= 0
            while g < generations:
                #offspring population:
                q_population = nsga2.create_offspring_population(p_population)
                q_population = nsga2.evaluate_population(q_population)

                # we only wnat to proceed with the data having trades that is PNL !=0:
                all_individuals= q_population.copy()
                real_trades=[i for i in all_individuals if i.pnl != 0]
                no_trade_individuals= [i for i in all_individuals if i.pnl == 0]

                q_population= real_trades

                r_population= q_population + p_population

                nsga2.population_params.clear()


                # identifier i for each individual:
                i= 0
                population= dict()

                # Store the population in dictionary with the identifier as its key
                for bt in r_population:
                    bt.reset_results()
                    nsga2.population_params.append(bt.parameters)
                    population[i]= bt
                    i+= 1
                    
                fronts= nsga2.non_dominated_sorting(population)
                # Crowding distance of each Front:
                for j in range(len(fronts)):
                    fronts[j]= nsga2.crowding_distance(fronts[j])
                
                p_population= nsga2.create_new_population(fronts)

                print(f"{int((g + 1) / generations * 100)}%", end= ' ')
                g+=1
            
            print("\n")

            for individual in p_population:
                print(individual)
                #for front in fronts:
                #    print(front)