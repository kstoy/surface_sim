import numpy as np
import constants as const

class cosinewavecontroller:
    def __init__(self, coeffs):
        self.rng = np.random.default_rng()
        self.coeffs = coeffs

    def cosinewave( self, x, y, timestep ):
        my, sigma, kx, wx, phix = self.coeffs

        t = float( timestep ) * const.DT

        return( np.exp(-(t-my)**2/(2*(sigma**2))) * (1.0 + np.sin( kx*float(x) + wx*t + phix))/2.0 )
    
    def update( self, i, j, timestep):
        return( np.clip(  self.rng.normal( self.cosinewave( i, j, timestep ), const.SIGMA), 0.0, 1.0 ) )

