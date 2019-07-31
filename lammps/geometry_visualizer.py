#!/usr/bin/env python3
import sys


try:
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.pyplot as plt
    import numpy as np
except Exception as e:
    print("Failed to import modules required for plot")
    print(e)
    sys.exit(1)

from input_file import LammpsInputFile
from matplotlib import colors as mcolors

#ALL_COLORS = list(mcolors.CSS4_COLORS.keys()) #this contains all colours but it is not looking that good
ALL_COLORS = ["red", "blue", "green", "black", "gray", "magenta", "orange",
              "aqua", "olive", "pink", "plum"]
N = len(ALL_COLORS)
"""
mid = int(N/2)
ATOM_COLORS = ALL_COLORS[:mid]
BOND_COLORS = ALL_COLORS[mid + 1:]
"""

def plot(geometry_obj):
    print(geometry_obj)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    atoms = geometry_obj.get_atoms()
    for atom in atoms:
        if len(atom) == 10:
            (id, tag, type, q, x, y, z, nx, ny, nz) = atom
        else:
            (id, tag, type, q, x, y, z) = atom
        ax.scatter(x, y, z, c=ALL_COLORS[(type - 1) % len(ALL_COLORS)], marker='o')

    bonds = geometry_obj.get_bonds()
    xs = []
    ys = []
    zs = []


    for bond in bonds:
        (idx, type, aidx1, aidx2) = bond

        atom1 = atoms[aidx1 - 1]
        if len(atom1) == 10:
            (_, _, _, _, x1, y1, z1, _, _, _) = atom1
        else:
            (_, _, _, _, x1, y1, z1) = atom1
        xs.append(x1)
        ys.append(y1)
        zs.append(z1)

        atom2 = atoms[aidx2 - 1]
        if len(atom2) == 10:
            (_, _, _, _, x2, y2, z2, _, _, _) = atom2
        else:
            (_, _, _, _, x2, y2, z2) = atom2
        xs.append(x2)
        ys.append(y2)
        zs.append(z2)

    plt.axis('off')
    plt.plot(xs, ys, zs, "green")

    plt.show()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: {} <desc_file>".format(sys.argv[0]))
        sys.exit(-1)
    l = LammpsInputFile(sys.argv[1])
    plot(l)
