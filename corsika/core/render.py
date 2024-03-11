
# Author: Gael Varoquaux <gael.varoquaux@normalesup.org>
# Copyright (c) 2008, Enthought, Inc.
# License: BSD Style.

from mayavi import mlab
import numpy as np
from scipy.special import sph_harm

# Create a sphere
r = 25
pi = np.pi
cos = np.cos
sin = np.sin
phi, theta = np.mgrid[0:pi:21j, 0:2 * pi:21j]

x = r * sin(phi) * cos(theta)
y = r * sin(phi) * sin(theta)
z = r * cos(phi)

mlab.figure(1, bgcolor=(1, 1, 1), fgcolor=(0, 0, 0), size=(1920, 1080))
mlab.clf()


def add_sphere(xi, yi, zi, c):
    _s = sph_harm(xi, yi, theta, phi).real
    mlab.mesh(x - xi, y - yi, z - zi, scalars=_s, color=c)

def show():
    
    mlab.view(45, 0, 0, (10, 10, 10))
    #mlab.move( 272.9,  3830.1,   -1451.4)
    #mlab.move(20, 20, 20)
    mlab.show()
    

# Represent spherical harmonics on the surface of the sphere
"""
for i in range(10):
    for j in range(15):
        for k in range(15):
            
            t = (x - k, y - j, z - i, _s, (1,0,0))
            l.append(t)
print("done")

exit(0)
#
"""
 
"""
for n in range(1, 6):
    for m in range(n):
        s = sph_harm(m, n, theta, phi).real

        mlab.mesh(x - m, y - n, z, scalars=s, colormap='jet')

        s[s < 0] *= 0.97

        s /= s.max()
        mlab.mesh(s * x - m, s * y - n, s * z + 1.3,
                  scalars=s, colormap='Spectral')

"""
"""
try:
    mlab.show()
except:
    pass
"""