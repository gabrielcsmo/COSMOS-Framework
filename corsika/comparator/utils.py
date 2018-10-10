import sys, os

class Antenna():
    def __init__(self, x, y, z, name):
        """
        :param x: in cm
        :param y: in cm
        :param z: in cm
        :param name: unique
        """
        # transform in meters
        self.x = x # int(x / 100)
        self.y = y # int(y / 100)
        self.z = z # int(z / 100)
        self.name = name
        self.cluster_no = -1

    def toString(self):
        #print 'Antenna:', self.name, '\tCoordinates:', self.x, self.y, self.z
        #print '(', self.x, ', ', self.y , ')'
        resstr = 'AntennaPosition = ' + str(self.x) +\
                 ' ' + str(self.y) + ' ' + str(self.z) + ' ' + self.name + '\n'
        return resstr

    def getPos(self):
        return [self.x, self.y, self.z]

    def set_cluster(self, cno):
        self.cluster_no = cno

    def get_cluster_no(self):
        return self.cluster_no

def read_file(filename):
    f = open(filename)
    lines = f.readlines()
    observers = []
    for line in lines:
        tokens = line.split('=')
        if tokens[0] == 'AntennaPosition ':
            l = tokens[1].strip(' \n')
            [x, y, z, name] = l.split(' ')
            observers.append(Antenna(float(x), float(y), float(z), name))
    return observers

def write_files(filename, antennas, no_clusters):
    files = []
    for i in xrange(no_clusters):
        folder = 'run' + str(i)
        os.system('rm -rf ' + folder)
        os.system('mkdir ' + folder)
        files.append(open(os.path.join(folder, filename), 'w+'))

    for a in antennas:
        index = a.get_cluster_no()
        print a.toString()
        files[index].write(a.toString())

    for f in files:
        f.close()

