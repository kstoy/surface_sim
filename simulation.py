import numpy as np
import time

from constants import *

import ballstate as bs
import simcorexpbd as sc
import visualization as vis
import rodstate as rs

def simulation( coeffs, visualization = True ):
    rodsstate = rs.RodsState( coeffs )
    rodsstate.settimestep( 0 )
    ballsstate = bs.BallsState( rodsstate )

    ballsstates = []
    rodsstates = []

    for timestep in range(MAXSIMULATIONSTEPS):
        rodsstate.settimestep( timestep )
        if visualization:
            rodsstate.update()
            rodsstates.append(rodsstate.rods.copy())

        sc.step(
            ballsstate,
            rodsstate, 
            dt=DT,
            gravity=9.81,
            mu_s=0.6, mu_k=0.5,
            compliance_n=0.1,     # 0 = hard contact
            num_pos_iters=10,     # tighter contact
            substeps=1,           # reduce per-substep travel
            pair_margin=0.15,
            use_grid_broadphase=False,
            linear_damping=0.01
        )

        ballsstates.append(ballsstate.r.copy())

    return( rodsstates, ballsstates, ballsstate.R )


    

if __name__ == "__main__":
    print("simulation running without visualization...", end="")
    start = time.time()
    rodsstates, ballsstates, ballsradiuses = simulation( [  2.6438248610474613, 13.431899848987156, -6.7422126501257065, 14.444057341122013, -1.7242975763525634, -19.617516094223525, -10.202722516830153, -23.1695767704936, -2.034232542548068, -32.57241602377202, 10.410573050097318, -6.944904682706344, 3.560616901906224, 11.940890122375952 ], visualization=False )
    end = time.time()
    print("done")
    print("Simulation complete - time elapsed: " + str( end - start ))

    print("simulation running with visualization...", end="")
    start = time.time()
    rodsstates, ballsstates, ballsradiuses = simulation( [  2.6438248610474613, 13.431899848987156, -6.7422126501257065, 14.444057341122013, -1.7242975763525634, -19.617516094223525, -10.202722516830153, -23.1695767704936, -2.034232542548068, -32.57241602377202, 10.410573050097318, -6.944904682706344, 3.560616901906224, 11.940890122375952 ], visualization=True )
    end = time.time()
    print("done")
    print("Simulation complete - time elapsed: " + str( end - start ))


    #visualization: generate and save gltf files
    vis.generategltffiles( "surfacevisualization", rodsstates, ballsstates, ballsradiuses )
