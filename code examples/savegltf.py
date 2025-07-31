from pygltflib import GLTF2, Scene, Node, Mesh, Buffer, BufferView, Accessor, Asset, Animation, AnimationChannel, AnimationSampler, Primitive, Attributes
import numpy as np
import trimesh
from scipy.spatial import Delaunay

def savegltf( points ):
    vertices = points.reshape(-1, 3)

    # Create face indices (each triangle uses 3 consecutive vertices)
    nfaces = int(len(vertices)/3)
    faces = np.arange(nfaces*3).reshape(nfaces, 3)

    # Create the mesh
    theta = np.pi/4
    mesh1 = trimesh.Trimesh(vertices=vertices, faces=faces)
    mesh1.apply_transform( ((1,0,0,1), (0,1,0,0), (0,0,1,0), (0,0,0,1)) )
    mesh1.apply_transform( ((np.cos(theta),-np.sin(theta),0,0), (np.sin(theta),np.cos(theta),0,0), (0,0,1,0), (0,0,0,1)) )


    mesh2 = trimesh.Trimesh(vertices=vertices, faces=faces)

    # Export to glTF
    #mesh.export("mesh.glb")
    mesh3 = trimesh.util.concatenate( mesh1, mesh2 )

    mesh3.show()

    """  # Flatten the data
    flat_positions = np.array(points).flatten().astype(np.float32)
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
        count=len(points),
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
 """