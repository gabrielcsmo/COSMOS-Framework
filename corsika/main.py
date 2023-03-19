from core.antenna import Antenna
from core.experiment import Experiment
import sys

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(sys.argv[0], "<folder>")
        sys.exit(1)

    e = Experiment(sys.argv[1])
    #print e.to_string()
    e.mark_relevant_antennas()
    e.plot()
