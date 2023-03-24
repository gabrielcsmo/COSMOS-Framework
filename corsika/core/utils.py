import os
import random
from itertools import combinations
from os.path import basename

def generate_colors(num):
    total = (num // 3) + 1
    step = 1 / total
    l = []
    for i in range(total + 1):
        l.append([round(i * step, 2), 0, 0])
        l.append([0, 0, round(i * step, 2)])
        l.append([0, round(i * step, 2), 0])
 
    #l = list(combinations(l, 3))
    random.shuffle(l)
    return l

def write_files(filename, antennas, no_clusters):
    files = []
    for i in range(no_clusters):
        folder = 'run' + str(i)
        os.system('rm -rf ' + folder)
        os.system('mkdir ' + folder)
        files.append(open(os.path.join(folder, filename), 'w+'))

    # create a special folder for antennas without tag
    # index = -2
    folder = "run-not-relevant"
    os.system('rm -rf ' + folder)
    os.system('mkdir ' + folder)
    files.append(open(os.path.join(folder, filename), 'w+'))

    # create a special folder for antennas that are important
    # index = -1
    folder = "run-relevant"
    os.system('rm -rf ' + folder)
    os.system('mkdir ' + folder)
    files.append(open(os.path.join(folder, filename), 'w+'))


    for a in antennas:
        index = a.get_cluster_tag()

        # if index < 0, it means the antenna is unclustered
        # second-last file is run-not-relevant and last file is run-relevant
        if a.is_relevant():
            files[-1].write(a.toString())
        else:
            files[-2].write(a.toString())

        if index >= 0:
            files[index].write(a.toString())

    for f in files:
        f.close()
