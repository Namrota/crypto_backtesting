from utils.params import *
from database import Hdf5Client
from utils.time_convertor import *
from models import BacktestResult
import random
import typing

import strategies.obv
import strategies.ichimoku
import strategies.support_resistance

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
            


        
    '''
    Creating initial population for NSGA 2 algorithm called P0
    
    
    Generate population_size individuals (BacktestResult objects) randomly:

    Loop until you have enough.

    For each hyperparameter in self.params_data:

    Draw an integer or float in its allowed range.

    Store it in backtest.parameters.

    Uniqueness check:
    if backtest not in population: ensures no two identical parameter sets.
    
    
    
    '''

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
    
    '''

    Non-dominated sorting to find the Fronts with different ranking in order to get the Pareto Front:

    fronts will become a list of “fronts,” where

        fronts[0] is the first (best) Pareto front,

        fronts[1] the second, and so on.
    
    After the loops, for each individual you know:

        dominated_by — how many others dominate it.

        dominates — list of IDs it beats.

    Returns a list of Fronts which in turn contains a list of individuals

    '''
    
    def non_dominated_sorting(self, population: typing.Dict[int, BacktestResult])-> typing.List[typing.List[BacktestResult]]:
        fronts=[]
        # Comparing one individual with the other individual in a loop 
        # Collecting all the IDs of the individual that dominates the other individual
        for id_1, indiv_1 in population.items():
            for id_2, indiv_2 in population.items():
                # The below condition means that individual 1 cannot perform worse than individual 2:
                # The individual 1 should have atleast one advantage over the individual 2:
                if indiv_1.pnl >= indiv_2.pnl and indiv_1.max_dd<= indiv_2.max_dd \
                    and(indiv_1.pnl > indiv_2.pnl or indiv_1.max_dd < indiv_2.max_dd):
                    indiv_1.dominates.append(id_2)
                # Checking the condition for if individual 2 has an advantage over individual 1
                elif indiv_2.pnl >= indiv_1.pnl and indiv_2.max_dd<= indiv_1.max_dd \
                    and(indiv_2.pnl > indiv_1.pnl or indiv_2.max_dd < indiv_1.max_dd):
                    indiv_1.dominated_by += 1

            if indiv_1.dominated_by == 0:
                if len(fronts) == 0:
                    fronts.append([])
                fronts[0].append(indiv_1)
                indiv_1.rank= 0  # The individual belongs to Front 1
            
        i= 0

        while True:
            # Get the other fronts
            fronts.append([])

            for indiv_1 in fronts[i]:
                for indiv_2_id in indiv_1.dominates:
                    population[indiv_2_id].dominated_by -= 1
                    if population[indiv_2_id].dominated_by == 0:
                        fronts[i + 1].append(population[indiv_2_id])
                        population[indiv_2_id].rank = i + 1


            if len(fronts[i + 1]) > 0:
                i+= 1
            else:
                del fronts[-1]
                break
        return fronts

    '''
    Evaluate the Population: PnL and Maximum Drawdown values will be filled in the updated List

    For each individual:

    Call the appropriate backtest function (Python or C).

    Unpack the returned PnL and max-drawdown into the BacktestResult fields.

    Return the list, now with every individual carrying its (pnl, max_dd) pair.
    
    '''
    def evaluate_population(self, population: typing.List[BacktestResult])-> typing.List[BacktestResult]:
        if self.strategy == "obv":
            for bt in population:
                bt.pnl, bt.max_dd= strategies.obv.backtest(self.data, ma_period=bt.parameters["ma_period"])
            return population
    
        elif self.strategy== "ichimoku":
            for bt in population:
                bt.pnl, bt.max_dd= strategies.ichimoku.backtest(self.data, tenkan_period= bt.parameters["tenkan_period"], 
                                            kijun_period= bt.parameters["kijun_period"])
            return population
        

        elif self.strategy== "sup_res":
            for bt in population:
                bt.pnl, bt.max_dd= strategies.support_resistance.backtest(self.data, min_points= bt.parameters["min_points"], 
                                                        min_diff_points= bt.parameters["min_diff_points"] , 
                                                        rounding_nb= bt.parameters["rounding_nb"], 
                                                        take_profit= bt.parameters["take_profit"], 
                                                        stop_loss= bt.parameters["stop_loss"])
            return population
        
        elif self.strategy== "sma":
            for bt in population:
                self.lib.Sma_execute_backtest(self.obj, bt.parameters["slow_ma"], bt.parameters["fast_ma"])
                bt.pnl= self.lib.Sma_get_pnl(self.obj)
                bt.max_dd= self.lib.Sma_get_mdd(self.obj)


            return population
        

    


