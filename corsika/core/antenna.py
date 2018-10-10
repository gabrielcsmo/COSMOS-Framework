from numpy import sqrt, power

class Antenna():
    def __init__(self, x, y, z, name):
        """
        :param x: in cm
        :param y: in cm
        :param z: in cm
        :param name: unique
        """
        # transform in meters
        self.x = round(float(x)/100, 1)
        self.y = round(float(y)/100, 1)
        self.z = round(float(z)/100, 1)
        self.relevant = False
        self.name = name
        self.cluster_no = -1

    def get_possition(self):
        return [self.x, self.y, self.z]

    def mark_as_relevant(self):
        self.relevant = True

    def is_relevant(self):
        return self.relevant

    def set_cluster(self, cno):
        self.cluster_no = cno

    def get_cluster_no(self):
        return self.cluster_no

    def distance_to(self, ant):
        """

        :param ant: Antenna type
        :return: euclidian_distance(self, ant)
        """
        [x, y, z] = ant.get_possition()
        d = sqrt((self.x - x) * (self.x - x) +
                 (self.y - y) * (self.y - y) +
                 (self.z - z) * (self.z - z))

        return d

    def XOY_distance(self, p):
        [x, y] = p
        return sqrt((self.x - x) * (self.x - x) +
                    (self.y - y) * (self.y - y))

    def to_string(self):
        resstr = 'AntennaPosition = ' + str(self.x) +\
                 ' ' + str(self.y) + ' ' + str(self.z) + ' ' + self.name + '\n'
        return resstr
