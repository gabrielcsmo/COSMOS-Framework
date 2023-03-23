import os
import random
from itertools import combinations

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

    for a in antennas:
        index = a.get_cluster_tag()
        files[index].write(a.toString())

    for f in files:
        f.close()
