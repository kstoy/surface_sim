import numpy as np
import constants as const

def cosinewave( coeffs, x, t ):
    v0 = coeffs[0]
    a = 1.0 #heighest wave always best
    b = coeffs[1] 
    c = coeffs[2]
    x_shifted = x - v0*t

    return( (np.cos( b * x_shifted + c ) + 1.0)/2 )
    
if __name__ == '__main__':
    coeffs = [0.25555584936371467 , 2.2480573717160564 , 3.654110870114149 ]

    with open("./data/cosineseries.dat", "w") as f:
        for x in np.linspace(0, 10, 100):
            print( x, " ", cosinewave(coeffs, x, 0), file=f )
