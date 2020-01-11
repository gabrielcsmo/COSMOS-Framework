"""https://application.wiley-vch.de/books/sample/3527408134_c01.pdf
    Useful: https://www.youtube.com/watch?v=PSsNcvzJAqk&t=682s
    PYMATGEN: http://pymatgen.org/#api-documentation
"""

import pymatgen
import sys
from pymatgen import Molecule
from pymatgen import Element, Specie, Composition
from math import sqrt
from pymatgen import Structure, Lattice
from monty.serialization import dumpfn, loadfn

# measurements are done in nm
CELL_DX = 0.328910293
CELL_DY = 0.328910293
CELL_DZ = 0.530682059

# CELL SIZE
DX = 20
DY = 20
DZ = 100

"""Starting from ZnO wurtzite conventional standard cif
we will create a supercell"""
def create_supercell(fname):
    struct = Structure.from_file(fname)
    print(struct.composition)
    OX_replication = int(DX / CELL_DX)
    OY_replication = int(DY / CELL_DY)
    OZ_replication = int(DZ / CELL_DZ)

    print("Supercell sizes: {} {} {}".format(OX_replication, OY_replication, OZ_replication))

    print("Creating supercell. Please wait, it might take a while")
    struct.make_supercell([OX_replication, OY_replication, OZ_replication])

    print("Dumping ZnO supercell to file")
    struct.to('cif', 'ZnO-supercell.cif')

    return struct

def main():
    print("python version: {}".format(sys.version))
    print("pymatgen version: {}".format(pymatgen.__version__))

    #simple_element()

    #simple_zno_molecule()

    if len(sys.argv) == 2:
        struct = create_supercell(sys.argv[1])
    else:
        print("Usage: python3 {} <cif_file>".format(sys.argv[0]))
        sys.exit(0)

if __name__ == '__main__':
    main()