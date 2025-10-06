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
    rodsstates, ballsstates, ballsradiuses = simulation( [  1.08268258, 1.00004563, -0.3360156 ], visualization=False )
    end = time.time()
    print("done")
    print("Simulation complete - time elapsed: " + str( end - start ))

    print("simulation running with visualization...", end="")
    start = time.time()
    rodsstates, ballsstates, ballsradiuses = simulation( [  1.08268258, 1.00004563, -0.3360156 ], visualization=True )
    end = time.time()
    print("done")
    print("Simulation complete - time elapsed: " + str( end - start ))


    #visualization: generate and save gltf files
    vis.generategltffiles( "surfacevisualization", rodsstates, ballsstates, ballsradiuses )
