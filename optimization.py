from scipy.optimize import differential_evolution, OptimizeResult
import surfacesimulation as sim
import visualization as vis
import constants as const
from numpy import fabs, inf

def fitness( cosinewavecoefficients ):
    ballpath, rodspath = sim.run_1d(  cosinewavecoefficients )
    #fitness = fabs( (const.D*1.5)-ballpath[-1][0])

    # move to the right end of surface as fast as possible
    fitness = (-ballpath[-1][0]/(const.D*(float(const.GRIDSIZEX)-1.0)))/(len(ballpath)/const.MAXSIMULATIONSTEPS)
    #fitness = - ballpath[-1][0]
    #end in middle of second module
    #fitness += fabs( (const.D*1.5)-ballpath[-1][0])
    return( fitness )

def printresult( result ):
    print( "[" + str(result.x[0]), end=" ")
    for f in result.x[1:]:
        print( ", " + str(f), end=" " )
    print( "]", end=" " )

    print( "fitness: " + str( result.fun ) )

def thecallback(intermediate_result: OptimizeResult):
    printresult( intermediate_result )
    #if intermediate_result.fun < -7.0:
    #    raise StopIteration

if __name__ == '__main__':
    bounds = [(0.0,5.0)]*const.MAXCOEFF

    result = differential_evolution(fitness, bounds, workers=10, polish=False, updating='deferred', callback=thecallback )

    print( "Final result:")
    printresult( result )

    ballpath, rodspath = sim.run_1d( result.x )

    vis.generategltffiles( "surfacevisualization", rodspath, ballpath )


    
