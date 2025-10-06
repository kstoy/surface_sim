from scipy.optimize import differential_evolution, OptimizeResult, minimize
import catenarysurface as sim
import visualization as vis
import constants as const
import simulation as sim
from numpy import fabs, inf, sum

def fitness( cosinewavecoefficients ):
    fitness = 0.0

    _ , ballspaths, _ = sim.simulation( cosinewavecoefficients )


    for ballpositions in ballspaths[-1]:
        fitness += fabs( (const.D*2.5) - ballpositions[0] )
        #fitness += sum( fabs( const.D*(const.GRIDSIZEX-1) - 0.5 - ballpositions[:,0] ) + fabs( const.D*(const.GRIDSIZEX-1) - 4.5 - ballpositions[:,1] ) + fabs( 1 - ballpositions[:,2] ))
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
    bounds = [(-15.0,15.0)]*const.MAXCOEFF

    result = differential_evolution(fitness, bounds, workers=10, polish=False, updating='deferred', callback=thecallback )

    print( "Final result:")
    printresult( result )

    rodspaths, ballspaths, ballsradiuses = sim.simulation( result.x )

    vis.generategltffiles( "surfacevisualization", rodspaths, ballspaths, ballsradiuses )


    
