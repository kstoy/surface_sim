
import catenary as cat
import numpy as np

DQ = 0.01            # constant to calculate an estimate of the derivative with respect to q

# this generates a fan of p catenary curves from the origin O to the catenary curve
# connecting point 1 and 2 where lf is the length factor and d is the distances and h the heights
def calccatenarysurface( lf, d_O2, d_12, d_O1, h_O, h_2, h_1, p ):
    curve_12 = cat.findcatenaryparameters( lf*d_12, d_12, h_1, h_2 )     # curve from 1 to 2

    surfacepoints = []

    # triangle made up of sides d_O2, d_12, and d_O1     
    q_1 = np.arccos( (d_O1**2 + d_12**2 - d_O2**2 ) / ( 2* d_O1 * d_12 ))
    q_O = np.arcsin( d_12 * np.sin( q_1 ) / d_O2  )

    Q = np.linspace( 0, q_O, p) 

    # lower coordinate is at (0,0) 
    surfacepoints.append( (0.0,0.0,h_O) )

    for q in Q:
        q_3 = np.pi - q_1 - q    
        d_O3 = d_O1 * np.sin( q_1 ) / np.sin( q_3 )   # from law of sines
        d_13 = d_O1 * np.sin( q ) / np.sin( q_3 )

        h_3 = cat.catenary( d_13, curve_12 )

        curve_O3 = cat.findcatenaryparameters( d_O3 * lf, d_O3, h_O, h_3)

        for r in np.linspace( 0, d_O3, p):
            surfacepoints.append( (r*np.cos(q), r*np.sin(q), cat.catenary( r, curve_O3)))

    return( np.array( surfacepoints ) )

def findcurve_O3(lf, z_O, q_O, q_1, d_O1, curve_12 ):
    q_3 = np.pi - q_1 - q_O    
    d_O3 = d_O1 * np.sin( q_1 ) / np.sin( q_3 )   # from law of sines
    d_13 = d_O1 * np.sin( q_O ) / np.sin( q_3 )
    z_3 = cat.catenary( d_13, curve_12 )
    curve_O3 = cat.findcatenaryparameters( d_O3*lf, d_O3, z_O, z_3 )
    return curve_O3 

# this finds the gradient in the radial and angular direction at p = (p_r, p_q)
# lf - is the fabric length factor 
# d_O1 - is the distance from the origin to point 1
# d_O2 - is the distance from the origin to point 2 (assumed to be counter-clockwise from point 1)
# d_12 - is the distance from point 1 to point 2
# z_O - is the height of point 0
# z_1 - is the height of point 1
# z_2 - is the height of point 2
def grad(p_r, p_q, lf, d_O2, d_12, d_O1, z_O, z_2, z_1):
    # catenary curve between point 1 and 2
    curve_12 = cat.findcatenaryparameters( lf*d_12, d_12, z_1, z_2 ) 

    # radial direction
    ##################

    ## find the distance from point 2 to point 3 (point 3 is where the the radial line at angle p_q intersects the line from 1 to 2)
    q_1 = np.arccos( (d_O1**2 + d_12**2 - d_O2**2 ) / ( 2* d_O1 * d_12 ))

    # triangle made of up sides d_r (d_03), d_c (d_13), d_O1 where d_01, q_1, and p_q (ie. q_O) are known

    curve_O3 = findcurve_O3(lf, z_O, p_q, q_1, d_O1, curve_12 )
    grad_r = cat.dcatenary( p_r, curve_O3 ) 

    # angular direction
    ##################

    # triangle made of up sides d_r (d_03), d_c (d_13), d_O1 where d_01, q_1, and p_q (ie. q_O) are known
    curve_O3 = findcurve_O3(lf, z_O, p_q + DQ, q_1, d_O1, curve_12 )
    z_q_plus = cat.catenary( p_r, curve_O3 )

    curve_O3 = findcurve_O3(lf, z_O, p_q - DQ, q_1, d_O1, curve_12 )
    z_q_minus = cat.catenary( p_r, curve_O3 )

    if p_r > 0:
        grad_q = ( z_q_plus - z_q_minus ) / ( 2 * DQ * p_r) 
    else:
        grad_q = 0.0

    return( np.array([grad_r,grad_q] ) )

#find z of surface at point p_r, p_q
def findz(p_r, p_q, lf, d_O2, d_12, d_O1, z_O, z_2, z_1):
    # catenary curve between point 1 and 2
    curve_12 = cat.findcatenaryparameters( lf*d_12, d_12, z_1, z_2 ) 

    q_1 = np.arccos( (d_O1**2 + d_12**2 - d_O2**2 ) / ( 2* d_O1 * d_12 ))
    curve_O3 = findcurve_O3(lf, z_O, p_q, q_1, d_O1, curve_12 )
    z = cat.catenary( p_r, curve_O3 ) 

    return( z )