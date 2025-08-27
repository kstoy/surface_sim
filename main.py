from sys import exit
import numpy as np
import time
import pygltflib as gltf
import catenary as cat
import fourierserieswave as fsw
import surfacesimulation as sim
from constants import *
import visualization as vis

#do simulation
start = time.time()
ballpath, rodspath = sim.run()
end = time.time()
print("time elapsed: " + str( end - start ))

#generate and save gltf files
vis.generategltffiles( "surfacevisualization", rodspath, ballpath )
