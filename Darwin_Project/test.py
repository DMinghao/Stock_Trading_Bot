import os
import visualize
import neat
from datetime import date, datetime, timedelta
import pickle 
from utility import util

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