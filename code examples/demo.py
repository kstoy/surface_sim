import numpy as np
import time
import ball

# geometry from above
#    h_n 
# /      \
# h_w -  h_e


H_W = 1.0          # height of the three poles west, north, east
H_N = 2.0
H_E = 1.0

D_WN = 1.0         # distance between poles in meters
D_NE = 1.0
D_EW = 1.0       

LF = 4             # side length fabric factor (e.g. 1 means the fabric is equal to distance, 4 that there is four times more)

ball.set_polar( D_EW/2-0.3, np.pi/6+0.1, 0)  #initial position of ball
p_r, p_q, p_z = ball.update_polar(LF, D_WN, D_NE, D_EW, H_W, H_N, H_E)

start = time.time()

path = []
for step in range(150):  # in ball timestep is 0.1 so this is 20 seconds
    h_n = H_N
    h_w = H_W  - step/150*np.sin(step/10)
    h_e = H_E  + step/150*np.sin(step/10)

    #update ball
    p_r, p_q, p_z = ball.update_polar(LF, D_WN, D_NE, D_EW, h_w, h_n, h_e )

    path.append( [p_r,p_q,p_z] )

end = time.time()

file = open("demo.dat", "w" )
for entry in path:
    file.write( str( entry[0] ) + " " + str( entry[1] ) + " " + str( entry[2] ) + "\n")
file.close()

print("time elapsed: " + str( end - start ))
