"""https://application.wiley-vch.de/books/sample/3527408134_c01.pdf"""

import pymatgen
import sys
from pymatgen import Molecule
from math import sqrt

from crystal_toolkit import view

def main():
    print("python version: {}".format(sys.version))
    print("pymatgen version: {}".format(pymatgen.__version__))
    my_molecule = Molecule(['Zn', 'O'], [[0.5, sqrt(3)/2, 0], [0.5, -sqrt(3)/2, 0]])
    print(my_molecule)
    view(my_molecule)

if __name__ == '__main__':
    main()