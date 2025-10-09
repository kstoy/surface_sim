D  = 1.0                # distance between rods in meters
LF = 1.42 # (>sqrt(2))                # fabric length factor (e.g. 1 means the fabric is equal to distance, 4 that there is four times more)

MAXSIMULATIONSTEPS = 200   # x0.1sec = 45seconds  
DT = 0.02                   # simulation time step in seconds

GRIDSIZEX = 10            # poles per side - must be even so there is an odd number of modules per side (restriction from rendering)
GRIDSIZEY = 2

TRIANGLES = 9

EXPLODE = 1.0             # used to seperate trianglestrips for debugging 1 no separation - 2 some seperation

RECORDFRAME = 2 # record every nth frame

MAXCOEFF = 14

NBALL = 1

SIGMA = 0.01            # this is the std. dev. add as noise to surface height


P = 2.0
