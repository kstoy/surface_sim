import catenarysurface as sim
import visualization as vis
import constants as const
import simulation as sim
import cma 
from numpy import fabs, inf, sum, array, ndarray, dot
import multiprocessing
from scipy.optimize import linear_sum_assignment

def fitness( coeffs ):
    fitness = 0.0

    _ , ballspaths, _ = sim.simulation( array( coeffs ), visualization=False )

    goalpositions = array([
        [ 3.5, 3.5, 0.0],
        [ 2.5, 1.5, 0.0],
        [ 3.5, 1.5, 0.0],
        [ 2.5, 2.5, 0.0],
        [ 2.5, 3.5, 0.0],
    ], dtype= float)

    costmatrix = ndarray((const.NBALL,const.NBALL), dtype=float )

    for ballpositions in ballspaths:
        for ballno in range(const.NBALL):
            for goalno in range(const.NBALL):
                costmatrix[ballno,goalno] = sum( fabs( goalpositions[goalno] - ballpositions[ballno] ) ) 

        row_ind, col_ind = linear_sum_assignment( costmatrix )

        fitness += costmatrix[row_ind, col_ind].sum()

    return( fitness )

def printresult( result ):
    print( "[" + str(result[0]), end=" ")
    for f in result[1:]:
        print( ", " + str(f), end=" " )
    print( "]" )

if __name__ == '__main__':
    es = cma.CMAEvolutionStrategy( [0.0] * const.MAXCOEFF, 1.0, {'tolfun': 0.01, 'maxfevals': 2000} )

    #for e in cma.CMAOptions():
    #    print( str( e ) )

    pool = multiprocessing.Pool()

    while not es.stop():
        solutions = es.ask()
        fitnessvalues = pool.map(fitness, solutions)
        es.tell(solutions, fitnessvalues)
        es.logger.add()
        #printresult( es.result.xbest )
        es.disp()
        
    pool.close()
    es.result_pretty()
    printresult( es.result.xbest )

    rodspaths, ballspaths, ballsradiuses = sim.simulation(   es.result.xbest, visualization=True )

    vis.generategltffiles( "surfacevisualization", rodspaths, ballspaths, ballsradiuses )


    
