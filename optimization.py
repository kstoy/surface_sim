from scipy.optimize import differential_evolution, OptimizeResult
import catenarysurface as sim
import visualization as vis
import constants as const
import simulation as sim
from numpy import fabs, inf, sum, array, inf

def fitness( cosinewavecoefficients ):
    fitness = 0.0

    _ , ballspaths, _ = sim.simulation( array( cosinewavecoefficients ), visualization=False )


    for ballpositions in ballspaths:
        fitness += sum( fabs( 2.5 - ballpositions[:,0] ) + fabs( 0.5 - ballpositions[:,1] ) + fabs( ballpositions[:,2] )  )
    return( fitness )

def printresult( result ):
    print( "[" + str(result.x[0]), end=" ")
    for f in result.x[1:]:
        print( ", " + str(f), end=" " )
    print( "]", end=" " )

    print( "fitness: " + str( result.fun ) )

def thecallback(intermediate_result: OptimizeResult):
    printresult( intermediate_result )
    if intermediate_result.fun < 0.0001:
        raise StopIteration

if __name__ == '__main__':
    bounds = [(-100,100)]*const.MAXCOEFF

    result = differential_evolution(fitness, bounds, workers=10, polish=False, updating='deferred', callback=thecallback, tol= 0.1 )

    print( "Final result:")
    printresult( result )

    rodspaths, ballspaths, ballsradiuses = sim.simulation( result.x, visualization=True )

    vis.generategltffiles( "surfacevisualization", rodspaths, ballspaths, ballsradiuses )


    
