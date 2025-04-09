import numpy as np
import time
import catenary as cat
import ball

# geometry from above
#    h_n 
# /      \
# h_w -  h_e


H_W = 1.0        # height of the three poles west, north, east
H_N = 2.0
H_E = 1.0

L  = 4           # side length of fabric in meters
D  = 1           # distance between poles in meters


ball.set_polar( D/2-0.3, np.pi/6+0.1, 0)  #initial position of ball
en_curve = cat.findcatenaryparameters( L, D, H_E, H_N )
p_r, p_q, p_z = ball.update_polar(L,D, H_W, en_curve)

start = time.time()

path = []
for step in range(200):  # in ball timestep is 0.1 so this is 20 seconds
    h_n = H_N
    h_w = H_W + np.sin(step/10)
    h_e = H_E - np.sin(step/10)

    #update ball
    en_curve = cat.findcatenaryparameters( L, D, h_e, h_n ) 
    p_r, p_q, p_z = ball.update_polar(L, D, h_w, en_curve)

    path.append( [p_r,p_q,p_z] )

end = time.time()

file = open("demo.dat", "w" )
for entry in path:
    file.write( str( entry[0] ) + " " + str( entry[1] ) + " " + str( entry[2] ) + "\n")
file.close()

print("time elapsed: " + str( end - start ))
