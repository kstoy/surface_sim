from sys import exit
import numpy as np
import time
import pygltflib as gltf
import catenary as cat

D  = 1.0            # distance between rods in meters

LF = 2              # fabric length factor (e.g. 1 means the fabric is equal to distance, 4 that there is four times more)
DT = 0.1            # simulation time step in seconds
GRIDSIDE = 5

a_ball = np.array( [ 0.0, 0.0] )
v_ball = np.array( [ 0.0, 0.0] )
p_ball = np.array( [ 2.0, 2.0] )

rods = np.empty( (GRIDSIDE,GRIDSIDE), dtype=object )

for i in range(GRIDSIDE):
    for j in range(GRIDSIDE):
        rods[i,j] = np.array([float(i)* D, (GRIDSIDE-1-float(j))*D, np.random.random()*LF/2 ])

def indextoposition( indices ):
    return( rods[indices[0], indices[1]] )

def positiontoindex( position ):
    return( np.array( [int( position[0] / D ), GRIDSIDE-1-int( position[1] / D )]))

# the mesh
surface_triangles = []
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
                surface_triangles.append( (x + i*D, y + (GRIDSIDE-2-j)*D, cat.catenary( x, cat_we_y)))
                surface_triangles.append( (x+dx + i*D, y + (GRIDSIDE-2-j)*D, cat.catenary( x+dx, cat_we_y)))
                surface_triangles.append( (x+dx + i*D, y+dy + (GRIDSIDE-2-j)*D, cat.catenary( x+dx, cat_we_dy)))

                surface_triangles.append( (x + i*D, y+dy + (GRIDSIDE-2-j)*D, cat.catenary( x, cat_we_dy)))
                surface_triangles.append( (x + i*D, y + (GRIDSIDE-2-j)*D, cat.catenary( x, cat_we_y)))
                surface_triangles.append( (x+dx + i*D, y+dy + (GRIDSIDE-2-j)*D, cat.catenary( x+dx, cat_we_dy)))

start = time.time()

path = []

for step in range(450):  # in ball timestep is 0.1 so this is 20 seconds
    if p_ball[0] < 0 or p_ball[0] > D*(GRIDSIDE-1) or p_ball[1] < 0 or p_ball[1] > D*(GRIDSIDE-1):
        break

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
    ball_z = cat.catenary( p_ball_local[0], cat_we_y) + 0.1 # ball radius
    
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

# generate ball visualization 
phis = np.linspace(0, np.pi, 20, endpoint=False)      # latitude
thetas = np.linspace(0, 2 * np.pi, 20, endpoint=False)  # longitude
dtheta = 2*np.pi/20
dphi = np.pi/20

ball_triangles = []
for phi in phis:
    for theta in thetas:
        x = np.sin(phi) * np.cos(theta)
        y = np.sin(phi) * np.sin(theta)
        z = np.cos(phi)
        ball_triangles.append( (x, y, z))

        x = np.sin(phi) * np.cos(theta + dtheta)
        y = np.sin(phi) * np.sin(theta + dtheta)
        z = np.cos(phi)
        ball_triangles.append( (x, y, z))

        x = np.sin(phi + dphi) * np.cos(theta + dtheta)
        y = np.sin(phi + dphi) * np.sin(theta + dtheta)
        z = np.cos(phi + dphi)
        ball_triangles.append( (x, y, z))

        x = np.sin(phi) * np.cos(theta)
        y = np.sin(phi) * np.sin(theta)
        z = np.cos(phi)
        ball_triangles.append( (x, y, z))

        x = np.sin(phi + dphi) * np.cos(theta + dtheta)
        y = np.sin(phi + dphi) * np.sin(theta + dtheta)
        z = np.cos(phi + dphi)
        ball_triangles.append( (x, y, z))

        x = np.sin(phi + dphi) * np.cos(theta)
        y = np.sin(phi + dphi) * np.sin(theta)
        z = np.cos(phi + dphi)
        ball_triangles.append( (x, y, z))

surface_vertices = np.array(surface_triangles, dtype=np.float32)
surface_vertices_binary_blob = surface_vertices.tobytes()

surface_indices = np.array( np.arange(len(surface_vertices)), dtype=np.uint32)
surface_indices_binary_blob = surface_indices.flatten().tobytes()

ball_vertices = np.array(ball_triangles, dtype=np.float32)
ball_vertices_binary_blob = ball_vertices.tobytes()

ball_indices = np.array( np.arange(len(ball_vertices)), dtype=np.uint32)
ball_indices_binary_blob = ball_indices.flatten().tobytes()

ball_timestamps = np.linspace(0, len(path)*DT, len(path), dtype=np.float32)
ball_positions = np.array(path, dtype=np.float32)

ball_timestamps_binary_blob = ball_timestamps.tobytes()
ball_positions_binary_blob = ball_positions.tobytes()

# Create gltfobj

