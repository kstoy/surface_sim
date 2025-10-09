import numpy as np
import constants as const

class neuralnetworkcontroller:
        def __init__(self, coeffs):
            self.rng = np.random.default_rng()
            self.coeffs = coeffs

        def sigmoid(x):
            return 1 / (1 + np.exp(-x))

        def update( self, x, y, timestep ):
            w, x0, w13, w23, w33 = self.coeffs[0:5]
            t = float( timestep ) * const.DT

            input = np.array( [(x / (const.D*const.GRIDSIZEX-1) - 0.5)*2, (t / (const.MAXSIMULATIONSTEPS*const.DT) - 0.5)*2, (np.cos( w*t + x0 )/2 + 0.5), -1.0] )

            w1 = np.array( self.coeffs[5:9] )
            w2 = np.array( self.coeffs[9:13] )

            return( np.clip( neuralnetworkcontroller.sigmoid( w13 * neuralnetworkcontroller.sigmoid( np.dot( w1, input) ) + w23 * neuralnetworkcontroller.sigmoid(  np.dot( w2, input ) ) + w33 * -1.0) + + const.SIGMA*self.rng.standard_normal(), 0.0, 1.0 ) ) 
        