#!/usr/bin/env python

import os
import sys
import logging
import math
logging.basicConfig(filename='check.log', level=logging.DEBUG)
"""
   a dict that contains the val
"""
runs = {}
def list_output_folders(folder_path):
    global runs
    content = os.listdir(folder_path)
    for f in content:
        complete_path = os.path.join(folder_path, f)
        if os.path.isdir(complete_path):
            runs[f] = {}
            files = os.listdir(complete_path)
            for _file in files:
                fi = os.path.join(complete_path, _file)
                if "coreas" in _file and os.path.isdir(fi):
                    coreas_files = os.listdir(fi)
                    runs[f]['files'] = []
                    for i in coreas_files: 
                        runs[f]['files'].append(os.path.join(fi,i))

def get_complete_path(l, name):
    for _name in l:
        if _name.endswith(name):
            return _name
    return None

def euclidean_distance(p1, p2):
    if len(p1) != len(p2):
        return None
    sum = 0
    for i in xrange(len(p1)):
        sum += pow((p1[i] - p2[i]), 2)
    return math.sqrt(sum)

def get_pairs(l1, l2):
    res = []
    for item in l1:
        tokens = item.split('/')
        name = tokens[len(tokens) - 1]
        p = get_complete_path(l2, name)
        if p != None:
            res.append((item, p))
    return res
    
def compute_differences(pair):
    file1 = pair[0]
    file2 = pair[1]

    # store tuples of (timestamp_distance, euclidean_distance) for each
    # record in the table
    res = []
    try:
        f = open(file1, 'r')
        g = open(file2, 'r')
    except Exception as e:
        print e
        sys.exit(1)
    f_lines = f.readlines()
    g_lines = g.readlines()
    n = min(len(f_lines), len(g_lines))
    logging.info("Files pair " + str(pair) + " has " \
                 + str(len(f_lines)) + ", " + str(len(g_lines)) \
                 + " number of lines") 
    for i in xrange(n):
        line_one = f_lines[i].strip('\n ').split('\t')
        # timestamp
        t1 = float(line_one[0])
        # north- component
        x1 = float(line_one[1])
        # west- component
        y1 = float(line_one[2])
        # vertical component
        z1 = float(line_one[3]) 
        # compute the modulus
        m1 =  euclidean_distance([x1, y1, z1], [0.0, 0.0, 0.0])

        line_two = g_lines[i].strip('\n ').split('\t')
        # timestamp
        t2 = float(line_two[0])
        # north- component
        x2 = float(line_two[1])
        # west- component
        y2 = float(line_two[2])
        #vertical component
        z2 = float(line_two[3])
        #compute the modulus        
        m2 =  euclidean_distance([x2, y2, z2], [0.0, 0.0, 0.0])

        # average modulus of those two vectors
        m_avg = (m1 + m2) / 2
        # 0 is the value we are expecting for
        timestamp_distance = abs(t1 - t2)
        # if all the euclidian distances between all coresponding pairs are 0
        # it means that our results are the same
        points_distance = euclidean_distance([x1, y1, z1], [x2, y2, z2])
        res.append((timestamp_distance, points_distance, m_avg))
    return res    

def compute_average(l1):
    """
       l1 - list of (delta_t, dist) tuples
    """
    n = len(l1)
    # average time differences
    t_avg = 0
    # average distance
    d_avg = 0
    # average modulus
    m_avg = 0

    for t in l1:
        t_avg += t[0]
        d_avg += t[1]
        m_avg += t[2]
    t_avg /= n
    d_avg /= n
    m_avg /= n
    return (t_avg, d_avg, m_avg)

def main():
    if len(sys.argv) != 2:
        print "Fail. Correct run ./check <results_path>"
        sys.exit(-1)
    # get the content of the folders
    list_output_folders(sys.argv[1])
    # get the relative path of each antena file for each run
    pairs = get_pairs(runs['run1']['files'], runs['run2']['files'])
    # compute difference for each pair
    for pair in pairs:
        #logging.info("Computing diffs for " + str(pair))
        res = compute_differences(pair)
        avg = compute_average(res)
        logging.info("Pair " + str(pair) + " average :\n\t- delta time: " +\
                      str(avg[0]) + "\n\t- distance: " + str((avg[1] * 100 / avg[2])) + "%")
 
if __name__ == '__main__':
    main()
    #print runs
