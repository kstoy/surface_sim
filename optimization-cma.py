import catenarysurface as sim
import visualization as vis
import constants as const
import simulation as sim
import cma 
from numpy import fabs, inf, sum
import multiprocessing

def fitness( cosinewavecoefficients ):
    fitness = 0.0

    _ , ballspaths, _ = sim.simulation( cosinewavecoefficients, visualization=False )


    for ballpositions in ballspaths[-1]:
        #fitness += fabs( (const.D*2.5) - position[0] )
        fitness += sum( fabs( 2.5 - ballpositions[0] )  )
    return( fitness )

def printresult( result ):
    print( "[" + str(result.x[0]), end=" ")
    for f in result.x[1:]:
        print( ", " + str(f), end=" " )
    print( "]", end=" " )

    print( "fitness: " + str( result.fun ) )

if __name__ == '__main__':
    es = cma.CMAEvolutionStrategy( [0.0] * const.MAXCOEFF, 1.0 )

    #for e in cma.CMAOptions():
    #    print( str( e ) )

    pool = multiprocessing.Pool()

    while not es.stop():
        solutions = es.ask()
        fitnessvalues = pool.map(fitness, solutions)
        es.tell(solutions, fitnessvalues)
        es.logger.add()
        es.disp()
        
    pool.close()
    es.result_pretty()

    #result = differential_evolution(fitness, bounds, workers=10, polish=False, updating='deferred', callback=thecallback )

    #print( "Final result:")
    #printresult( result )

    rodspaths, ballspaths, ballsradiuses = sim.simulation(   es.result.xbest, visualization=True )

    vis.generategltffiles( "surfacevisualization", rodspaths, ballspaths, ballsradiuses )


    
