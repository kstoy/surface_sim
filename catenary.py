from sys import exit
from numpy import sinh, cosh, arctanh, sqrt, fabs, pi, linspace, sin, cos, array
from scipy.optimize import newton

# This is based on the paper entitled "Catenary Curve" by Rod Deakin
# The paper can be found here: https://www.mygeodesy.id.au/documents/Catenary%20Curve.pdf, Apr 2025.
# Equations references in the code is to this paper

# the catenary function
def catenary( x, parameters):
    a, offsetx, offsety = parameters
    return( a*cosh( (x+offsetx)/a) + offsety )

# differentiated catenary function
def dcatenary( x, parameters ):
    a, offsetx, offsety = parameters
    return( sinh( (x+offsetx)/a) )

# find the parameters of a catenary function given
# l length of chain, d distance between the attachments of the chain, and h1 and h2 the heights of the attachments
def findcatenaryparameters( l, d, h1, h2 ):   
    v = h2 - h1

    if (v**2 + d**2) > l**2:
        print( "Chain too short! Minimum required length: " + str( sqrt((fabs(v)**2 + d**2)) ) )
        print( str(l) + " " + str(d) + " " + str(h1) + " " + str(h2) )
        exit()


    # the purpose of the follow section is to find the parameter a.
    # Unfortunately, it is not possible to isolate a in the equation below and
    # therefore we have to find it numerically here using the Newton-Rapson method
    def f( a:float ):
        return( 2*a*sinh(d/(2*a)) - sqrt( l**2 - v**2 ) )

    def f_prime( a:float ):
        return( 2*(sinh(d/(2*a))-d/(2*a)*cosh(d/(2*a))) )

    #   alternative set of equations - same results as above - maybe useful if faster - not tested for performance
    #    def f( a:float ):
    #        q = arctanh( v/L )
    #        return( a*(sinh(D/(2*a)+q)+sinh(D/(2*a)-q)) - L) 

    #    def f_prime( a:float ):
    #        q = arctanh( v/L )
    #        return( 2*cosh(q)*(sinh(D/(2*a))-D/(2*a)*cosh(D/(2*a))) )

    initial_guess = d/sqrt(24)*sqrt( d / ( sqrt( l**2 - v**2 ) - d ) )      # initial guess (equation 42 of Deakin's paper)
        
    a = fabs( newton(f, initial_guess, fprime = f_prime) )                  # find paraneter a using the Newton-Rapson method

    # with the a parameter known we can translate the function to match the known end points (see paper)
    x1 = a * arctanh( v / l ) - d/2                                     
    offsetx = x1 
    y1 = a*cosh( x1 / a )
    offsety = ( h1 - y1 )

    # these are the parameters for a catenary curve running in the interval [0:d] where f(0)=y1 and f(d)=y2
    return( [a, offsetx, offsety] ) 

# this generates a fan of p catenary curves from h_w to the catenary curve
# connecting h_e and h_n where l is the chain length and d is the distance between h_e, h_w, h_n
def calccatenarysurface( l, d, h_n, h_w, h_e, p ):
    en_curve = findcatenaryparameters( l, d, h_e, h_n )     # curve from east (e) to north (n)

    surfacepoints = []

    Q = linspace( 0, pi/3, p) 

    # lower coordinate is at (0,0) 
    z_x0 = h_w

    surfacepoints.append( (0.0,0.0,z_x0) )

    for q in Q:
        d_q = sin( pi/3) * d / sin( 2*pi/3 - q )
        l_q = d_q*l/d
        c_q  = sin(q) * d_q / sin(pi/3)  
        
        z_x1 = catenary( c_q, en_curve )

        curve = findcatenaryparameters( l_q, d_q, z_x0, z_x1)

        R = linspace( 0, d_q, p)
        for r in R:
            surfacepoints.append( (r*cos(q), r*sin(q), catenary( r, curve)))

    return( array( surfacepoints ) )