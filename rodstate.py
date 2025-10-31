import numpy as np

from constants import *
from neuralnetworkcontroller import neuralnetworkcontroller as controller
import catenarysurface 

class RodsState:
    def __init__(self, coeffs):        
        self.rods = np.empty( (GRIDSIZEX,GRIDSIZEY, 3), dtype=float )

        # Create index grids
        self.i_indices, self.j_indices = np.meshgrid(np.arange(GRIDSIZEX), np.arange(GRIDSIZEY), indexing='ij')

        self.rods[:,:,0] = self.i_indices * D
        self.rods[:,:,1] = self.j_indices * D
        self.rods[:,:,2] = 1.0

        self.coeffs = coeffs

        self.timestep = 0.0

        self.controller = controller( coeffs )

    def settimestep(self,  timestep):
         self.timestep = timestep

    def update( self ):
        # surface control 
        for i in range(GRIDSIZEX):
            for j in range(GRIDSIZEY):
                t = float(self.timestep)*DT
                self.rods[i][j][2] = self.controller.update( i, j, self.timestep )

    def positiontoindex( self, x, y ):
        return( np.array( [int( x / D ), int( y / D )]))        

    def surfacejet( self, x, y ):
        if x < 0.0 or x > D*(GRIDSIZEX-1) or y < 0.0 or y > D*(GRIDSIZEY-1):
            jet = np.array([-2.0, 0.0, 0.0])
        else:
            (x_idx,y_idx) = self.positiontoindex( x, y )

            x_local = x - float( x_idx * D )
            y_local = y - float( y_idx * D )
        
            # find heights of surrounding rods
            rodheights = np.array([
                self.controller.update( x_idx, y_idx, self.timestep ),
                self.controller.update( x_idx+1, y_idx, self.timestep ),
                self.controller.update( x_idx, y_idx+1, self.timestep ),
                self.controller.update( x_idx+1, y_idx+1, self.timestep ),
            ])
            jet = catenarysurface.jet1( x_local, y_local, rodheights)    

        return( jet )

