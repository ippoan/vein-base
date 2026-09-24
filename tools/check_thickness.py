"""Fail if a printed part has a wall thinner than the minimum (DMM.make resin SLA: 1.0 mm).
Usage: python3 tools/check_thickness.py MIN_MM part.stl [part.stl ...]

The interference checks only see collisions, so thin walls went unnoticed until DMM cancelled orders
(0020433268, 0020433323). A ray straight through each face is not enough: v0.8 had 0.5 mm between a counterbore
rim and a boss root diagonally, and the ray said 1.25. So: sample the surface densely, pair points whose normals
face away from each other across the material (dot < -0.3), keep pairs whose midpoint is inside the solid, and
take the smallest distance.
"""
import sys
import numpy as np
import trimesh
from scipy.spatial import cKDTree

DENSITY = 25          # surface samples per mm² (~0.2 mm spacing): fine enough for a 1 mm wall
CHUNK = 50_000


def thin_spots(path, limit):
    """Distances (and midpoints) of opposing surface-point pairs closer than `limit`, midpoint inside the solid.
    Processed in chunks so memory stays bounded (a CI runner has 16 GB)."""
    m = trimesh.load(path)
    pts, fi = trimesh.sample.sample_surface(m, int(m.area * DENSITY), seed=0)
    nrm = m.face_normals[fi]
    tree = cKDTree(pts)
    ds, mids = [], []
    for s0 in range(0, len(pts), CHUNK):
        idx = np.arange(s0, min(s0 + CHUNK, len(pts)))
        nb_lists = tree.query_ball_point(pts[idx], r=limit)
        ia = np.repeat(idx, [len(l) for l in nb_lists])
        ib = np.fromiter((j for l in nb_lists for j in l), dtype=np.int64, count=len(ia))
        keep = ib > ia
        ia, ib = ia[keep], ib[keep]
        v = pts[ib] - pts[ia]
        d = np.linalg.norm(v, axis=1)
        k = ((np.einsum('ij,ij->i', nrm[ia], nrm[ib]) < -0.3) & (np.einsum('ij,ij->i', nrm[ia], v) < 0)
             & (np.einsum('ij,ij->i', nrm[ib], -v) < 0) & (d > 0.05))
        if k.any():
            ds.append(d[k]); mids.append((pts[ia[k]] + pts[ib[k]]) / 2)
    if not ds:
        return np.zeros(0), np.zeros((0, 3))
    d, mid = np.concatenate(ds), np.concatenate(mids)
    inside = m.contains(mid)
    return d[inside], mid[inside]


def main():
    limit = float(sys.argv[1])
    bad = []
    for path in sys.argv[2:]:
        d, mid = thin_spots(path, limit)
        print(f'{path}: min {d.min():.2f} mm' if len(d) else f'{path}: OK (no wall under {limit} mm)')
        for i in np.argsort(d)[:5]:
            if d[i] < limit - 0.02:          # sampling noise on a wall of exactly `limit`
                print(f'  THIN {d[i]:.2f} mm at x={mid[i][0]:.1f} y={mid[i][1]:.1f} z={mid[i][2]:.1f}')
                bad.append(path)
    if bad:
        raise SystemExit(f'walls thinner than {limit} mm in: {", ".join(sorted(set(bad)))}')


if __name__ == '__main__':
    main()
