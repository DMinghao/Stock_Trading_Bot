import os 
import neat 
from utility import util
import pickle
import visualize
import threading
import glob

class GA(): 
    def run(self, train, livePlot = False): 
        if livePlot:
            plot = threading.Thread(target=self.livePlot)
            plot.start()
        self.best = self.p.run(train, self.maxGen)
        if livePlot: plot.join()
        return self.best

    def saveBest(self): 
        pickle.dump( self.best, open( "save.p", "wb" ) )

    def loadBest(self): 
        return pickle.load( open( "save.p", "rb" ) )

    def visualize(self, geno=None, net = False): 
        plotPath = '/plots'
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
        if net: visualize.draw_net(self.config, geno, view=True, node_names=nodeNames, filename=f'{plotPath}/net.dot')
        visualize.plot_stats(self.stats, ylog=False, view=True, filename=f'{plotPath}/avg_fitness.svg')
        visualize.plot_species(self.stats, view=True, filename=f'{plotPath}/speciation.svg')

    def livePlot(self): 
        visualize.live_plot(self)

    def liveSpecies(self): 
        visualize.live_plot_species(self)

    def __init__(self, maxGen = 300, checkpoint = None): 
        self.maxGen = maxGen
        self.config_path = os.path.join(util.getProjectDir(), r"config\NEATconfig.txt")
        self.config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                            neat.DefaultSpeciesSet, neat.DefaultStagnation,
                            self.config_path)
        if checkpoint: 
            cp = 0
            for root, dirs, files in os.walk("./checkpoints"):
                files = list(map(lambda x: int(x.split('-')[2]), files))
                files.sort(reverse = True) 
                cp = files[0]
            print(f'Starting from checkpoint: {cp}')
            self.p = neat.Checkpointer.restore_checkpoint(f'./checkpoints/neat-checkpoint-{cp}')
        else: self.p = neat.Population(self.config)
        self.p.add_reporter(neat.StdOutReporter(True))
        self.stats = neat.StatisticsReporter()
        self.p.add_reporter(self.stats)
        self.p.add_reporter(neat.Checkpointer(generation_interval=1, time_interval_seconds=600, filename_prefix=f'./checkpoints/neat-checkpoint-'))

if __name__ == "__main__": 
    from Matrix import Matrix
    import sys
    fromCheckpoint = False
    if len(sys.argv)>1 and sys.argv[1] == '-cp': ga = GA(checkpoint = True)
    elif len(sys.argv)>1 and sys.argv[1] == '-new': 
        for f in glob.glob('./checkpoints'): os.remove(f)
    else: ga = GA()
    mtrx = Matrix()
    winner = ga.run(mtrx.training, False)
    ga.visualize(geno=winner, net = True)
