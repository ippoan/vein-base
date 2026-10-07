"""Fail if a printed part has a wall thinner than the minimum (DMM.make resin SLA: 1.0 mm).
Usage: python3 tools/check_thickness.py [--cache DIR] [--jobs N] MIN_MM part.stl [part.stl ...]

--cache DIR: a part that passed leaves a file in DIR named after sha256(the STL's bytes, this script's bytes, MIN_MM);
the next run skips a part whose key is there (the same bytes passed the same check before) and says so. A failure is
never cached. CadQuery writes the same STL bytes for the same model, so unchanged parts hit (CI keeps DIR with
actions/cache). --jobs N: parts checked in parallel (default 4; one part takes under 0.9 GB, a CI runner has 16 GB).

The interference checks only see collisions, so thin walls went unnoticed until DMM cancelled orders
(0020433268, 0020433323). A ray straight through each face is not enough: v0.8 had 0.5 mm between a counterbore
rim and a boss root diagonally, and the ray said 1.25. So: sample the surface densely, pair points whose normals
face away from each other across the material (dot < -0.3), keep pairs whose midpoint is inside the solid, and
take the smallest distance.
"""
import argparse, hashlib, os, sys
from multiprocessing import Pool
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


def check(job):
    """(report lines, passed) for one part."""
    path, limit = job
    d, mid = thin_spots(path, limit)
    lines = [f'{path}: min {d.min():.2f} mm' if len(d) else f'{path}: OK (no wall under {limit} mm)']
    ok = True
    for i in np.argsort(d)[:5]:
        if d[i] < limit - 0.02:          # sampling noise on a wall of exactly `limit`
            lines.append(f'  THIN {d[i]:.2f} mm at x={mid[i][0]:.1f} y={mid[i][1]:.1f} z={mid[i][2]:.1f}')
            ok = False
    return lines, ok


def cache_key(path, limit):
    h = hashlib.sha256()
    for part in (open(path, 'rb').read(), open(__file__, 'rb').read(), repr(limit).encode()):
        h.update(hashlib.sha256(part).digest())
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cache', help='directory of passed parts (see the docstring)')
    ap.add_argument('--jobs', type=int, default=4)
    ap.add_argument('limit', type=float)
    ap.add_argument('paths', nargs='+')
    a = ap.parse_args()
    limit, bad, todo = a.limit, [], []
    for path in a.paths:
        if a.cache and os.path.exists(os.path.join(a.cache, cache_key(path, limit))):
            print(f'{path}: OK (cached: the same bytes passed before)')
        else:
            todo.append(path)
    with Pool(max(1, min(a.jobs, len(todo)))) as pool:
        for path, (lines, ok) in zip(todo, pool.imap(check, [(p, limit) for p in todo])):
            print('\n'.join(lines), flush=True)
            if not ok:
                bad.append(path)
            elif a.cache:
                os.makedirs(a.cache, exist_ok=True)
                open(os.path.join(a.cache, cache_key(path, limit)), 'w').write(path + '\n')
    if bad:
        raise SystemExit(f'walls thinner than {limit} mm in: {", ".join(sorted(set(bad)))}')


if __name__ == '__main__':
    main()
