from utils.params import *
from database import Hdf5Client
from utils.time_convertor import *
from models import BacktestResult
import random
import typing


class Nsga2:
    def __init__(self, exchange:str, 
                 symbol:str, strategy:str, 
                 tf:str, from_time:int, to_time:int,
                 population_size:int):
        
        self.exchange= exchange
        self.symbol= symbol
        self.strategy= strategy
        self.tf= tf
        self.from_time= from_time
        self.to_time= to_time
        self.population_size= population_size

        self.params_data= STRAT_PARAMS[strategy]

        if self.strategy in ["obv", "ichimoku", "sup_res"]:
            h5_db = Hdf5Client(exchange)
            # data variable will be an instance variable because it wil be used in other methods
            self.data= h5_db.get_data(symbol, from_time=from_time, to_time=to_time)
            # Resample the data to the specified timeframe
            self.data= resample_timeframe(self.data, tf)
        
        elif self.strategy in ["sma"]:

            self.lib= get_library()

            if self.strategy == "sma":
                self.obj= self.lib.Sma_new(exchange.encode(), symbol.encode(), tf.encode(), from_time, to_time)
            


        
    '''Creating initial population for NSGA 2 algorithm called P0'''

    def create_initial_population(self)-> typing.List[BacktestResult]:
        population=[]
        '''
        Keep creating an individual or a backtest result until the size of the population is reached
        '''
        while len(population) < self.population_size:
            
            backtest= BacktestResult()
            #Generating Random Parameters
            for p_code, p in self.params_data.items():
                if p["type"] == int:
                    backtest.parameters[p_code]= random.randint(p["min"], p["max"])
                elif p["type"] == float:
                    backtest.parameters[p_code]= round(random.uniform(p["min"], p["max"]), p["decimals"])
            
            if backtest not in population:
                population.append(backtest)

        return population 

        