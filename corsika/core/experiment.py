from os import listdir
from os.path import isfile, join, abspath, expanduser, basename
import sys
from core.antenna import Antenna
import re
import numpy as np
import random
from core.lloyd_kmeans import find_centers, cluster_points
from core.utils import generate_colors, write_files


class Experiment():

    def __init__(self, args):
        self.args = args
        self.folder = expanduser(args.input)
        self.verbose = args.verbose

        self.files = {"reas" : None, "list" : None, "inp" : None}
        self.reas_dict_params = {}
        self.inp_dict_params = {}
        self.convert_exceptions = ["Comment", "CorsikaFilePath",
                                   "CorsikaParameterFile"]
        self.antennas = []
        self.par_dir_vec = None
        self.par_coord = None
        self.max_distance = 100

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
        self.xmin = 100000000.0
        self.xmax = -100000000.0
        self.ymin = 100000000.0
        self.ymax = -100000000.0
        self.zmin = 100000000.0
        self.zmax = -100000000.0

        if args.num_clusters:
            self.colors = generate_colors(args.num_clusters)
        else:
            self.colors = generate_colors(10)

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
        if self.args.verbose:
            print(f"Direction vector: {self.par_dir_vec}")

    def __set_par_coordinates(self):
        """Add particle initial position"""
        x = round(self.reas_dict_params["CoreCoordinateWest"] / 100 , 1)
        y = round(self.reas_dict_params["CoreCoordinateNorth"] / 100 , 1)
        z = round(self.reas_dict_params["CoreCoordinateVertical"] / 100 , 1)
        self.max_distance = round(self.reas_dict_params["DistanceOfShowerMaximum"] / 100 , 1)
        self.par_coord = [x, y, z]

    def get_sim_box_limits(self):
        for antenna in self.antennas:
                [x, y, z] = antenna.get_position()
                if x < self.xmin:
                    self.xmin = x
                elif x > self.xmax:
                    self.xmax = x

                if y < self.ymin:
                    self.ymin = y
                elif y > self.ymax:
                    self.ymax = y

                if z < self.zmin:
                    self.zmin = z
                elif z > self.zmax:
                    self.zmax = z

    def mark_relevant_antennas(self):
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
            #print a1.get_position(), a2.get_position(), r
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
        dir_vect_magnitude = np.linalg.norm(self.par_dir_vec)
        if self.args.verbose:
            print(f"Direction vector magnitude: {dir_vect_magnitude}")

        self.steps = int(self.max_distance/dir_vect_magnitude) # int(np.ceil(np.abs((z - zmin)/dz)))
        self.par_dir_points = [self.par_coord]
        end_p = self.par_dir_points[-1]
        for i in range(self.steps):
            P = [x + i * dx, y + i * dy, z + i * dz]
            self.par_dir_points.append(P)
        if self.verbose:
            print(f"Primary particle:\n\tdiscretization steps = {self.steps}")
            print(f"\tstart position {self.par_dir_points[0]}")
            print(f"\tend position   {self.par_dir_points[-1]}")

    def set_clusters(self, position, cluster_tag):
        x = int(position[0])
        y = int(position[1])
        for a in self.antennas:
            ax = int(a.x)
            ay = int(a.y)
            if x == ax and y == ay:
                if self.args.verbose:
                    print("set tag %s on antena %s" %(cluster_tag, a))
                a.set_cluster_tag(cluster_tag)
                return

    def sort_antennas_by_x_pos(self):
        self.antennas = sorted(self.antennas, key=lambda a: a.x)

    def plot_antennas_2D(self):
        # skip plotting if --no-plot was used
        if self.args.no_plot:
            return

        import matplotlib.pyplot as pl

        for a in self.antennas:
            index = a.get_cluster_tag()
            if self.args.only_relevant and not a.is_relevant():
                continue
            pl.plot([a.x], [a.y],
                        color=self.colors[index], marker='o')
        pl.show()

    def cluster_antennas(self):
        self.sort_antennas_by_x_pos()
        if self.args.only_relevant:
            points = np.array([a.get_position() for a in self.antennas if a.is_relevant()])
        else:
            points = np.array([a.get_position() for a in self.antennas])
        centers = find_centers(points, self.args.num_clusters)
        clusters_dict = cluster_points(points, centers[0])
        for key in clusters_dict:
            for val in clusters_dict[key]:
                self.set_clusters([val[0], val[1]], key)
        write_files(basename(self.files["list"]), self.antennas, len(clusters_dict))
        
        if self.args.use_vispy:
            self.plot_vispy(True)
        else:
            self.plot_antennas_2D()


    def plot(self):
        # skip plotting if --no-plot was used
        if self.args.no_plot:
            return
        try:
            from mpl_toolkits.mplot3d import Axes3D
            import matplotlib.pyplot as plt
            import numpy as np
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            if(self.verbose):
                print("Antennas list:")
            for antenna in self.antennas:
                [x, y, z] = antenna.get_position()
                c = [0.5, 0, 0]
                if antenna.is_relevant():
                    c = [0, 0.7, 0]
                ax.scatter(x, y, z, color=c, marker='o')

                if (self.verbose):
                    print("\t" + str(antenna))

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

    def plot_maya(self):
        # skip plotting if --no-plot was used
        if self.args.no_plot:
            return
        try:
            from core.render import add_sphere, show
            RED = (1, 0, 0)
            GREEN = (0, 1, 0)
            for antenna in self.antennas:
                [x, y, z] = antenna.get_position()
                colour = RED
                if antenna.is_relevant():
                    colour = GREEN
                if (self.verbose):
                    print("\t" + str(antenna))

                add_sphere(x, y , z ,colour)
            for x,y,z in self.par_dir_points:
                add_sphere(x, y , z , (0,0,1))

            show()
        except:
            print("Cannot plot using MayaVI")        

    def plot_vispy(self, plot_cluster = False):
            # skip plotting if --no-plot was used
            if self.args.no_plot:
                return

            from vispy import scene
            from vispy.visuals.transforms import STTransform

            canvas = scene.SceneCanvas(keys='interactive', bgcolor='white',
                                       size=(800, 600), show=True)
            view = canvas.central_widget.add_view()
            view.camera = 'arcball'

            for antenna in self.antennas:
                if self.args.only_relevant and not antenna.is_relevant():
                    continue
                pos=antenna.get_position()
                c = 'red'
                if plot_cluster:
                    index = antenna.get_cluster_tag()
                    c = self.colors[index]
                elif antenna.is_relevant():
                    c = 'green'
                _s = scene.visuals.Sphere(color=c, radius=35, method='latitude', parent=view.scene)
                _s.transform = STTransform(translate=pos)

            for pos in self.par_dir_points:
                
                _s = scene.visuals.Sphere(color ='blue',
                                     radius=10, method='latitude', parent=view.scene)
                _s.transform = STTransform(translate=pos)

            self.get_sim_box_limits()

            view.camera.set_range(x=[self.xmin, self.xmax],
                                  y=[self.ymin, self.ymax],
                                  z = [self.zmin, self.zmax])
            canvas.app.run()
