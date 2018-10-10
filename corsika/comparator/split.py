#!/usr/bin/env python

import sys
import numpy as np
import matplotlib.pyplot as pl
from corsika.comparator.lib.utils import read_file, write_files
observers = []
from Lloyd_kmeans import find_centers, cluster_points
colors = ['r', 'b', 'g', 'm', 'c', 'y', 'k']
shapes = ['D', 'p', '*', 'H', '+', 's', 'x']
avail_colors = len(colors)

def set_clusters(pos, cno, antennas):
    x = int(pos[0])
    y = int(pos[1])
    for a in antennas:
        ax = int(a.x)
        ay = int(a.y)
        if x == ax and y == ay:
            a.set_cluster(cno)
            return

def sort_antennas(alist):
    res = sorted(alist, key=lambda a: a.x)
    #for a in res:
    #    a.toString()
    return res

def plot_antennas(antennas):
    global colors, avail_colors, shapes
    x = []
    y = []
    for a in antennas:
        index = a.get_cluster_no() % avail_colors
        code = colors[index] + shapes[index]
        pl.plot([a.x], [a.y], code)
    pl.show()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "Usage: split.py <filename> <res_filename>"
        sys.exit(1)
    observers = read_file(sys.argv[1])
    ant = sort_antennas(observers)
    points = np.array([a.getPos() for a in ant])
    centers = find_centers(points, 4)
    clusters_dict = cluster_points(points, centers[0])
    no_clusters = len(clusters_dict)
    print "We found the following clusters: "
    for key in clusters_dict:
        print "Cluster no", key
        for val in clusters_dict[key]:
            set_clusters([val[0], val[1]], key, ant)
    write_files(sys.argv[2], ant, no_clusters)
    plot_antennas(ant)
