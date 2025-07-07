import typing

class BacktestResult:
    def __init__(self):

        # Attributes
        self.pnl: float= 0.0
        self.max_dd: float= 0.0
        # Parameters generated randomly are stored in Dictionary
        self.parameters: typing.Dict= dict()
        # attributes related to the NSGA 2 Algorithm
        self.dominated_by: int= 0 # dominated by how many other backtests
        self.dominates:typing.List[int]= [] #which backtest dominates
        self.rank: int= 0 #Pareto Front
        self.crowding_distance: float= 0.0


    def __repr__(self):
        return f"PNL= {round(self.pnl, 2)}; Maximum Drawdown={round(self.max_dd, 2)}; " \
            f"Parameters= {self.parameters}; Rank={self.rank}; Crowding Distance={self.crowding_distance}"
    
    # Resetting all the variables to their initial state, since these variables wil get updated
    # generation after generation, or iteration apart from the params of the backtest
    def reset_results(self):
        self.pnl= 0.0
        self.max_dd= 0.0
        self.dominated_by= 0 
        self.dominates.clear()
        self.rank= 0
        self.crowding_distance= 0.0



