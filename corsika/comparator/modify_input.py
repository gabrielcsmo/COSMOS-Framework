#!/usr/bin/env python
from random import randint, choice
import sys
import os
def check_eq(f1, f2):
    return abs(f1 - f2) <= 1e-20

def modify(filename, r = 5):
    try:
        f = open(filename, 'r')
        wf = open(filename + "_modif", 'w+')
    except Exception as e:
        print e
        sys.exit(1)
    f_lines = f.readlines()
    n = len(f_lines)
    for i in xrange(n):
        line_one = f_lines[i].strip('\n ').split('\t')
        if choice([True, False]):
		wf.write(f_lines[i])
		continue
	# timestamp
        t1 = float(line_one[0]) #+ float(randint(0, r)) / 100
        # north- component
	x1 = float(line_one[1])*(1 + (float(randint(0, r)) / 100))
        # west- component
        y1 = float(line_one[2])*(1 + (float(randint(0, r)) / 100))
        # vertical- component
	z1 = float(line_one[3])*(1 + (float(randint(0, r)) / 100))
	wf.write(str(t1) + "\t" + str(x1) + "\t" + str(y1) + "\t" + str(z1) + "\n")
    f.close()
    wf.close()
    os.system("mv " + filename + "_modif " + filename)
modify(sys.argv[1])
