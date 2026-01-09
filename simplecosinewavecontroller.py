import numpy as np
import constants as const

class simplecosinewavecontroller:
    def __init__(self, coeffs):
        self.rng = np.random.default_rng()
        self.coeffs = coeffs

    def cosinewave( self, x, y, timestep ):
        t = float( timestep ) * const.DT

        return( (1.0 + np.cos(  np.pi * float(x) + np.pi * t))/2.0 )
    
    def update( self, i, j, timestep):
        return( np.clip(  self.rng.normal( self.cosinewave( i, j, timestep ), const.SIGMA), 0.0, 1.0 ) )

