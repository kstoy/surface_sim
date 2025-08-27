import numpy as np
from constants import *
import fourierserieswave as fsw
import catenary as cat

def positiontoindex( position ):
    return( np.array( [int( position[0] / D ), int( position[1] / D )]))

def run():
    # initial ball parameters - p position, v velocity, a acceleration
    a_ball = np.array( [ 0.0, 0.0] )
    v_ball = np.array( [ 0.0, 0.0] )
    p_ball = np.array( [ 2.0, 0.5] )

    # ball path
    ballpath = []

    # height of poles as a function of timestep
    rodspath = []

    for step in range(MAXSIMULATIONSTEPS):  # in ball timestep is 0.1 so this is 20 seconds
        # check if ball has fallen off the grid
        if p_ball[0] < 0 or p_ball[0] > D*(GRIDSIZEX-1) or p_ball[1] < 0 or p_ball[1] > D*(GRIDSIZEY-1):
            break

        # surface control 
        rods = np.empty( (GRIDSIZEX,GRIDSIZEY), dtype=object )
        for i in range(GRIDSIZEX):
            for j in range(GRIDSIZEY):
                t = float(step)*DT
                rods[i][j] = np.array( [float(i)* D, float(j)*D, fsw.fourierserieswave( [0.25,0.25,0.75,0.25,0.75], float(i)*D, float(step)*DT) ] )  # this is the wave function

        # ball simulation
        (ball_x_index,ball_y_index) = positiontoindex( p_ball )

        p_ball_local = p_ball - np.array([ ball_x_index * D, ball_y_index*D ])

        # find heights of surrounding rods
        rod_nw = rods[ball_x_index][ball_y_index+1]
        rod_sw = rods[ball_x_index][ball_y_index]
        rod_se = rods[ball_x_index+1][ball_y_index]
        rod_ne = rods[ball_x_index+1][ball_y_index+1]

        cat_w = cat.findcatenaryparameters( LF, D, rod_sw[2], rod_nw[2] )  
        cat_e = cat.findcatenaryparameters( LF, D, rod_se[2], rod_ne[2] )  
        height_w_y = cat.catenary( p_ball_local[1], cat_w )
        height_e_y = cat.catenary( p_ball_local[1], cat_e )
        cat_we_y = cat.findcatenaryparameters( LF, D, height_w_y, height_e_y )  

        cat_n = cat.findcatenaryparameters( LF, D, rod_nw[2], rod_ne[2] )  
        cat_s = cat.findcatenaryparameters( LF, D, rod_sw[2], rod_se[2] )  
        height_n_y = cat.catenary( p_ball_local[0], cat_n )
        height_s_y = cat.catenary( p_ball_local[0], cat_s )
        cat_sn_y = cat.findcatenaryparameters( LF, D, height_s_y, height_n_y )  

        grad_x = cat.dcatenary( p_ball_local[0], cat_we_y)
        grad_y = cat.dcatenary( p_ball_local[1], cat_sn_y)
        ball_z = cat.catenary( p_ball_local[0], cat_we_y)  + 0.1 # ball radius
    
        grad = np.array( [grad_x, grad_y])

        # Calculate accelerations F = m*a = -m*g*sin(angle) hence a = -k*sin(angle) where k=mg
        a_ball = - 0.1 * np.sin( np.arctan( grad ) )

        # Update velocities
        v_ball += a_ball * DT
    
        # Update positions
        p_ball += v_ball * DT

        if ( step % RECORDFRAME == 0 ): 
            rodspath.append( rods )
            ballpath.append( [p_ball[0],p_ball[1],ball_z] )

    return( ballpath, rodspath )
    


