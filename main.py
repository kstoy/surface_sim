import time

import surfacesimulation as sim
import visualization as vis

#do simulation
start = time.time()
ballpath, rodspath = sim.run()
end = time.time()
print("time elapsed: " + str( end - start ))

#generate and save gltf files
vis.generategltffiles( "surfacevisualization", rodspath, ballpath )
