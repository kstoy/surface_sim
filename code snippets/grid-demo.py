import numpy as np
import time
import catenary as cat
import catenarysurface as catsurf
import ball

D  = 1.0            # distance between rods in meters
LF = 4.0            # fabric length factor (e.g. 1 means the fabric is equal to distance, 4 that there is four times more)
DT = 0.1            # simulation time step in seconds

a_ball = np.array( [ 0.0, 0.0] )
v_ball = np.array( [ 0.0, 0.0] )
p_ball = np.array( [ 0.5, 1.0] )

rods = np.empty( (3,3), dtype=object )

for i in range(3):
    for j in range(3):
        rods[i,j] = np.array([float(i)* D, (2-float(j))*D, np.random.random() ])

def indextoposition( indices ):
    return( rods[indices[0], indices[1]] )

def positiontoindex( position ):
    return( np.array( [int( position[0] / D ), 2-int( position[1] / D )]))

def point_in_triangle(p, a, b, c):
    # Using barycentric coordinates to check if point p is in triangle abc
    v0 = c - a
    v1 = b - a
    v2 = p - a

    dot00 = np.dot(v0, v0)
    dot01 = np.dot(v0, v1)
    dot02 = np.dot(v0, v2)
    dot11 = np.dot(v1, v1)
    dot12 = np.dot(v1, v2)

    denom = dot00 * dot11 - dot01 * dot01
    if denom == 0:
        return False # Degenerate triangle
    u = (dot11 * dot02 - dot01 * dot12) / denom
    v = (dot00 * dot12 - dot01 * dot02) / denom

    return (u >= 0) and (v >= 0) and (u + v <= 1)


start = time.time()

path = []

for step in range(450):  # in ball timestep is 0.1 so this is 20 seconds
    (ball_x_index,ball_y_index) = positiontoindex( p_ball )

    # find heights of surrounding rods
    rod_sw = rods[ball_x_index][ball_y_index]
    rod_nw = rods[ball_x_index][ball_y_index-1]
    rod_se = rods[ball_x_index+1][ball_y_index]
    rod_ne = rods[ball_x_index+1][ball_y_index-1]
    cat1 = cat.findcatenaryparameters( LF, 2*np.sqrt(2*D), rod_nw[2], rod_se[2] )  
    cat2 = cat.findcatenaryparameters( LF, 2*np.sqrt(2*D), rod_sw[2], rod_ne[2] )  
    rod_center_height = np.max( [cat.catenary( np.sqrt(2), cat1 ), cat.catenary( np.sqrt(2), cat2 ) ] )
    rod_center = np.array([rod_sw[0]+D/2, rod_sw[1]+D/2, rod_center_height])

    triangles = [ np.array([rod_ne, rod_center, rod_nw]), 
        np.array([rod_nw, rod_center, rod_sw]),
        np.array([rod_sw, rod_center, rod_se]), 
        np.array([rod_se, rod_center, rod_ne])]

    # Check which triangle contains the point
    triangle = []
    found = False
    for i, (a, b, c) in enumerate(triangles):
        if point_in_triangle(p_ball, a[:2], b[:2], c[:2]):
            triangle = triangles[i]
            found = True
            break

    if not found:
        break

    # convert to local frame
    ball_vector = p_ball - triangle[1][:2]
    p_r = np.sqrt( np.dot( ball_vector, ball_vector ) )
    vector = triangle[0][:2]-triangle[1][:2]
    p_q = np.arctan2(vector[0]*ball_vector[1] - vector[1]*ball_vector[0], np.dot(vector, ball_vector))

    D_DIAGONAL = np.sqrt(2*0.5**2)

    (grad_r, grad_q) = catsurf.grad(p_r, p_q, LF, D_DIAGONAL, D, D_DIAGONAL, triangle[1][2], triangle[0][2], triangle[2][2])
    p_z = catsurf.findz(p_r, p_q, LF, D_DIAGONAL, D, D_DIAGONAL, triangle[1][2], triangle[0][2], triangle[2][2]) # which means the z position is one time step delayed

    # Calculate accelerations F = m*a = -m*g*sin(angle) hence a = -k*sin(angle) where k=mg
    a_r = - 0.1 * np.sin( np.arctan( grad_r ) )
    a_q = - 0.1 * np.sin( np.arctan( grad_q ) )

    # transform accelerations back to carthesian coordinates
    q = np.pi/4 + float(i)*np.pi/2 + p_q

    a_ball = np.array( [a_r * np.cos(q) - a_q*np.sin(q), a_r * np.sin(q) + a_q*np.cos(q) ] )

    # Update velocities
    v_ball += a_ball * DT
    
    # Update positions
    p_ball += v_ball * DT

    path.append( [p_ball[0],p_ball[1],p_z] )

end = time.time()

file = open("demo_3x3.dat", "w" )
for entry in path:
    file.write( str( entry[0] ) + " " + str( entry[1] ) + " " + str( entry[2] ) + "\n")
file.close()

print("time elapsed: " + str( end - start ))
