import matplotlib.pyplot as plt
import catenarysurface as cat

# from https://www.mygeodesy.id.au/documents/Catenary%20Curve.pdf

# geometry from above - n = north, w = west, e = east
#    h_n 
# /      \
# h_w -  h_e

# constants
P = 20                # number of points per side of the fabric for the visualization part

LF  = 4                # side length factor

D_WN = 1.0         #np.sqrt(2)    # distance between poles in meters
D_NE = 1.0
D_EW = 1.0

H_W = 1.0        # height of the three poles west, north, east
H_N = 2.0
H_E = 0.5


surfacepoints = cat.calccatenarysurface( LF, D_WN, D_NE, D_EW, H_W, H_N, H_E, P)

# Create the plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Set labels
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

X = surfacepoints[:, [0]].reshape(-1)
Y = surfacepoints[:, [1]].reshape(-1)
Z = surfacepoints[:, [2]].reshape(-1)
ax.set_zlim(-1,2)

surfaceplot = ax.plot_trisurf( X, Y, Z )

plt.show()   # for some odd reason the surface does not show, but the ball does
