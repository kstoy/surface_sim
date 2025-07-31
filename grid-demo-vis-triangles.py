import numpy as np
import time
import pygltflib as gltf
import catenary as cat

D  = 1.0            # distance between rods in meters

LF = 2            # fabric length factor (e.g. 1 means the fabric is equal to distance, 4 that there is four times more)
DT = 0.1            # simulation time step in seconds
GRIDSIDE = 5

a_ball = np.array( [ 0.0, 0.0] )
v_ball = np.array( [ 0.0, 0.0] )
p_ball = np.array( [ 2.0, 2.0] )

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
                triangles.append( (x + i*D, y + (GRIDSIDE-2-j)*D, cat.catenary( x, cat_we_y)))
                triangles.append( (x+dx + i*D, y + (GRIDSIDE-2-j)*D, cat.catenary( x+dx, cat_we_y)))
                triangles.append( (x+dx + i*D, y+dy + (GRIDSIDE-2-j)*D, cat.catenary( x+dx, cat_we_dy)))

                triangles.append( (x + i*D, y+dy + (GRIDSIDE-2-j)*D, cat.catenary( x, cat_we_dy)))
                triangles.append( (x + i*D, y + (GRIDSIDE-2-j)*D, cat.catenary( x, cat_we_y)))
                triangles.append( (x+dx + i*D, y+dy + (GRIDSIDE-2-j)*D, cat.catenary( x+dx, cat_we_dy)))

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
    ball_z = cat.catenary( p_ball_local[0], cat_we_y) + 0.2 # ball radius
    
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

vertices = np.array(triangles, dtype=np.float32)
indices = np.array( np.arange(len(vertices)), dtype=np.uint32)
ball_positions = np.array(path, dtype=np.float32)

points_binary_blob = vertices.tobytes()
triangles_binary_blob = indices.flatten().tobytes()
ball_position_bytes = ball_positions.tobytes()

# Create node and scene
node = gltf.Node(mesh=0)
scene = gltf.Scene(nodes=[0])

gltfobj = gltf.GLTF2(
    scene=0,
    scenes=[gltf.Scene(nodes=[0])],
    nodes=[gltf.Node(mesh=0)],
    materials = [
        gltf.Material(
            pbrMetallicRoughness=gltf.PbrMetallicRoughness(
                baseColorFactor=[1.0, 0.0, 0.0, 1.0],  # Red
                metallicFactor=0.0,
                roughnessFactor=1.0
            )
        )
    ],
    meshes=[
        gltf.Mesh(
            primitives=[
                gltf.Primitive(
                    attributes=gltf.Attributes(POSITION=1), indices=0
                ),
                gltf.Primitive(
                    attributes=gltf.Attributes(POSITION=2), mode=0, material=0  # mode=0 for POINTS
                )
            ]
        ),
    ],
    accessors=[
        gltf.Accessor(
            bufferView=0,
            componentType=gltf.UNSIGNED_INT,
            count=indices.size,
            type=gltf.SCALAR,
            max=[int(indices.max())],
            min=[int(indices.min())],
        ),
        gltf.Accessor(
            bufferView=1,
            componentType=gltf.FLOAT,
            count=len(vertices),
            type=gltf.VEC3,
            max=vertices.max(axis=0).tolist(),
            min=vertices.min(axis=0).tolist(),
        ),
        gltf.Accessor(
            bufferView=2,
            componentType=gltf.FLOAT,
            count=len(path),
            type="VEC3",
            max=ball_positions.max(axis=0).tolist(),
            min=ball_positions.min(axis=0).tolist(),
        )
    ],
    bufferViews=[
        gltf.BufferView(
            buffer=0,
            byteLength=len(triangles_binary_blob),
            target=gltf.ELEMENT_ARRAY_BUFFER,
        ),
        gltf.BufferView(
            buffer=0,
            byteOffset=len(triangles_binary_blob),
            byteLength=len(points_binary_blob),
            target=gltf.ARRAY_BUFFER,
        ),
        gltf.BufferView(
            buffer=0,
            byteOffset=len(triangles_binary_blob)+len(points_binary_blob),
            byteLength=len(ball_position_bytes),
            target=gltf.ARRAY_BUFFER,
        ),
    ],
    buffers=[
        gltf.Buffer(
            byteLength=len(triangles_binary_blob) + len(points_binary_blob) + len(ball_position_bytes)
        )
    ]
)

# Save binary buffer to .bin file
with open("static_triangles.bin", "wb") as f:
    f.write(triangles_binary_blob)
    f.write(points_binary_blob)
    f.write(ball_position_bytes)

# Link buffer URI
gltfobj.buffers[0].uri = "static_triangles.bin"

# Save glTF file
gltfobj.save("static_triangles.gltf")

print("static_triangles.gltf and static_triangles.bin have been created.")