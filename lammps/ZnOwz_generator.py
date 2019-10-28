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

#from crystal_toolkit import view

def simple_element():
    my_element = Element('Zn')
    my_spec = Specie('Zn', oxidation_state=+2)
    print(my_element.average_ionic_radius)

    print(my_spec)

def simple_zno_molecule():
    my_molecule = Molecule(['Zn', 'O'], [[0.5, sqrt(3) / 2, 0], [0.5, -sqrt(3) / 2, 0]])
    print(my_molecule)
    print(my_molecule.cart_coords)
    print(my_molecule.center_of_mass)
    print(len(my_molecule))

    #site can hold Element, Specie or Composition
    site0 = my_molecule[0]
    print(site0.specie)

def structure_from_file(fname):
    struct = Structure.from_file(fname)
    struct.make_supercell([10, 10, 10])
    struct.to('cif', 'zno-wz_final.dat')
    #print(struct.)
    dumpfn(struct, "ZnO-wz.json")

def main():
    print("python version: {}".format(sys.version))
    print("pymatgen version: {}".format(pymatgen.__version__))

    #simple_element()

    #simple_zno_molecule()

    if len(sys.argv) == 2:
        structure_from_file(sys.argv[1])

if __name__ == '__main__':
    main()