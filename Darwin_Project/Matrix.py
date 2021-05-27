import pickle
import random
import time
from threading import Thread
import multiprocessing
from datetime import date, datetime, timedelta
import math

import backtrader as bt
import backtrader.analyzers as btanalyze
import matplotlib
from cashier import cache
from utility import constant, util
from tqdm import tqdm

from Agent import Agent
from PolygonData import getData

class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None, spinner = False):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        # print(type(self._target))
        if self._target is not None: 
            self._return = self._target(*self._args, **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return

class Matrix(): 
    """The Matrix is the trading environment. It manages a protfolio of stocks through an array of Bodies. 
    """
    def __init__(self, equityValue=100000, portfolio = []): 
        print("Initializing trading environment...")
        self.equityValue = equityValue
        self.universe = self.getUniverse()
        print(f"Tradeable Asset Count: {len(self.universe)}")
        self.portfolio = portfolio
        self.agents = []
        self.gen = 0

    @cache(cache_time=24*60*60, cache_length=1)
    def getUniverse(self): 
        uni = []
        allStock = util.allStocks()
        uni+=allStock[constant.rating.STRONG_BUY]
        uni+=allStock[constant.rating.BUY]
        uni+=allStock[constant.rating.NEUTRAL]
        uni+=allStock[constant.rating.SELL]
        uni+=allStock[constant.rating.STRONG_SELL]
        for i, x in enumerate(uni): uni[i] = x['symbol']
        return uni

    def generatePortfolio(self): 
        pass

    def training(self, genomes, config): 
        self.agents =[]
        ge = []
        random.seed(datetime.now())

        stocks = random.sample(self.universe, 30)

        fromdate = datetime.today().replace(year=datetime.today().year - 15).date()
        todate = datetime.today().date()
        time_between_dates = todate - fromdate
        days_between_dates = time_between_dates.days
        # random_number_of_days = random.randrange(days_between_dates)
        # random_date = (fromdate + timedelta(days=random_number_of_days)).strftime("%Y-%m-%d")
        dataPaths = [None] * len(stocks)
        returnThreads = []
        msgs=[]
        status=['WORKING...', 'DONE']
        def reprintStatus():
            for i, x in enumerate(dataPaths): 
                if dataPaths[i]!=None and stocks[i] in dataPaths[i]: 
                    msgs[i] = msgs[i].replace(f"{status[0]}",f"{status[1]}")
            lineCount = len(msgs)+1
            erase = f"\033[{lineCount}A"
            clear = '\033[K'
            print(erase) 
            for x in msgs: print(clear+x)
        def checkData(): 
            while None in dataPaths: reprintStatus()
            reprintStatus()
        print(f"Getting {len(stocks)} random stock data...")
        for i, stock in enumerate(stocks): 
            random_number_of_days = random.randrange(days_between_dates)
            random_date = (fromdate + timedelta(days=random_number_of_days)).strftime("%Y-%m-%d")
            text=f"Getting {stock}\t{random_date} data\t[{status[0]}]"
            msgs.append(text)
            t = ThreadWithReturnValue(target=getData, args=(stock, random_date))
            t.start()
            returnThreads.append(t)
        for x in msgs: print(x)
        x = Thread(target=checkData)
        x.start()
        for i, t in enumerate(returnThreads): dataPaths[i] = t.join()
        x.join()

        dataPaths = ['./trainingData/BFST/BFST_2018-04-20.csv', './trainingData/ANGI/ANGI_2012-05-14.csv', './trainingData/ZNTL/ZNTL_2020-04-07.csv', './trainingData/MSFT/MSFT_2009-06-29.csv', './trainingData/CVLB/CVLB_2020-12-29.csv', './trainingData/POOL/POOL_2013-06-26.csv', './trainingData/BAM/BAM_2009-10-20.csv', './trainingData/UNAM/UNAM_2017-01-18.csv', './trainingData/CZZ/CZZ_2011-03-29.csv', './trainingData/CBIO/CBIO_2015-09-18.csv', './trainingData/XFOR/XFOR_2019-04-23.csv', './trainingData/CHNGU/CHNGU_2019-08-05.csv', './trainingData/SPGI/SPGI_2019-07-15.csv', './trainingData/PQG/PQG_2017-10-16.csv', './trainingData/MEG/MEG_2010-04-12.csv', './trainingData/XPO/XPO_2010-05-21.csv', './trainingData/BCOR/BCOR_2012-07-17.csv', './trainingData/USLM/USLM_2009-12-14.csv', './trainingData/YUM/YUM_2010-06-30.csv', './trainingData/OKTA/OKTA_2017-05-04.csv', './trainingData/SJR/SJR_2014-04-03.csv', './trainingData/TTGT/TTGT_2017-01-03.csv', './trainingData/DMAC/DMAC_2018-12-10.csv', './trainingData/KNSA/KNSA_2018-06-14.csv', './trainingData/DORM/DORM_2012-04-18.csv', './trainingData/GILD/GILD_2012-06-06.csv', './trainingData/NWFL/NWFL_2006-09-19.csv', './trainingData/RC/RC_2018-10-10.csv', './trainingData/CPRI/CPRI_2019-01-10.csv', './trainingData/MIME/MIME_2015-11-27.csv']
        
        print("Creating agents...")
        for i in tqdm(range(len(genomes)), colour='blue'): 
            ge.append(genomes[i][1])
            temp = []
            for j in range(len(stocks)): 
                agent = Agent(self.equityValue, stocks[j], dataPaths[j], random_date, genomes[i][1], config)
                temp.append(agent)
            self.agents.append(temp)
        
        print('Trading...')
        pop = len(self.agents)
        s = len(stocks)

        def devidedWork(chunk): 
            for l in chunk: 
                subThreads(l)
            return chunk


        def subThreads(alist): 
            l = alist
            ts = []
            for a in l:  a.start()
            #     t = Thread(target=a.start)
            #     t.start()
            #     ts.append(t)
            # for t in ts: t.join()
            return l

        from pathos.multiprocessing import ProcessingPool as pool
        t0 = time.time()
        c = multiprocessing.cpu_count() * 2 
        chunkSize = -(-len(self.agents) // c)
        print(c)
        p = pool(c) 
        devideAgents = [self.agents[i:i + chunkSize] for i in range(0, len(self.agents), chunkSize)]
        # print(devideAgents[:])
        # result = p.imap(devidedWork, devideAgents)
        result = p.imap(subThreads, self.agents)
        # for i in tqdm(range(pop), colour='blue'): 
        #     for j in tqdm(range(s), colour='red',leave=False): 
        #         t = p.apply_async(self.agents[i][j].start)
        # while not result.ready(): time.sleep(3)
        self.agents = list(result)
        # self.agents = [item for sublist in list(result) for item in sublist]
        p.close()
        p.join()

        # 1 process 1 thread * 15000 : 2217.1058859825134
        # 1 process 30 thread * 500 : 2284.1666662693024
        # 1 process 15000 thread: error
        # (16 pool) 500 process 1 thread * 30: 
        # (16 pool) 500 process 30 thread: 
        # (8 pool) 500 process 1 thread * 30: 1613.284544467926
        # (8 pool) 500 process 30 thread: 
        # (8 pool) 8 process 62~63 thread * 30: 
        # (8 pool) 8 process 1 thread 62~63 *30: 

        # t0 = time.time()
        # # threads=[]
        # for i in tqdm(range(pop), colour='blue'): 
        #     for j in tqdm(range(s), colour='red',leave=False): 
        #         # t = Thread(target=self.agents[i][j].start)
        #         # t.start()
        #         # threads.append(t)
        #         self.agents[i][j].start() 
        # # for t in threads: t.join()
        t1 = time.time()
        print(f"time used: {t1-t0}")
        best = -math.inf
        worst = math.inf
        print('Evaluating...')
        for i, l in enumerate(self.agents): 
            avgFit = 0
            for agent in l:
                avgFit += agent.fitness()
                if agent.finalValue() > best: 
                    best = agent.finalValue()
                    pickle.dump( ge[i], open( "best", "wb" ) )
                if agent.finalValue() < worst: worst = agent.finalValue()
            ge[i].fitness = avgFit/len(l)
        print(f"Generation Best: {best}")
        print(f"Generation Worst: {worst}")
        self.gen += 1

    def train(self): 
        pass

    def start(self): 
        today = datetime.date.today()
        for asset in self.portfolio: 
            self.agents.append(Agent(equityValue/self.portfolio.count, asset, today + datetime.timedelta(days=-today.weekday(), weeks=-10)))
        for agent in self.agents: 
            agent.start()

