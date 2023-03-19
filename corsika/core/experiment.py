from os import listdir
from os.path import isfile, join, abspath
import sys
from core.antenna import Antenna
import re
import numpy as np
import random

class Experiment():

    def __init__(self, input_folder):
        self.folder = input_folder
        self.files = {"reas" : None, "list" : None, "inp" : None}
        self.reas_dict_params = {}
        self.inp_dict_params = {}
        self.convert_exceptions = ["Comment", "CorsikaFilePath",
                                   "CorsikaParameterFile"]
        self.antennas = []
        self.par_dir_vec = None
        self.par_coord = None

        # get absolute path for experiment config files
        self.find_input_files()
        # read list file
        self.read_list_file()
        # read reas file
        self.read_reas_file()
        # read the input file
        self.read_inp_file()
        self.__set_par_coordinates()
        self.__set_direction_vector()
        self.__set_direction_points()

    def find_input_files(self):
        self.folder = abspath(self.folder)
        content = listdir(self.folder)
        # search for .reas / .inp / .list files
        for f in content:
            full_path = join(self.folder, f)
            if not isfile(full_path):
                continue
            # search for dict keys to find proper files
            for key in self.files:
                if full_path.endswith(key):
                    self.files[key] = full_path
                    break

    def read_list_file(self):
        """
            Experiment cannot be done without a
            the file that contains antennas positions
        """
        filename = self.files["list"]
        if not filename:
            print(".list file is missing. Exiting  now.")
            sys.exit(1)
        with open(filename) as f:
            lines = f.readlines()
            for line in lines:
                tokens = line.split('=')
                if tokens[0] == 'AntennaPosition ':
                    l = tokens[1].strip(' \n')
                    [x, y, z, name] = l.split(' ')
                    self.antennas.append(Antenna(float(x),
                                                 float(y),
                                                 float(z),
                                                 name))

    def exit_if_missing_tokens(self, tokens, expected_tokens):
        if len(tokens) != expected_tokens:
            print("Got {} tokens. Expected {}. Exiting now."\
                .format(len(tokens), expected_tokens))
            sys.exit(1)

    def parse_inp_line(self, string):
        tokens = string.split(" ")
        key = tokens[0]
        if key in ["RUNNR", "EVTNR", "NSHOW", "PRMPAR",
                   "OBSLEV", "MAXPRT", "ATMOD"]:
            self.exit_if_missing_tokens(tokens, 2)
            self.inp_dict_params[key] = int(tokens[1])
        elif key in ["ERANGE", "THETAP", "PHIP", "MAGNET"]:
            self.exit_if_missing_tokens(tokens, 3)
            self.inp_dict_params[key] = [float(i) for i in tokens[1:]]
        elif key == "SEED":
            self.exit_if_missing_tokens(tokens, 4)
            seed_tup = [int(i) for i in tokens[1:]]
            if key not in self.inp_dict_params:
                self.inp_dict_params[key] = [seed_tup]
            else:
                self.inp_dict_params[key].append(seed_tup)
        elif key in ["ECUTS", "THINH", "ECTMAP", "STEPFC", "RADNKG"]:
            energies = [float(i) for i in tokens[1:]]
            self.inp_dict_params[key] = energies
        elif key in ["ELMFLG", "MUADDI", "MUMULT", "PAROUT",
                     "LONGI", "DIRECT", "DATBAS", "USER"]:
            self.inp_dict_params[key] = tokens[1:]
        elif key == "THIN":
            self.exit_if_missing_tokens(tokens, 4)
            self.inp_dict_params[key] = [float(i) for i in tokens[1:]]
        elif key == "EXIT":
            self.inp_dict_params[key] = True
        else:
            print ("No Case for {}".format(key))

    def read_inp_file(self):
        """
        Parse the inp file
        :return:
        """
        filename = self.files["inp"]
        if not filename:
            print (".inp file is missing. Exiting now.")
            sys.exit(1)
        with open(filename) as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip().replace("\t", " ")
                line = re.sub(" +", " ", line)
                self.parse_inp_line(line)

    def read_reas_file(self):
        """
        Parse the reas file and save the content into a
        dict.
        :return:
        """
        filename = self.files["reas"]
        if not filename:
            print (".reas file is missing. Exiting now.")
            sys.exit(1)
        with open(filename) as f:
            lines = f.readlines()
            for line in lines:
                """ignore empty lines and comments"""
                if line.startswith("#") or line.startswith("\n"):
                    continue
                line = line.strip()
                [key, value] = line.split("=")
                """The format is k = v ; comment"""
                tokens = value.strip().split(";")
                k = key.strip()
                """Most of the params are floas so we are
                converting to float all the params that are
                not in the exception list (initialized in constructor
                """
                if k not in self.convert_exceptions:
                    v = float(tokens[0].strip())
                else:
                    v = tokens[0].strip()
                self.reas_dict_params[k] = v

    def to_string(self):
        retstr = "Folder:\t" + self.folder
        retstr += "\nFiles:"
        for k in self.files:
            retstr += "\n\t" + k + ": " + str(self.files[k])

        """Print the Antennas file"""
        retstr += "\nAntennas:\n"
        for a in self.antennas:
            retstr += "\t" + a.to_string()

        """Print the REAS file"""
        retstr += "\nREAS FILE:\n"
        for k in self.reas_dict_params:
            retstr += "\t" + k + " = "\
                      + str(self.reas_dict_params[k]) + "\n"

        """Print the INP file"""
        retstr += "\nINP FILE:\n"
        for k in self.inp_dict_params:
            retstr += "\t" + k + " = " \
                      + str(self.inp_dict_params[k]) + "\n"
        return retstr

    def __set_direction_vector(self):
        theta = self.inp_dict_params["THETAP"][0]
        phi = self.inp_dict_params["PHIP"][0]
        [dx, dy, dz] = [np.cos(theta) * np.cos(phi),
                            np.cos(theta) * np.sin(phi),
                            - np.sin(theta)]
        self.par_dir_vec = [dx/np.abs(dz), dy/np.abs(dz), dz / np.abs(dz)]
        #print "Direction vector: {}".format(self.par_dir_vec)

    def __set_par_coordinates(self):
        """Add particle initial position"""
        x = round(self.reas_dict_params["CoreCoordinateWest"] / 100 , 1)
        y = round(self.reas_dict_params["CoreCoordinateNorth"] / 100 , 1)
        z = round(self.reas_dict_params["CoreCoordinateVertical"] / 100 , 1)
        self.par_coord = [x, y, z]

    def mark_relevant_antennas(self):
        print (self.steps)
        """initial radius"""
        a1 = random.choice(self.antennas)
        a2 = random.choice(self.antennas)
        while a1 == a2:
            a2 = random.choice(self.antennas)
        """
        r_min = a1.distance_to(a2)
        r_max = a2.distance_to(a2)

        #get the min and max distance
        for a2 in self.antennas:
            if a1 == a2:
                continue
            r = a1.distance_to(a2)
            #print a1.get_possition(), a2.get_possition(), r
            if r < r_min and r > 1.0:
                r_min = r
            if r > r_max:
                r_max = r

        #set the initial radius 2 x
        r_start = 2 * r_min
        r_end = r_max / 3
        r_step = (r_end - r_start) / self.steps
        """
        r_start = 300
        r_step = 0

        for i in range(len(self.par_dir_points)):
            """get the point that corresponds to step i
            computed as Point0 + i * dirVect
            """
            [x0, y0, z] =  self.par_dir_points[i]
            r = r_start + r_step * i
            for antenna in self.antennas:
                d = antenna.XOY_distance([x0, y0])
                if d < r:
                    antenna.mark_as_relevant()


    def __set_direction_points(self):
        """Do the computation until we have the intersection
           with OX plane
        """
        [x, y, z] = self.par_coord
        [dx, dy, dz] = self.par_dir_vec
        zmin = self.antennas[0].get_possition()[2] # get first antenna z
        for antenna in self.antennas[1:]:
            [xp, yp, zp] = antenna.get_possition()
            if zp < zmin:
                zp = zmin
        self.steps = int(np.ceil(np.abs((z - zmin)/dz)))
        self.par_dir_points = [self.par_coord]
        end_p = self.par_dir_points[-1]
        for i in range(self.steps):
            P = [x + i * dx, y + i * dy, z + i * dz]
            self.par_dir_points.append(P)

    def plot(self):
        try:
            from mpl_toolkits.mplot3d import Axes3D
            import matplotlib.pyplot as plt
            import numpy as np
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            for antenna in self.antennas:
                [x, y, z] = antenna.get_possition()
                colour = 'r'
                if antenna.is_relevant():
                    colour = 'g'
                ax.scatter(x, y, z, c=colour, marker='o')
            """start coordinates"""
            [xs, ys, zs] = self.par_coord
            """end coordinats"""
            [xe, ye, ze] = self.par_dir_points[-1]
            """step"""
            x = np.linspace(xs, xe, 100)
            y = np.linspace(ys, ye, 100)
            z = np.linspace(zs, ze, 100)
            ax.scatter(x, y, z)

            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            plt.show()
        except Exception as e:
            print ("Failed to plot Antennas")
            print (e)
            sys.exit(1)
