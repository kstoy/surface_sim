import numpy as np
import catenary as cat
import pygltflib as gltf
from constants import *

def generategltffiles( filenameroot, rodspath, ballpath ):
    print("calculating visualization..", end="")
    simsteps=len(ballpath)

    # generate ball visualization - points of the triangles constituting the surface of a sphere
    phis = np.linspace(0, np.pi, TRIANGLES, endpoint=False)      # latitude
    thetas = np.linspace(0, 2 * np.pi, TRIANGLES, endpoint=False)  # longitude
    dtheta = 2*np.pi/TRIANGLES
    dphi = np.pi/TRIANGLES

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

    # generate the points of the surface in the format of a triangle strip array
    def generatetrianglestripsurface( rods ):
        surface_triangles = []

        yrangenoflip = np.linspace( 0.0, D, TRIANGLES, endpoint=False )
        yrangeflip = np.flip( yrangenoflip )
        xrangenoflip = np.linspace( 0.0, D, TRIANGLES, endpoint=True )
        xrangeflip = np.flip( xrangenoflip )

        modulelist = []
        for i in range(GRIDSIZEX-1):
            if i % 2 == 0:
                flipy = True
                flipx = False
                for j in range(GRIDSIZEY-1):
                    modulelist.append((i,j,flipx,flipy))
                    flipx = not flipx
            else:
                flipy = False
                flipx = False
                for j in reversed( range(GRIDSIZEY-1) ):
                    modulelist.append((i,j,flipx, flipy))
                    flipx = not flipx

        # assume number of modules per side is even - number of rods is uneven
        for i,j,flipx,flipy in modulelist:
                rod_nw = rods[i][j+1]
                rod_sw = rods[i][j]
                rod_se = rods[i+1][j]
                rod_ne = rods[i+1][j+1]

                cat_w = cat.findcatenaryparameters( LF, D, rod_sw[2], rod_nw[2] )  
                cat_e = cat.findcatenaryparameters( LF, D, rod_se[2], rod_ne[2] )  

                dy = float(D)/TRIANGLES
                dx = dy

                localflipx = flipx

                if not flipy:
                    yrange = yrangeflip
                else:
                    yrange = yrangenoflip

                for y in yrange:
                    height_w_y = cat.catenary( y, cat_w )
                    height_e_y = cat.catenary( y, cat_e )
                    cat_we_y = cat.findcatenaryparameters( LF, D, height_w_y, height_e_y )  

                    height_w_dy = cat.catenary( y+dy, cat_w )
                    height_e_dy = cat.catenary( y+dy, cat_e )
                    cat_we_dy = cat.findcatenaryparameters( LF, D, height_w_dy, height_e_dy )  

                    if localflipx:
                        for x in xrangeflip:
                            surface_triangles.append( ((x + i*(EXPLODE*D)), EXPLODE*y+dy + j*(EXPLODE*D), cat.catenary( x, cat_we_dy)))
                            surface_triangles.append( ((x + i*(EXPLODE*D)), EXPLODE*y + j*(EXPLODE*D), cat.catenary( x, cat_we_y)))
                        localflipx = False
                    else:
                        for x in xrangenoflip:
                            surface_triangles.append( ((x + i*(EXPLODE*D)), EXPLODE*y + j*(EXPLODE*D), cat.catenary( x, cat_we_y)))
                            surface_triangles.append( ((x + i*(EXPLODE*D)), EXPLODE*y+dy + j*(EXPLODE*D), cat.catenary( x, cat_we_dy)))
                        localflipx = True

        return( surface_triangles )

    trianglestrips = []
    first = True
    for rod in rodspath:
        atrianglestrip = generatetrianglestripsurface( rod )
        if first:
            basistrianglestrip = []
            for vector in atrianglestrip:
                basistrianglestrip.append( (vector[0]*0.5, vector[1]*0.5, 0.0 ))
            trianglestrips.append( basistrianglestrip )
            first = False

        scaled_array = [[x * 0.5 for x in row] for row in atrianglestrip]
        trianglestrips.append( scaled_array )

    weightarrays = []
    for i in range(simsteps):
        weights = [0.0]*simsteps
        weights[i] = 1.0
        weightarrays.append( weights )

    # save visualization in the gltf format

    # step 1: change all data to byte format and save it in binary format

    surface_vertices = np.array(trianglestrips, dtype=np.float32)
    surface_vertices_binary_blob = surface_vertices.flatten().tobytes()

    surface_indices = np.array( np.arange(len(surface_vertices[0])), dtype=np.uint32)
    surface_indices_binary_blob = surface_indices.flatten().tobytes()

    ball_vertices = np.array(ball_triangles, dtype=np.float32)
    ball_vertices_binary_blob = ball_vertices.tobytes()

    ball_indices = np.array( np.arange(len(ball_vertices)), dtype=np.uint32)
    ball_indices_binary_blob = ball_indices.flatten().tobytes()

    ball_timestamps = np.linspace(0, len(ballpath)*DT*RECORDFRAME, len(ballpath), dtype=np.float32)
    ball_timestamps_binary_blob = ball_timestamps.tobytes()

    ball_positions = np.array(ballpath, dtype=np.float32)
    ball_positions_binary_blob = ball_positions.tobytes()

    np_weight_arrays = np.array(weightarrays, dtype=np.float32)
    weight_arrays_binary_blob = np_weight_arrays.flatten().tobytes()


    # Save binary buffer to .bin file
    with open("./output/" + filenameroot + ".bin", "wb") as f:
        f.write(surface_indices_binary_blob)
        f.write(surface_vertices_binary_blob)
        f.write(ball_indices_binary_blob)
        f.write(ball_vertices_binary_blob)
        f.write(ball_timestamps_binary_blob)
        f.write(ball_positions_binary_blob)
        f.write(weight_arrays_binary_blob)

    # step 2: generate the gltfobj file and point it to the data and save it 
    gltfobj = gltf.GLTF2()
    gltfobj.scene = 0
    scene = gltf.Scene()

    # ball
    gltfobj.nodes.append( gltf.Node(mesh=0, scale=[ 0.1, 0.1, 0.1 ] ) ) #, translation=path[0]) )
    scene.nodes.append( 0 )

    # robot
    gltfobj.nodes.append( gltf.Node(mesh=1, scale=[ 1.0, 1.0, 2.0 ] ) ) # somehow the triangle array is shown in 2x scale so we have to scale down
    scene.nodes.append( 1 )


    camera_matrix = [
                    0.996529757976532,
                    0,
                    -0.08323691785335541,
                    0,
                    0.056379012763500214,
                    0.7356777191162109,
                    0.6749812960624695,
                    0,
                    0.06123554706573486,
                    -0.677331805229187,
                    0.7331247329711914,
                    0,
                    3.3165924549102783,
                    -3.3049261569976807,
                    6.134603023529053,
                    1
                ]

    gltfobj.nodes.append( gltf.Node( camera=0, matrix=camera_matrix) )
    scene.nodes.append( 2 )
    gltfobj.cameras.append( gltf.Camera(type="orthographic", orthographic=gltf.Orthographic( 
                    xmag = 1.0,
                    ymag = 1.0,
                    zfar= 56.84701458464913,
                    znear= 0.005684701458464913 )))

    gltfobj.scenes.append( scene ) 

    gltfobj.animations.append(
        gltf.Animation(
                samplers = [
                    gltf.AnimationSampler( input=2, interpolation="LINEAR", output=3),
                    gltf.AnimationSampler( input=2, interpolation="LINEAR", output=6),
                ],
                channels = [
                    gltf.AnimationChannel( sampler=0, target=gltf.AnimationChannelTarget(node=0,path="translation") ),
                    gltf.AnimationChannel( sampler=1, target=gltf.AnimationChannelTarget(node=1,path="weights") ),
                ]
        )
    )

    gltfobj.materials.append( 
            gltf.Material(
                pbrMetallicRoughness=gltf.PbrMetallicRoughness(
                    baseColorFactor=[1.0, 0.0, 0.0, 1.0],  # Red
                    metallicFactor=0.0,
                    roughnessFactor=1.0,
                ),
                doubleSided=True,
                alphaMode="MASK",
            )
    )
    
    gltfobj.materials.append( 
        gltf.Material(
                pbrMetallicRoughness=gltf.PbrMetallicRoughness(
                    baseColorFactor=[0.0, 0.0, 0.0, 1.0],  # Black
                    metallicFactor=0.0,
                    roughnessFactor=1.0
                ),
                alphaMode="MASK",
                doubleSided=True,
        )
    )

    # ball
    gltfobj.meshes.append( 
        gltf.Mesh(
            primitives=[
                gltf.Primitive(
                    attributes=gltf.Attributes(POSITION=1), indices=0, material=1, mode=gltf.TRIANGLES
                )
            ]            
        )
    )

    thetargets = []
    for i in range( simsteps ):
        thetargets.append( gltf.Attributes(POSITION=7+i) )

    # surface
    gltfobj.meshes.append( 
        gltf.Mesh(
            primitives=[
                gltf.Primitive(
                    attributes=gltf.Attributes(POSITION=5), indices=4, material=0, mode=gltf.TRIANGLE_STRIP, targets=thetargets
                )
            ],
            weights=weightarrays[0],            
        )
    )

    # 0 - ball - triangle indices
    gltfobj.accessors.append( 
            gltf.Accessor(
                bufferView=2,
                componentType=gltf.UNSIGNED_INT,
                count=ball_indices.size,
                type=gltf.SCALAR,
                max=[int(ball_indices.max())],
                min=[int(ball_indices.min())],
            )
    )

    # 1 - ball - vertices
    gltfobj.accessors.append( 
            gltf.Accessor(
                bufferView=3,
                componentType=gltf.FLOAT,
                count=len(ball_vertices),
                type=gltf.VEC3,
                max=ball_vertices.max(axis=0).tolist(),
                min=ball_vertices.min(axis=0).tolist(),
            )
    )

    # 2 - timesteps
    gltfobj.accessors.append( 
            gltf.Accessor(
                bufferView=4,
                componentType=gltf.FLOAT,
                count=len(ballpath),
                type=gltf.SCALAR,
                max=[len(ballpath)*DT*RECORDFRAME],
                min=[0],
            )
    )

    # 3 - ball path - positions at above timesteps
    gltfobj.accessors.append( 
            gltf.Accessor(
                bufferView=5,
                componentType=gltf.FLOAT,
                count=len(ballpath),
                type=gltf.VEC3,
                max=ball_positions.max(axis=0).tolist(),
                min=ball_positions.min(axis=0).tolist(),
            )
    )

    # 4 - surface indicies
    gltfobj.accessors.append( 
        gltf.Accessor(
            bufferView=0,
            componentType=gltf.UNSIGNED_INT,
            count=len(surface_indices),
            type=gltf.SCALAR,
            max=[int(surface_indices.max())],
            min=[0],
        )
    )

    # 5 - surface vertices
    gltfobj.accessors.append( 
            gltf.Accessor(
                bufferView=1,
                componentType=gltf.FLOAT,
                count=len(surface_vertices[0]),
                type=gltf.VEC3,
                max=surface_vertices[0].max(axis=0).tolist(),
                min=surface_vertices[0].min(axis=0).tolist(),
            )
    )
        
    # 6 - weights
    gltfobj.accessors.append( 
        gltf.Accessor(
            bufferView=6,
            componentType=gltf.FLOAT,
            count=simsteps*simsteps,
            type=gltf.SCALAR,
            max=[1.0],
            min=[0.0],
        )
    )

    # 7 and more
    for i in range(simsteps):
        # surface vertices
        gltfobj.accessors.append( 
            gltf.Accessor(
                bufferView=1,
                componentType=gltf.FLOAT,
                byteOffset=len(surface_vertices[0])*3*4*i,
                count=len(surface_vertices[0]),
                type=gltf.VEC3,
                max=surface_vertices[i].max(axis=0).tolist(),
                min=surface_vertices[i].min(axis=0).tolist(),
            )
        )

    # views of the data in the binary file
    gltfobj.bufferViews.append( 
            gltf.BufferView(
                buffer=0,
                byteLength=len(surface_indices_binary_blob),
                target=gltf.ELEMENT_ARRAY_BUFFER,
            )
    )
    gltfobj.bufferViews.append( 
            gltf.BufferView(
                buffer=0,
                byteStride=12,
                byteOffset=len(surface_indices_binary_blob),
                byteLength=len(surface_vertices_binary_blob),
                target=gltf.ARRAY_BUFFER,
            )
    )
    gltfobj.bufferViews.append( 
            gltf.BufferView(
                buffer=0,
                byteOffset=len(surface_indices_binary_blob) + len(surface_vertices_binary_blob),
                byteLength=len(ball_indices_binary_blob),
                target=gltf.ELEMENT_ARRAY_BUFFER,
            )
    )
    gltfobj.bufferViews.append( 
            gltf.BufferView(
                buffer=0,
                byteOffset=len(surface_indices_binary_blob) + len(surface_vertices_binary_blob) + len(ball_indices_binary_blob),
                byteLength=len(ball_vertices_binary_blob),
                target=gltf.ARRAY_BUFFER,
            )
    )
    gltfobj.bufferViews.append( 
            gltf.BufferView(
                buffer=0,
                byteOffset=len(surface_indices_binary_blob) + len(surface_vertices_binary_blob) + len(ball_indices_binary_blob) + len(ball_vertices_binary_blob),
                byteLength=len(ball_timestamps_binary_blob)
            )
    )
    gltfobj.bufferViews.append( 
            gltf.BufferView(
                buffer=0,
                byteOffset=len(surface_indices_binary_blob) + len(surface_vertices_binary_blob) + len(ball_indices_binary_blob) + len(ball_vertices_binary_blob) + len(ball_timestamps_binary_blob),
                byteLength=len(ball_positions_binary_blob),
            )
    )

    gltfobj.bufferViews.append( 
            gltf.BufferView(
                buffer=0,
                byteOffset=len(surface_indices_binary_blob) + len(surface_vertices_binary_blob) + len(ball_indices_binary_blob) + len(ball_vertices_binary_blob) + len(ball_timestamps_binary_blob) + len(ball_positions_binary_blob),
                byteLength=len(weight_arrays_binary_blob),
            )
    )

    gltfobj.buffers.append(
        gltf.Buffer(
            byteLength=len(surface_indices_binary_blob) + len(surface_vertices_binary_blob) + len(ball_indices_binary_blob) + len(ball_vertices_binary_blob) + len(ball_timestamps_binary_blob) + len(ball_positions_binary_blob) + len(weight_arrays_binary_blob)
        )
    )

    # Link buffer URI
    gltfobj.buffers[0].uri = filenameroot + ".bin"

    # Save glTF file
    gltfobj.save("./output/" + filenameroot + ".gltf")

    print(filenameroot + " gltf files written")

