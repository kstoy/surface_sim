
import catenary as cat
import numpy as np

# ball is simculated in cylindrical coordinates below are (p_r,P_q,p_z) and the time derivatives and their initialization
BALL_R = 0.05
FLOOR_LEVEL = -1.0   # this where the ball ends if it falls off the surface

p_r = 0.0                  # this needs to be between 0 and D (although slightly more than D depending on angle)
p_q = 0.0          # this angle is between 0 and pi/3                                    
p_z = 0.0                  # this is updated in first simulation loop so not important

v_r = 0
v_q = 0

a_r = 0
a_q = 0

dt = 0.1                    # Time step for the simulation

dq = 0.01                   # constant to calculate an estimate of the derivative with respect to q


def set_polar( r, q, z ):
    global p_r, p_q, p_z
    p_r = r
    p_q = q
    p_z = z

def update_polar(l, d, h_w, en_curve): 
    global p_q, p_r, p_z, v_r, v_q, a_r, a_q

    # ball is on surface
    z_x0 = h_w

    # ball r
    d_r = np.sin( np.pi / 3 ) * d / np.sin( 2 * np.pi / 3 - p_q )
    l_r = d_r * l / d
    c_r  = np.sin( p_q ) * d / np.sin( 2 * np.pi / 3 - p_q )          
    z_x1 = cat.catenary( c_r, en_curve )
    r_curve = cat.findcatenaryparameters( l_r, d_r, z_x0, z_x1 )

    rping = cat.dcatenary( p_r, r_curve ) 

    # Calculate accelerations F = m*a = -m*g*sin(angle) hence a = -k*sin(angle) where k=mg
    a_r = - 0.1 * np.sin( np.atan( rping ) )
    
    # Update velocities
    v_r += a_r * dt
    
    # Update positions
    p_r += v_r * dt

    if p_r >= 0 and p_r <= d_r and p_q >= 0 and p_q <= np.pi/3:  
        p_z = cat.catenary( p_r, r_curve ) + BALL_R
    else:
        p_z = FLOOR_LEVEL

    # ball q
    d_q = np.sin( np.pi / 3 ) * d / np.sin( 2 * np.pi / 3 - (p_q+dq) )
    l_q = d_q * l / d
    c_q  = np.sin( p_q + dq ) * d / np.sin( 2 * np.pi / 3 - (p_q+dq ) )          
    z_x1 = cat.catenary( c_q, en_curve )
    r_dq_plus_curve = cat.findcatenaryparameters( l_q, d_q, z_x0, z_x1 )

    d_q = np.sin( np.pi / 3 ) * d / np.sin( 2 * np.pi / 3 - (p_q-dq) )
    l_q = d_q * l / d
    c_q  = np.sin( p_q - dq ) * d / np.sin( 2 * np.pi / 3 - (p_q-dq ) )          
    z_x1 = cat.catenary( c_q, en_curve )
    r_dq_minus_curve = cat.findcatenaryparameters( l_q, d_q, z_x0, z_x1 )

    if np.abs( p_r) > 0:
        qping = (cat.catenary( p_r, r_dq_plus_curve ) - cat.catenary( p_r, r_dq_minus_curve ) )/(2*dq*p_r) 
    else:
        qping = 0.0

    # Calculate accelerations F = m*a = -m*g*sin(angle) hence a = -k*sin(angle) where k=mg
    a_q = - 0.1 * np.sin( np.atan( qping ) )
    
    # Update velocities
    v_q += a_q * dt
    
    # Update positions
    p_q += v_q * dt    

    return( [p_r,p_q,p_z] )