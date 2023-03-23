from core.antenna import Antenna
from core.experiment import Experiment
import sys
import argparse
from core.utils import generate_colors

parser = argparse.ArgumentParser(description="CORSIKA Optimizer Headless")
parser.add_argument('--input', action = "store", type = str, required = True,
                    help = "Input Folder")
parser.add_argument('-v', '--verbose', action='store_true',
                    help = "Enable verbose")
parser.add_argument('-c', '--cluster', action='store_true',
                    help = "Enable clustering the antennas")
parser.add_argument('-n', '--num-clusters', action = "store", type = int,
                    help = "Number of antenna clusters")
parser.add_argument('--use-vispy', action='store_true',
                    help = "Enable ploting with VisPY")
parser.add_argument('--only-relevant', action='store_true',
                    help = "Enable ploting with VisPY")


if __name__ == '__main__':
    args = parser.parse_args()

    e = Experiment(args)
    e.mark_relevant_antennas()

    if args.use_vispy:
        e.plot_vispy()
    else:
        e.plot()
    
    if args.cluster:
        if not args.num_clusters:
            print("Warning: \"-n <value>\" is required if clustering is enabled.")
            sys.exit(0)
        e.cluster_antennas()
    
    #e.plot_maya()
    #e.plot_vispy()