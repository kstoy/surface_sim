import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import catenary as cat
import ball

# from https://www.mygeodesy.id.au/documents/Catenary%20Curve.pdf

# geometry from above
#    h_n 
# /      \
# h_w -  h_e

# constants
P = 20           # number of points per side of the fabric for the visualization part

L  = 4           # side length of fabric in meters
D  = 1           # distance between poles in meters

H_W = 1.0        # height of the three poles west, north, east
H_N = 2.0
H_E = 1.0

ball.set_polar( D/2-0.3, np.pi/6+0.1, 0)

en_curve = cat.findcatenaryparameters( L, D, H_E, H_N )

surfacepoints = cat.calccatenarysurface( L, D, H_N, H_W, H_E, P)
p_r, p_q, p_z = ball.update_polar(L,D, H_W, en_curve)

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
    h_w = H_W + np.sin(n/10)
    h_e = H_E - np.sin(n/10)

    #update surface
    surfacepoints = cat.calccatenarysurface( L, D, h_n, h_w, h_e, P)
    X = surfacepoints[:, [0]].reshape(-1)
    Y = surfacepoints[:, [1]].reshape(-1)
    Z = surfacepoints[:, [2]].reshape(-1)

    ax.clear()
    ax.set_zlim(-1,2)
    #ax.view_init(elev=90, azim=0)
    surfaceplot = ax.plot_trisurf( X, Y, Z )

    #update ball
    en_curve = cat.findcatenaryparameters( L, D, h_e, h_n ) 
    p_r, p_q, p_z = ball.update_polar(L, D, h_w, en_curve)
    ballplot, = ax.plot([p_r*np.cos(p_q)], [p_r*np.sin(p_q)], [p_z], 'ro', markersize = 5, zorder=10)

    return ballplot, surfaceplot

# Create animation
ani = FuncAnimation(fig, animate, frames=200, interval=50, blit=True)

#plt.show()   # for some odd reason the surface does not show, but the ball does
ani.save('demo-w-visualization.gif',fps=10)
