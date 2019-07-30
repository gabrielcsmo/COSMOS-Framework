#!/usr/bin/env python3
import re

"""Based on LAMMPS Data Format: https://lammps.sandia.gov/doc/2001/data_format.html"""
import sys

class LammpsInputFile():

    STYPES = ["Masses", "Nonbond Coeffs", "Bond Coeffs", "Angle Coeffs", "Dihedral Coeffs",
              "Improper Coeffs", "BondBond Coeffs", "BondAngle Coeffs", "MiddleBondTorsion Coeffs",
              "EndBondTorsion Coeffs", "AngleTorsion Coeffs", "AngleAngleTorsion Coeffs", "BondBond13 Coeffs",
              "AngleAngle Coeffs", "Atoms", "Velocities", "Bonds", "Angles", "Dihedrals", "Impropers"]
    def __init__(self, input_fname = ""):
        self.header = { "atoms" : 0,
                        "bonds" : 0,
                        "angles" : 0,
                        "dihedrals" : 0,
                        "impropers" : 0,
                        "atom types" : 0,
                        "bond types" : 0,
                        "angle types" : 0,
                        "dihedral types" : 0,
                        "improper types" : 0,
                      }
        self.box =  {   "xlo xhi" : None,
                        "ylo yhi": None,
                        "zlo zhi": None
                    }

        self.header_keys = self.header.keys()
        self.input_fname = input_fname
        self.input_file = None
        self.lines = []
        self.current_index = -1

        self.masses = []
        self.atoms = []

        """parse the file"""
        self.read_file()

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

    def parse_masses(self):
        N = self.header["atom types"]
        print("Parsing {} Masses starting at line #{}".format(N, self.current_index))

        start = self.current_index + 1
        end = start + N
        for l in self.lines[start:end]:
            tokens = l.split()
            self.masses.append(float(tokens[1]))
        self.current_index = end

    def parse_atoms(self):
        N = self.header["atoms"]
        print("Parsing {} Atoms starting at line #{}".format(N, self.current_index))

        start = self.current_index + 1
        end = start + N
        for l in self.lines[start:end]:
            items = l.split()
            idx = int(items[0])
            tag = int(items[1])
            type = int(items[2])
            q = float(items[3])
            x = float(items[4])
            y = float(items[5])
            z = float(items[6])

            """it means we also have nx ny nz"""
            if len(items) == 10:
                nx = float(items[7])
                ny = float(items[8])
                nz = float(items[9])
                atom = (idx, tag, type, q, x, y, z, nx, ny, nz)
            else:
                atom = (idx, tag, type, q, x, y, z)
            self.atoms.append(atom)
        self.current_index = end

    def parse_velocities(self):
        print("Parsing Velocities starting at line #{}".format(self.current_index))
        self.current_index = len(self.lines)
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

    def parse_header(self):
        for i in range(len(self.lines)):
            sline = self.lines[i].strip()
            goto_next_line = False

            """empty line"""
            if sline == "":
                continue
            """comment"""
            if sline.startswith("#"):
                continue

            for key in self.header_keys:
                if sline.endswith(key):
                    token = sline.strip("\t {}".format(key))
                    self.header[key] = int(token)
                    goto_next_line = True
                    break

            if goto_next_line:
                continue

            if sline.endswith("xlo xhi"):
                tokens = sline.strip(" xlo xhi").split(" ")
                tokens = [i for i in tokens if i != ""]
                print(tokens)
                self.box["xlo xhi"] = (float(tokens[0]), float(tokens[1]))
            elif sline.endswith("ylo yhi"):
                tokens = sline.strip(" ylo yhi").split(" ")
                tokens = [i for i in tokens if i != ""]
                self.box["ylo yhi"] = (float(tokens[0]), float(tokens[1]))
            elif sline.endswith("zlo zhi"):
                tokens = sline.strip(" zlo zhi").split(" ")
                tokens = [i for i in tokens if i != ""]
                self.box["zlo zhi"] = (float(tokens[0]), float(tokens[1]))
            else:
                """It means we got out of header"""
                self.current_index = i
                return

    """Returns the line index for the last data point for this type of coeff
        or -1 if type is unknown. If -1 is returned, ignore until next found type"""
    def decide_what_comes_next(self):
        if self.current_index >= len(self.lines):
            return

        coeff_type = self.lines[self.current_index].split("#")[0].strip()
        if coeff_type not in LammpsInputFile.STYPES:
            print ("Something is wrong in the input file. Unknown type: {}".format(coeff_type))
            return

        method_name = "parse_" + coeff_type.lower().replace(" ", "_")
        method_to_call = getattr(self, method_name)
        method_to_call()
        self.decide_what_comes_next()

    def read_file(self):
        self.input_file = open(self.input_fname)
        """first two lines are ignored"""
        self.lines = self.input_file.readlines()[2:]
        self.lines = [re.sub(' +', ' ', i.strip()) for i in self.lines if i.strip() != ""]
        """parse the header"""
        self.parse_header()

        """See what is coming next in file"""
        self.decide_what_comes_next()

        print("Reading file: Done")

    def __del__(self):
        self.input_file.close()
        print("All cleared!")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: {} <input_file>".format(sys.argv[0]))
        sys.exit(-1)
    l = LammpsInputFile(sys.argv[1])
    print(l.header)
    print(l.masses)
    #print(l.atoms)

