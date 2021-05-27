# import datetime
import pickle
import random
from datetime import date, datetime, timedelta

import backtrader as bt
import backtrader.analyzers as btanalyze
import matplotlib
from backtrader.dataseries import TimeFrame
from utility import util

from Brain import Brain, Strategy
from PolygonData import getData
# from numba import cuda, jit

# from neat import visualize


class PolyData(bt.feeds.GenericCSVData):
    
  params = (
    ('fromdate', datetime.min),
    ('todate', datetime.max),
    ('nullvalue', 0.0),
    ('dtformat', ('%Y-%m-%d %H:%M')),
    # ('tmformat', ('%H:%M')),
    ('timeframe',bt.TimeFrame.Minutes),
    ('datetime', 6),
    # ('time', 9),
    ('high', 4),
    ('low', 5),
    ('open', 2),
    ('close', 3),
    ('volume', 0),
    ('openinterest', -1)
    )

class Agent(): 
    """The Agent is the middleware between the Brain and the Matrix. 
    It should receive data from the Matrix and pass it along to the Brain, and once the Brain issued a command, it should perform trading actions accordingly. 
    """
    # def __init__(self, equity, stockSymbol, dataPath, date, genome=None, config=None):
    def __init__(self, equity, stockSymbol, dataPath, date, genome, config):
        # print(stockSymbol)
        self.cerebro = bt.Cerebro()
        # dataPath = getData(stockSymbol, date)
        data = PolyData(dataname = dataPath)
        self.cerebro.adddata(data)
        self.cerebro.addstrategy(Strategy, genome, config)
        # self.cerebro.addstrategy(Strategy)
        self.cerebro.broker.setcash(equity)
        self.cerebro.addsizer(bt.sizers.PercentSizer, percents = 100)
        self.cerebro.addanalyzer(btanalyze.SharpeRatio, _name = "sharpe")
        self.cerebro.addanalyzer(btanalyze.Transactions, _name = "trans")
        self.cerebro.addanalyzer(btanalyze.TradeAnalyzer, _name = "trade")
        
    # @cuda.jit(device=True)
    def start(self): 
        self.backtest = self.cerebro.run(runonce=False) 
        # return self
        # self.backtest = self.cerebro.run() 

    def finalValue(self): 
        return self.cerebro.broker.getvalue()

    def plot(self): 
        self.cerebro.plot()
    
    def fitness(self): 
        wincount = self.backtest[0].wincount
        positioncount = self.backtest[0].positioncount
        winrate = wincount/positioncount if positioncount>0 else 1
        fitness = self.backtest[0].fitness * winrate if self.backtest[0].fitness >=0 else self.backtest[0].fitness * (1-winrate)
        return fitness
        
if __name__ == "__main__": 
    import os
    import visualize
    import neat
    today = date.today()
    fromdate = today + timedelta(days=-today.weekday(), weeks=-10)
    todate = fromdate+timedelta(days=5)
    # print(datetime(today+ timedelta(days=-today.weekday(), weeks=-10)+timedelta(days=5)))
    geno = pickle.load( open( "best", "rb" ) )
    print(geno)
    # conf = pickle.load( open( "conf", "rb" ) )
    config_path = os.path.join(util.getProjectDir(), r"config\NEATconfig.txt")
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                        neat.DefaultSpeciesSet, neat.DefaultStagnation,
                        config_path)
    folders = []
    files = []
    account = Agent(
            100000, 
            '',
            f"./trainingData/A/A_2006-01-13.csv", 
            '2019-11-05',
            genome = geno, 
            config = config)
    # print(account.genome)
    account.start()
    print(account.finalValue())
    account.plot()
    plotPath = './plots'
    nodeNames = {
            -1: "price", 
            -2: "ma_fast", 
            -3: "ma_slow", 
            -4: "expMA", 
            -5:"wtgMA",
            -6:"stocSlow", 
            -7:"MACD", 
            -8:"rsi",
            -9:"smoMA",
            -10:"ATR", 
            -11:"buyprice", 
            -12:"sellprice",
            0: "buy", 
            1: "sell", 
            2: "close"}
    visualize.draw_net(config, geno, view = True, node_names=nodeNames, filename=f'{plotPath}/net.dot')
