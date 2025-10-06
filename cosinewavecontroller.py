import numpy as np
import constants as const

class cosinewavecontroller:
    def __init__(self, coeffs):
        self.rng = np.random.default_rng(3)
        self.SIGMA = 0.01
        self.coeffs = coeffs

    def cosinewave( self, x, t ):
        v0, a, b = self.coeffs
        x_shifted = x - v0*t

        return( (np.cos( 2 * np.pi * a *  x_shifted + 2*np.pi*b ) + 1.0) /2)
    
    def update( self, i, j, timestep):
        return( np.clip( self.cosinewave( float(i)*const.D, float(timestep)*const.DT) + self.SIGMA*self.rng.standard_normal(), 0.0, 1.0 ) )
