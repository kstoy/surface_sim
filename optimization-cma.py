import catenarysurface as sim
import visualization as vis
import constants as const
import simulation as sim
import cma 
from numpy import fabs, inf, sum, array
import multiprocessing

def fitness( coeffs ):
    fitness = 0.0

    _ , ballspaths, _ = sim.simulation( array( coeffs ), visualization=False )


    for ballpositions in ballspaths:
        #fitness += fabs( (const.D*2.5) - position[0] )
        startz = ballpositions[0,2]
        fitness += sum( fabs( 3.5 - ballpositions[:,0] ) + fabs( startz - ballpositions[:,2] ) + fabs( 3.5 - ballpositions[:,1] ) )
    return( fitness )

def printresult( result ):
    print( "[" + str(result[0]), end=" ")
    for f in result[1:]:
        print( ", " + str(f), end=" " )
    print( "]" )

if __name__ == '__main__':
    es = cma.CMAEvolutionStrategy( [0.0] * const.MAXCOEFF, 1.0, {'tolfun': 0.1, 'maxfevals': 10000} )

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
    printresult( es.result.xbest )

    rodspaths, ballspaths, ballsradiuses = sim.simulation(   es.result.xbest, visualization=True )

    vis.generategltffiles( "surfacevisualization", rodspaths, ballspaths, ballsradiuses )


    
