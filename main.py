import time
import surfacesimulation as sim
import visualization as vis

if __name__ == '__main__':
    coeff = [0.1982430872439912 , 0.035204663956792004 , 0.4840001782981266 , 0.49983932970002243 , -0.30660393794799423 , 0.24091055640485215 ]

    #do simulation
    start = time.time()
    ballpath, rodspath = sim.run( coeff )
    end = time.time()
    print("time elapsed: " + str( end - start ))

    #visualization: generate and save gltf files
    vis.generategltffiles( "surfacevisualization", rodspath, ballpath )
