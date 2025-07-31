
import catenarysurface as cat
import numpy as np

# global variables
# ball is simulated in cylindrical coordinates below are (p_r,P_q,p_z) and the time derivatives and their initialization
p_r = 0.0  # this needs to be between 0 and D (although slightly more than D depending on angle)
p_q = 0.0  # this angle is between 0 and pi/3                                    
p_z = 0.0  # this is updated in first simulation loop so not important

v_r = 0
v_q = 0

a_r = 0
a_q = 0

# constants 
BALL_R = 0.05
FLOOR_LEVEL = -1.0   # this is here the ball ends if it falls off the surface
DT = 0.1             # Time step for the simulation


def set_polar( r, q, z ):
    global p_r, p_q, p_z
    p_r = r
    p_q = q
    p_z = z

def update_polar(lf, d_wn, d_ne, d_ew, h_w, h_n, h_e):
    global p_q, p_r, p_z, v_r, v_q, a_r, a_q

    (rping, qping) = cat.grad( p_r, p_q, lf, d_wn, d_ne, d_ew, h_w, h_n, h_e )

    # Calculate accelerations F = m*a = -m*g*sin(angle) hence a = -k*sin(angle) where k=mg
    a_r = - 0.1 * np.sin( np.atan( rping ) )
    
    # Update velocities
    v_r += a_r * DT
    
    # Update positions
    p_r += v_r * DT

    # Calculate accelerations F = m*a = -m*g*sin(angle) hence a = -k*sin(angle) where k=mg
    a_q = - 0.1 * np.sin( np.atan( qping ) )
    
    # Update velocities
    v_q += a_q * DT
    
    # Update positions
    p_q += v_q * DT    

    p_z = cat.findz(p_r, p_q, lf, d_wn, d_ne, d_ew, h_w, h_n, h_e)

    #if p_r >= 0 and p_r <= d_r and p_q >= 0 and p_q <= q_d_ne:  
    #    p_z = cat.catenary( p_r, r_curve ) + BALL_R
    #else:        
    #    p_z = FLOOR_LEVEL


    return( [p_r,p_q,p_z] )