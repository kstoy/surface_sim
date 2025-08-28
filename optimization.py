from scipy.optimize import differential_evolution, OptimizeResult
import surfacesimulation as sim
import visualization as vis
import constants as const
from main import generatevisualization

def fitness( fourierserieswavecoefficients ):
    ballpath, rodspath = sim.run(  fourierserieswavecoefficients )

    # move to the right end of surface as fast as possible
    # fitness = -( 1 - (2.0*float(len(ballpath))/const.MAXSIMULATIONSTEPS)) * (1 - ( const.D*(const.GRIDSIZEX-1) - ballpath[-1][0] ) / (const.D*(const.GRIDSIZEX-1)) )
    fitness = (-ballpath[-1][0]/const.D*(float(const.GRIDSIZEX)-1.0))/(len(ballpath)/const.MAXSIMULATIONSTEPS)
    return( fitness )

def printresult( result ):
    print( "[" + str(result.x[0]), end=" ")
    for f in result.x[1:]:
        print( ", " + str(f), end=" " )
    print( "]", end=" " )

    print( "fitness: " + str( result.fun ) )

def thecallback(intermediate_result: OptimizeResult):
    printresult( intermediate_result )
    #if intermediate_result.fun < -const.D*(float(const.GRIDSIZEX)-1.0):
    #    raise StopIteration

if __name__ == '__main__':
    bounds = [(-0.5,0.5)]*const.MAXCOEFF

    result = differential_evolution(fitness, bounds, workers=10, updating='deferred', callback=thecallback )

    printresult( result )

    ballpath, rodspath = sim.run( result.x )

    vis.generategltffiles( "surfacevisualization", rodspath, ballpath )


    
