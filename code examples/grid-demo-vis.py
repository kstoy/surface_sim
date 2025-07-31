import numpy as np
import time
from pygltflib import GLTF2, Scene, Node, Mesh, Buffer, BufferView, Accessor, Asset, Animation, AnimationChannel, AnimationSampler, Primitive, Attributes
import catenary as cat

D  = 1.0            # distance between rods in meters

LF = 2            # fabric length factor (e.g. 1 means the fabric is equal to distance, 4 that there is four times more)
DT = 0.1            # simulation time step in seconds
GRIDSIDE = 5

a_ball = np.array( [ 0.0, 0.0] )
v_ball = np.array( [ 0.0, 0.0] )
p_ball = np.array( [ 0.5, 1.0] )

rods = np.empty( (GRIDSIDE,GRIDSIDE), dtype=object )

for i in range(GRIDSIDE):
    for j in range(GRIDSIDE):
        rods[i,j] = np.array([float(i)* D, (GRIDSIDE-1-float(j))*D, np.random.random()*2 ])

def indextoposition( indices ):
    return( rods[indices[0], indices[1]] )

def positiontoindex( position ):
    return( np.array( [int( position[0] / D ), GRIDSIDE-1-int( position[1] / D )]))

# the mesh
triangles = []
for i in range(GRIDSIDE-1):
    for j in range(GRIDSIDE-1):
        rod_sw = rods[i][j+1]
        rod_nw = rods[i][j]
        rod_se = rods[i+1][j+1]
        rod_ne = rods[i+1][j]
        cat_w = cat.findcatenaryparameters( LF, D, rod_sw[2], rod_nw[2] )  
        cat_e = cat.findcatenaryparameters( LF, D, rod_se[2], rod_ne[2] )  

        drange = np.linspace( 0.0, D, 20, endpoint=False )
        dy = float(D)/20
        dx = dy

        for y in drange:
            height_w_y = cat.catenary( y, cat_w )
            height_e_y = cat.catenary( y, cat_e )
            cat_we_y = cat.findcatenaryparameters( LF, D, height_w_y, height_e_y )  

            height_w_dy = cat.catenary( y+dy, cat_w )
            height_e_dy = cat.catenary( y+dy, cat_e )
            cat_we_dy = cat.findcatenaryparameters( LF, D, height_w_dy, height_e_dy )  

            for x in drange:
                triangles.append( (x + i*D, y + (GRIDSIDE-1-j)*D, cat.catenary( x, cat_we_y)))
                triangles.append( (x+dx + i*D, y + (GRIDSIDE-1-j)*D, cat.catenary( x+dx, cat_we_y)))
                triangles.append( (x+dx + i*D, y+dy + (GRIDSIDE-1-j)*D, cat.catenary( x+dx, cat_we_dy)))

                triangles.append( (x + i*D, y+dy + (GRIDSIDE-1-j)*D, cat.catenary( x, cat_we_dy)))
                triangles.append( (x + i*D, y + (GRIDSIDE-1-j)*D, cat.catenary( x, cat_we_y)))
                triangles.append( (x+dx + i*D, y+dy + (GRIDSIDE-1-j)*D, cat.catenary( x+dx, cat_we_dy)))

start = time.time()

path = []

for step in range(450):  # in ball timestep is 0.1 so this is 20 seconds
    (ball_x_index,ball_y_index) = positiontoindex( p_ball )

    p_ball_local = p_ball - np.array([ ball_x_index * D, (GRIDSIDE-1-float(ball_y_index))*D ])

    # find heights of surrounding rods
    rod_sw = rods[ball_x_index][ball_y_index]
    rod_nw = rods[ball_x_index][ball_y_index-1]
    rod_se = rods[ball_x_index+1][ball_y_index]
    rod_ne = rods[ball_x_index+1][ball_y_index-1]

    cat_w = cat.findcatenaryparameters( LF, D, rod_sw[2], rod_nw[2] )  
    cat_e = cat.findcatenaryparameters( LF, D, rod_se[2], rod_ne[2] )  
    height_w_y = cat.catenary( p_ball_local[1], cat_w )
    height_e_y = cat.catenary( p_ball_local[1], cat_e )
    cat_we_y = cat.findcatenaryparameters( LF, D, height_w_y, height_e_y )  

    cat_n = cat.findcatenaryparameters( LF, D, rod_nw[2], rod_ne[2] )  
    cat_s = cat.findcatenaryparameters( LF, D, rod_sw[2], rod_se[2] )  
    height_n_y = cat.catenary( p_ball_local[0], cat_n )
    height_s_y = cat.catenary( p_ball_local[0], cat_s )
    cat_sn_y = cat.findcatenaryparameters( LF, D, height_s_y, height_n_y )  

    grad_x = cat.dcatenary( p_ball_local[0], cat_we_y)
    grad_y = cat.dcatenary( p_ball_local[1], cat_sn_y)
    ball_z = cat.catenary( p_ball_local[0], cat_we_y)
    
    grad = np.array( [grad_x, grad_y])

    # Calculate accelerations F = m*a = -m*g*sin(angle) hence a = -k*sin(angle) where k=mg
    a_ball = - 0.1 * np.sin( np.arctan( grad ) )

    # Update velocities
    v_ball += a_ball * DT
    
    # Update positions
    p_ball += v_ball * DT

    path.append( [p_ball[0],p_ball[1],ball_z] )

end = time.time()
print("time elapsed: " + str( end - start ))

# Flatten the data
flat_positions = np.array(path).flatten().astype(np.float32)
position_bytes = flat_positions.tobytes()

# Create buffer
buffer = Buffer(byteLength=len(position_bytes))

# Create buffer view
position_view = BufferView(buffer=0, byteOffset=0, byteLength=len(position_bytes))

# Create accessor
position_accessor = Accessor(
    bufferView=0,
    byteOffset=0,
    componentType=5126,  # FLOAT
    count=len(path),
    type="VEC3",
    max=[float(np.max(flat_positions)), float(np.max(flat_positions)), float(np.max(flat_positions))],
    min=[float(np.min(flat_positions)), float(np.min(flat_positions)), float(np.min(flat_positions))] 
)

# Create mesh primitive with POINTS mode
primitive = Primitive(attributes=Attributes(POSITION=0), mode=0)  # mode=0 for POINTS
mesh = Mesh(primitives=[primitive])

# Create node and scene
node = Node(mesh=0)
scene = Scene(nodes=[0])

# Create glTF object
gltf = GLTF2(
    asset=Asset(),
    buffers=[buffer],
    bufferViews=[position_view],
    accessors=[position_accessor],
    meshes=[mesh],
    nodes=[node],
    scenes=[scene],
    scene=0
)

# Save binary buffer to .bin file
with open("static_points.bin", "wb") as f:
    f.write(position_bytes)

# Link buffer URI
gltf.buffers[0].uri = "static_points.bin"

# Save glTF file
gltf.save("static_points.gltf")

print("static_points.gltf and static_points.bin have been created.")

#file = open("demo_3x3.dat", "w" )
#for entry in path:
#    file.write( str( entry[0] ) + " " + str( entry[1] ) + " " + str( entry[2] ) + "\n")
#file.close()
