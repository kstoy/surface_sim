
import catenary as cat
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
FLOOR_LEVEL = -1.0   # this wis here the ball ends if it falls off the surface
DT = 0.1                    # Time step for the simulation
DQ = 0.01                   # constant to calculate an estimate of the derivative with respect to q


def set_polar( r, q, z ):
    global p_r, p_q, p_z
    p_r = r
    p_q = q
    p_z = z

def update_polar(lf, d_wn, d_ne, d_ew, h_w, h_n, h_e):
    global p_q, p_r, p_z, v_r, v_q, a_r, a_q

    # catenary curve on opposite side of triangle
    en_curve = cat.findcatenaryparameters( lf*d_ne, d_ne, h_e, h_n ) 

    # ball is on surface
    z_x0 = h_w

    ###############
    # ball r
    ###############

    # triangle made up of sides d_wn, d_ne, and d_ew 
    q_d_wn = np.arccos( (d_ew**2 + d_ne**2 - d_wn**2 ) / ( 2* d_ew * d_ne ))
    q_d_ne = np.arcsin( d_ne * np.sin( q_d_wn ) / d_wn  )

    # triangle made of up sides d_r, d_c, d_ew where d_ew, q_d_wn, and p_q (ie. q_d_c) are known
    q_d_ew = np.pi - q_d_wn - p_q    
    d_r = d_ew * np.sin( q_d_wn ) / np.sin( q_d_ew )   # from law of sines
    d_c = d_ew * np.sin( p_q ) / np.sin( q_d_ew )
    l_r = d_r * lf

    # ball off surface
    if p_r < 0 or p_r > d_r or p_q < 0 or p_q > q_d_ne:  
        return( [p_r, p_q, FLOOR_LEVEL] )

    z_x1 = cat.catenary( d_c, en_curve )
    r_curve = cat.findcatenaryparameters( l_r, d_r, z_x0, z_x1 )

    rping = cat.dcatenary( p_r, r_curve ) 

    # Calculate accelerations F = m*a = -m*g*sin(angle) hence a = -k*sin(angle) where k=mg
    a_r = - 0.1 * np.sin( np.atan( rping ) )
    
    # Update velocities
    v_r += a_r * DT
    
    # Update positions
    p_r += v_r * DT

    if p_r >= 0 and p_r <= d_r and p_q >= 0 and p_q <= q_d_ne:  
        p_z = cat.catenary( p_r, r_curve ) + BALL_R
    else:        
        p_z = FLOOR_LEVEL

    ###############
    # ball q
    ###############

    # triangle made of up sides d_r, d_c, d_ew where d_ew, q_d_wn, and p_q+DQ (ie. q_d_c) are known
    q_d_ew = np.pi - q_d_wn - (p_q+DQ)    
    d_r = d_ew * np.sin( q_d_wn ) / np.sin( q_d_ew )   # from law of sines
    d_c = d_ew * np.sin( p_q + DQ ) / np.sin( q_d_ew )
    l_r = d_r * lf
    z_x1 = cat.catenary( d_c, en_curve )
    r_dq_plus_curve = cat.findcatenaryparameters( l_r, d_r, z_x0, z_x1 )

    # triangle made of up sides d_r, d_c, d_ew where d_ew, q_d_wn, and p_q-DQ (ie. q_d_c) are known
    q_d_ew = np.pi - q_d_wn - (p_q-DQ)    
    d_r = d_ew * np.sin( q_d_wn ) / np.sin( q_d_ew )   # from law of sines
    d_c = d_ew * np.sin( p_q - DQ ) / np.sin( q_d_ew )
    l_r = d_r * lf
    z_x1 = cat.catenary( d_c, en_curve )
    r_dq_minus_curve = cat.findcatenaryparameters( l_r, d_r, z_x0, z_x1 )

    if p_r > 0:
        qping = (cat.catenary( p_r, r_dq_plus_curve ) - cat.catenary( p_r, r_dq_minus_curve ) )/(2*DQ*p_r) 
    else:
        qping = 0.0

    # Calculate accelerations F = m*a = -m*g*sin(angle) hence a = -k*sin(angle) where k=mg
    a_q = - 0.1 * np.sin( np.atan( qping ) )
    
    # Update velocities
    v_q += a_q * DT
    
    # Update positions
    p_q += v_q * DT    

    return( [p_r,p_q,p_z] )