gltfobj = gltf.GLTF2(
    scene=0,
    scenes=[gltf.Scene(nodes=[0,1])],
    nodes=[
        gltf.Node(mesh=0),
        gltf.Node(mesh=1, translation=path[0], scale=[ 0.025, 0.025, 0.025 ])
    ],
    animations=[
        gltf.Animation(
            samplers = [gltf.AnimationSampler( input=4, interpolation="LINEAR", output=5)],
            channels = [gltf.AnimationChannel( sampler=0, target=gltf.AnimationChannelTarget(node=1,path="translation") )]
        )
    ],
    materials = [
        gltf.Material(
            pbrMetallicRoughness=gltf.PbrMetallicRoughness(
                baseColorFactor=[1.0, 0.0, 0.0, 1.0],  # Red
                metallicFactor=0.0,
                roughnessFactor=1.0
            ),
            alphaMode="MASK"
        ),
        gltf.Material(

            pbrMetallicRoughness=gltf.PbrMetallicRoughness(
                baseColorFactor=[0.0, 0.0, 0.0, 1.0],  # Black
                metallicFactor=0.0,
                roughnessFactor=1.0
            ),
            alphaMode="MASK",
            doubleSided=True,
        )
    ],
    meshes=[
        gltf.Mesh(
            primitives=[
                gltf.Primitive(
                    attributes=gltf.Attributes(POSITION=1), indices=0, material=0
                )
            ]            
        ),
        gltf.Mesh(
            primitives=[
                gltf.Primitive(
                    attributes=gltf.Attributes(POSITION=3), indices=2, material=1
                )
            ]            
        ),
    ],
    accessors=[
        gltf.Accessor(
            bufferView=0,
            componentType=gltf.UNSIGNED_INT,
            count=surface_indices.size,
            type=gltf.SCALAR,
            max=[int(surface_indices.max())],
            min=[int(surface_indices.min())],
        ),
        gltf.Accessor(
            bufferView=1,
            componentType=gltf.FLOAT,
            count=len(surface_vertices),
            type=gltf.VEC3,
            max=surface_vertices.max(axis=0).tolist(),
            min=surface_vertices.min(axis=0).tolist(),
        ),
        gltf.Accessor(
            bufferView=2,
            componentType=gltf.UNSIGNED_INT,
            count=ball_indices.size,
            type=gltf.SCALAR,
            max=[int(ball_indices.max())],
            min=[int(ball_indices.min())],
        ),
        gltf.Accessor(
            bufferView=3,
            componentType=gltf.FLOAT,
            count=len(ball_vertices),
            type=gltf.VEC3,
            max=ball_vertices.max(axis=0).tolist(),
            min=ball_vertices.min(axis=0).tolist(),
        ),
        gltf.Accessor(
            bufferView=4,
            componentType=gltf.FLOAT,
            count=len(path),
            type=gltf.SCALAR,
            max=[len(path)*DT],
            min=[0],
        ),
        gltf.Accessor(
            bufferView=5,
            componentType=gltf.FLOAT,
            count=len(path),
            type=gltf.VEC3,
            max=ball_positions.max(axis=0).tolist(),
            min=ball_positions.min(axis=0).tolist(),
        ),
    ],
    bufferViews=[
        gltf.BufferView(
            buffer=0,
            byteLength=len(surface_indices_binary_blob),
            target=gltf.ELEMENT_ARRAY_BUFFER,
        ),
        gltf.BufferView(
            buffer=0,
            byteOffset=len(surface_indices_binary_blob),
            byteLength=len(surface_vertices_binary_blob),
            target=gltf.ARRAY_BUFFER,
        ),
        gltf.BufferView(
            buffer=0,
            byteOffset=len(surface_indices_binary_blob) + len(surface_vertices_binary_blob),
            byteLength=len(ball_indices_binary_blob),
            target=gltf.ELEMENT_ARRAY_BUFFER,
        ),
        gltf.BufferView(
            buffer=0,
            byteOffset=len(surface_indices_binary_blob) + len(surface_vertices_binary_blob) + len(ball_indices_binary_blob),
            byteLength=len(ball_vertices_binary_blob),
            target=gltf.ARRAY_BUFFER,
        ),
        gltf.BufferView(
            buffer=0,
            byteOffset=len(surface_indices_binary_blob) + len(surface_vertices_binary_blob) + len(ball_indices_binary_blob) + len(ball_vertices_binary_blob),
            byteLength=len(ball_timestamps_binary_blob)
        ),
        gltf.BufferView(
            buffer=0,
            byteOffset=len(surface_indices_binary_blob) + len(surface_vertices_binary_blob) + len(ball_indices_binary_blob) + len(ball_vertices_binary_blob) + len(ball_timestamps_binary_blob),
            byteLength=len(ball_positions_binary_blob),
        ),
    ],
    buffers=[
        gltf.Buffer(
            byteLength=len(surface_indices_binary_blob) + len(surface_vertices_binary_blob) + len(ball_indices_binary_blob) + len(ball_vertices_binary_blob) + len(ball_timestamps_binary_blob) + len(ball_positions_binary_blob) 
        )
    ]
)

# Save binary buffer to .bin file
with open("./output/static_triangles.bin", "wb") as f:
    f.write(surface_indices_binary_blob)
    f.write(surface_vertices_binary_blob)
    f.write(ball_indices_binary_blob)
    f.write(ball_vertices_binary_blob)
    f.write(ball_timestamps_binary_blob)
    f.write(ball_positions_binary_blob)

# Link buffer URI
gltfobj.buffers[0].uri = "static_triangles.bin"

# Save glTF file
gltfobj.save("./output/static_triangles.gltf")

print("static_triangles.gltf and static_triangles.bin have been created.")

