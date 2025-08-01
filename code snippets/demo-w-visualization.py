import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import catenarysurface as cat
import ball

# from https://www.mygeodesy.id.au/documents/Catenary%20Curve.pdf

# geometry from above
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
H_E = 1.0

ball.set_polar( D_EW/2-0.3, np.pi/6+0.1, 0)  #initial position of ball

surfacepoints = cat.calccatenarysurface( LF, D_WN, D_NE, D_EW, H_W, H_N, H_E, P)
p_r, p_q, p_z = ball.update_polar(LF, D_WN, D_NE, D_EW, H_N, H_W, H_E )

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
#ax.view_init(elev=0, azim=0)

surfaceplot = ax.plot_trisurf( X, Y, Z )
ballplot, = ax.plot([p_r*np.cos(p_q)], [p_r*np.sin(p_q)], [p_z], 'ro', markersize = 5, zorder=10)

# Function to update the plot for animation
def animate(n):
    global ballplot, surfaceplot
    h_n = H_N
    h_w = H_W - n/150*np.sin(n/10)
    h_e = H_E + n/150*np.sin(n/10)

    #update surface
    surfacepoints = cat.calccatenarysurface(  LF, D_WN, D_NE, D_EW, h_w, h_n, h_e, P)
    X = surfacepoints[:, [0]].reshape(-1)
    Y = surfacepoints[:, [1]].reshape(-1)
    Z = surfacepoints[:, [2]].reshape(-1)

    ax.clear()
    ax.set_zlim(-1,2)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    #ax.view_init(elev=90, azim=0)
    surfaceplot = ax.plot_trisurf( X, Y, Z )

    #update ball
    p_r, p_q, p_z = ball.update_polar( LF, D_WN, D_NE, D_EW, h_w, h_n, h_e )
    ballplot, = ax.plot([p_r*np.cos(p_q)], [p_r*np.sin(p_q)], [p_z], 'ro', markersize = 5, zorder=10)

    return ballplot, surfaceplot

# Create animation
ani = FuncAnimation(fig, animate, frames=150, interval=50, blit=True)

#plt.show()   # for some odd reason the surface does not show, but the ball does
ani.save('demo-w-visualization.mp4',fps=10)
