import time
import surfacesimulation as sim
import visualization as vis

if __name__ == '__main__':
    coeff = [0.2796433112703206 , 0.08429341132346124 , -0.49977767683445246 , -0.48679898087814644 , -0.43033998426660824 , 0.09216036312868536 ]

    #do simulation
    start = time.time()
    ballpath, rodspath = sim.run_1d( coeff )
    end = time.time()
    print("time elapsed: " + str( end - start ))

    #visualization: generate and save gltf files
    vis.generategltffiles( "surfacevisualization", rodspath, ballpath )
