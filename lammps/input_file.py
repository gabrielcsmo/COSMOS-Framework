#!/usr/bin/env python3

"""Based on LAMMPS Data Format: https://lammps.sandia.gov/doc/2001/data_format.html"""
import sys

class LammpsInputFile():

    STYPES = ["Masses", "Nonbond Coeffs", "Bond Coeffs", "Angle Coeffs", "Dihedral Coeffs",
              "Improper Coeffs", "BondBond Coeffs", "BondAngle Coeffs", "MiddleBondTorsion Coeffs",
              "EndBondTorsion Coeffs", "AngleTorsion Coeffs", "AngleAngleTorsion Coeffs", "BondBond13 Coeffs",
              "AngleAngle Coeffs", "Atoms", "Velocities", "Bonds", "Angles", "Dihedrals", "Impropers"]
    def __init__(self, input_fname = ""):
        self.parameters = { "atoms" : 0,
                            "bonds" : 0,
                            "angles" : 0,
                            "dihedrals" : 0,
                            "impropers" : 0,
                            "atom types" : 0,
                            "bond types" : 0,
                            "angle types" : 0,
                            "dihedral types" : 0,
                            "improper types" : 0,
                            "xhi" : (0, 0),
                            "yhi": (0, 0),
                            "zhi": (0, 0)
                          }

        self.input_fname = input_fname
        self.input_file = None
        self.lines = []
        self.current_index = -1

        """parse the file"""
        self.read_file()

    def parse_masses(self):
        pass
    def parse_nonbond_coeffs(self):
        pass
    def parse_bond_coeffs(self):
        pass
    def parse_angle_coeffs(self):
        pass
    def parse_dihedral_coeffs(self):
        pass
    def parse_improper_coeffs(self):
        pass
    def parse_bondbond_coeffs(self):
        pass
    def parse_bondangle_coeffs(self):
        pass
    def parse_middlebondtorsion_coeffs(self):
        pass
    def parse_endbondtorsion_coeffs(self):
        pass
    def parse_angletorsion_coeffs(self):
        pass
    def parse_angleangletorsion_coeffs(self):
        pass
    def parse_bondbond13_coeffs(self):
        pass
    def parse_angleangle_coeffs(self):
        pass

    def parse_atoms(self):
        print("Parsing Atoms starting at line #{}".format(self.current_index))
        pass
    def parse_velocities(self):
        print("Parsing Velocities starting at line #{}".format(self.current_index))
        pass
    def parse_bonds(self):
        print("Parsing Bonds starting at line #{}".format(self.current_index))
        pass
    def parse_angles(self):
        print("Parsing Angles starting at line #{}".format(self.current_index))
        pass
    def parse_dihedrals(self):
        print("Parsing Dihedrals starting at line #{}".format(self.current_index))
        pass
    def parse_impropers(self):
        print("Parsing Impropers starting at line #{}".format(self.current_index))
        pass

    """Returns the line index for the last data point for this type of coeff
        or -1 if type is unknown. If -1 is returned, ignore until next found type"""
    def decide_what_comes_next(self, coeff_type, index):
        if coeff_type not in LammpsInputFile.STYPES:
            print ("Something is wrong in the input file. Unknown type: {}".format(coeff_type))
            return -1

        method_name = "parse_" + coeff_type.lower().replace(" ", "_")
        method_to_call = getattr(self, method_name)
        self.current_index = index
        method_to_call()

        return index


    def read_file(self):
        self.input_file = open(self.input_fname)
        """first two lines are ignored"""
        self.lines = self.input_file.readlines()[2:]
        for i in range(len(self.lines)):
            sline = self.lines[i].strip()
            """empty line"""
            if sline == "":
                continue

            """comment"""
            if sline.startswith("#"):
                continue

            tokens = sline.split()
            """it is one of <Atoms, Velocities, Bonds, Angles, Dihedrals, Impropers>"""
            if len(tokens) == 1:
                self.decide_what_comes_next(sline, i)

            continue


        print("Reading file: Done")

    def __del__(self):
        self.input_file.close()
        print("All cleared!")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: {} <input_file>".format(sys.argv[0]))
        sys.exit(-1)
    l = LammpsInputFile(sys.argv[1])
    print(l.parameters)

