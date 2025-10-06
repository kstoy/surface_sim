import numpy as np

import ballstate as bs

# ===============================================================
# Broadphase: uniform grid in XY
# ===============================================================

def grid_pairs_xy(positions, radii, cell_size, margin, ax_x=0, ax_y=1):
    """
    Simple uniform grid broadphase on the horizontal plane. Returns candidate (i,j) pairs.
    """
    N = positions.shape[0]
    cells = {}
    for i in range(N):
        x = positions[i, ax_x]; y = positions[i, ax_y]
        kx = int(np.floor(x/cell_size))
        ky = int(np.floor(y/cell_size))
        cells.setdefault((kx,ky), []).append(i)

    pairs = []
    neighbors = [(-1,-1),(-1,0),(-1,1),
                 ( 0,-1),( 0,0),( 0,1),
                 ( 1,-1),( 1,0),( 1,1)]
    for (kx,ky), idxs in cells.items():
        for dx,dy in neighbors:
            lst = cells.get((kx+dx, ky+dy))
            if lst is None: continue
            for i in idxs:
                for j in lst:
                    if j <= i: continue
                    sumR = radii[i] + radii[j] + margin
                    dx_ = positions[i, ax_x] - positions[j, ax_x]
                    dy_ = positions[i, ax_y] - positions[j, ax_y]
                    if dx_*dx_ + dy_*dy_ <= sumR*sumR:
                        pairs.append((i,j))
    return pairs


# ===============================================================
# Penalty-based step (spring–damper + linear friction, no spin)
# ===============================================================

def step(
    S: bs.BallsState,
    surfacejets,
    dt=1/240,
    gravity=9.81,    
    k_p=1e5,           # normal stiffness (N/m)
    k_d=1e2,           # normal damping (N·s/m)
    mu=0.5,            # Coulomb friction coefficient (linear only)
    substeps=1,
    pair_margin=0.05,
    use_grid_broadphase=True
):
    """
    Advances the simulation by dt using penalty-based contact forces.
    Applies gravity, spring-damper normal forces, and linear friction (no torques).
    - heightfield: tuple (f, fx, fy)
    - substeps: internal sub-steps for stability (reduces tunneling)
    """
    h = dt / max(1, int(substeps))
    ax_x, ax_y, ax_z = [0,1,2]

    gvec = np.zeros(3)
    gvec[ax_z] = -abs(gravity)

    for _ in range(substeps):
        # Force accumulator
        F = np.zeros_like(S.r)

        # Gravity
        F += S.m[:, None] * gvec

        # --- Ball–surface contacts ---
        for i in range(S.N):
            x = float(S.r[i, ax_x]); y = float(S.r[i, ax_y]); z = float(S.r[i, ax_z])
            [z_s, fx_i, fy_i] = surfacejets[i]

            ntil = np.zeros(3)
            ntil[ax_x] = -fx_i; ntil[ax_y] = -fy_i; ntil[ax_z] = 1.0
            nlen = np.linalg.norm(ntil)
            if nlen < 1e-12:
                continue
            n = ntil / nlen

            # Along-normal gap: C = ((z - z_s)/||ntil||) - R
            C = (z - z_s)/nlen - S.R[i]
            if C < 0.0:
                # Penetration depth = -C  (meters)
                v_n = np.dot(S.v[i], n)                # normal speed of COM
                F_n = -k_p * C * n - k_d * v_n * n     # spring-damper
                F[i] += F_n

                # Linear Coulomb friction (no spin)
                v_t = S.v[i] - v_n * n
                v_t_mag = np.linalg.norm(v_t)
                if v_t_mag > 1e-8:
                    dir_t = v_t / v_t_mag
                    F_t = -mu * np.linalg.norm(F_n) * dir_t
                    F[i] += F_t

        # --- Ball–ball contacts ---
        if use_grid_broadphase:
            cell = 2.0 * float(np.max(S.R)) + pair_margin
            pair_idx = grid_pairs_xy(S.r, S.R, cell_size=cell, margin=pair_margin, ax_x=ax_x, ax_y=ax_y)
        else:
            pair_idx = []
            for i in range(S.N):
                for j in range(i+1, S.N):
                    d = S.r[i] - S.r[j]
                    if np.dot(d,d) <= (S.R[i] + S.R[j] + pair_margin)**2:
                        pair_idx.append((i,j))

        for (i, j) in pair_idx:
            d = S.r[i] - S.r[j]
            dist = np.linalg.norm(d)
            sumR = S.R[i] + S.R[j]
            if dist < 1e-12:
                n = np.array([1.0, 0.0, 0.0])  # arbitrary
                C = -sumR
            else:
                n = d / dist
                C = dist - sumR

            if C < 0.0:
                v_rel = S.v[i] - S.v[j]
                v_n = np.dot(v_rel, n)
                F_n = -k_p * C * n - k_d * v_n * n
                F[i] += F_n
                F[j] -= F_n

                # Linear friction on relative tangential motion
                v_t = v_rel - v_n * n
                v_t_mag = np.linalg.norm(v_t)
                if v_t_mag > 1e-8:
                    dir_t = v_t / v_t_mag
                    F_t = -mu * np.linalg.norm(F_n) * dir_t
                    F[i] += F_t
                    F[j] -= F_t

        # Integrate (semi-implicit Euler)
        S.v += h * F * S.inv_m[:, None]
        S.r += h * S.v

