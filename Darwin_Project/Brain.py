import neat
import backtrader as bt
import math

class Brain(): 
    """A Brain that independents from trading platforms. 
    It should take in data and perform thinking then output an action command to the agent. 
    """
    def __init__(self, genome, config): 
        # self.net = neat.nn.FeedForwardNetwork.create(genome, config)
        self.net = neat.nn.RecurrentNetwork.create(genome, config)

    def think(self, input=[]): 
        return self.net.activate(input)


class Strategy(bt.Strategy): 
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.datetime()
        print('%s, %s' % (dt, txt))
    
    # def __init__(self, genome=None, config=None): 
    def __init__(self, genome, config): 
        self.order = None
        self.buyprice = math.inf
        self.sellprice = -math.inf
        # self.buycomm = None
        self.wincount = 0
        self.positioncount = 0

        self.fitness = 0
        self.brain = Brain(genome, config)
        self.ma_fast = bt.indicators.MovingAverageSimple(self.datas[0], period = 10,subplot = True)
        self.ma_slow = bt.indicators.MovingAverageSimple(self.datas[0], period = 30,subplot = True)
        self.expMA = bt.indicators.ExponentialMovingAverage(self.datas[0], period=30,subplot = True)
        self.wtgMA = bt.indicators.WeightedMovingAverage(self.datas[0], period=30,subplot = True)
        self.stocSlow = bt.indicators.StochasticSlow(self.datas[0], safediv=True, subplot = True)
        self.MACD = bt.indicators.MACDHisto(self.datas[0],subplot = True)
        self.rsi = bt.indicators.RSI(self.datas[0], safediv=True,subplot = True)
        self.smoMA = bt.indicators.SmoothedMovingAverage(self.rsi, period=10,subplot = True)
        self.ATR = bt.indicators.ATR(self.datas[0],subplot = True)
        # self.crossover = bt.ind.CrossOver(ma_fast, ma_slow)

    def positionProfit(self): 
        if self.position: 
            if self.sellprice != -math.inf and self.buyprice != math.inf: 
                profitloss = (((self.sellprice - self.buyprice)/self.buyprice)*100)
                self.fitness += profitloss
                self.positioncount += 1
                if profitloss >= 0: self.wincount += 1
            self.buyprice = math.inf
            self.sellprice = -math.inf

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                # self.log(
                #     'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                #     (order.executed.price,
                #      order.executed.value,
                #      order.executed.comm))

                self.buyprice = order.executed.price
                self.positionProfit()
                # self.buycomm = order.executed.comm
            else:  # Sell
                # self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                #          (order.executed.price,
                #           order.executed.value,
                #           order.executed.comm))
                self.sellprice = order.executed.price
                self.positionProfit()

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            pass
            # self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def closeAtEnd(self): 
        i =  list(range(0, len(self.datas)))
        for (d,j) in zip(self.datas,i):
            if len(d) == (d.buflen()-1):
                close = self.close()
                return True
        return False

    def next(self): 
        if self.closeAtEnd(): return
        input = [
            self.datas[0][0], 
            self.ma_fast[0], 
            self.ma_slow[0], 
            self.expMA[0], 
            self.wtgMA[0], 
            self.stocSlow[0], 
            self.MACD[0], 
            self.rsi[0], 
            self.smoMA[0], 
            self.ATR[0],
            self.buyprice, 
            self.sellprice
            ]
        # input = [self.datas[0][0], self.ma_fast[0], self.ma_slow[0]]
        # input = [self.ma_fast[0], self.ma_slow[0]]
        output = self.brain.think(input)
        # self.broker.cash -= (0.0001 * self.broker.cash)
        # print(f"{input} {output} {self.datas[0][0]}")
        # print(f"{self.broker.cash} {self.position}")
        if not self.position: 
            if output[0] > 0.5: self.order = self.buy()
            elif output[1] > 0.5: self.order = self.sell()
        elif output[2] > 0.5: self.order = self.close()
        