from core.antenna import Antenna
from core.experiment import Experiment
import sys
import argparse

parser = argparse.ArgumentParser(description="CORSIKA Optimizer Headless")
parser.add_argument('--input', action = "store", help = "Input Folder",
                    type = str, required = True)
parser.add_argument('-v', '--verbose', help = "Enable verbose", action='store_true')

if __name__ == '__main__':
    args = parser.parse_args()

    e = Experiment(args)
    e.mark_relevant_antennas()
    #e.plot()
    #e.plot_maya()
    e.plot_vispy()