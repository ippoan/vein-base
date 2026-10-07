"""Shared by the station scripts: CadQuery box helpers, the vein module as a picture, and the 3D preview page
(tools/station_template.html). z_top is the height the preview puts at 0 (the top face of the assembly)."""
import base64, json, os, shutil
import numpy as np
import cadquery as cq
from m5_cad import stl_tris

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def rbox(x0, x1, y0, y1, z0, z1, r):
    return box(x0, x1, y0, y1, z0, z1).edges('|Z').fillet(r)


def cyl_z(x, y, r, z0, z1):
    return cq.Workplane('XY').workplane(offset=z0).center(x, y).circle(r).extrude(z1 - z0)


def cyl_y(x, y0, y1, z, r):
    return cq.Workplane('XZ').workplane(offset=-y1).center(x, z).circle(r).extrude(y1 - y0)  # XZ normal is -Y


def sym(f):
    """Union of f(sx, sy) over the four quadrants."""
    out = None
    for sx in (1, -1):
        for sy in (1, -1):
            s = f(sx, sy)
            out = s if out is None else out.union(s)
    return out


def quad(x0, x1, y0, y1, z0, z1):
    """Box in the +x +y quadrant (x0..x1, y0..y1 > 0), mirrored to all four."""
    return sym(lambda sx, sy: box(*sorted((sx * x0, sx * x1)), *sorted((sy * y0, sy * y1)), z0, z1))


def union(*shapes):
    out = shapes[0]
    for s in shapes[1:]:
        out = out.union(s)
    return out


def tri(shape, z_top):
    vs, ts = shape.val().tessellate(0.03, 0.15)
    v = np.array([(p.x, p.y, p.z - z_top) for p in vs], dtype=np.float32)
    return v[np.array(ts)].reshape(-1).astype(np.float32)


def stl_at(key, x, y, z, z_top, turn=False):
    """An official M5Stack STL moved to (x, y, z); ports / Grove on -y and the top (label face) on +z as in the file,
    or on +y with turn (half a turn about z)."""
    t = stl_tris(key).copy()
    c = (t.reshape(-1, 3).min(axis=0) + t.reshape(-1, 3).max(axis=0)) / 2
    t[..., :2] -= c[:2] if turn else 0
    if turn:
        t[..., :2] *= -1
    return (t + np.float32([x, y, z - z_top])).reshape(-1).astype(np.float32)


# measured on the module (2026-10): the top 2.0 is a step 1.0 / 0.5 in from the 59 × 26 body (57 × 25), and a groove
# 2 deep runs across the bottom 18..28 from the 9P end (the cable's slack is wound into it)
VEIN_STEP_H, VEIN_STEP_IN = 2.0, (1.0, 0.5)
VEIN_GROOVE = (18.0, 28.0, 2.0)


def vein_step_box(rect, z0):
    """The vein module as measured (59 × 26 × 15 with the 57 × 25 step on top and the groove across the bottom, the
    9P end at x0), long side along x: the solid for interference checks."""
    vx0, vx1, vy0, vy1 = rect
    ix, iy = VEIN_STEP_IN
    g0, g1, gd = VEIN_GROOVE
    return (rbox(*rect, z0, z0 + 15.0 - VEIN_STEP_H, 2.0)
            .union(rbox(vx0 + ix, vx1 - ix, vy0 + iy, vy1 - iy, z0 + 15.0 - VEIN_STEP_H - 0.01, z0 + 15.0, 1.5))
            .cut(box(vx0 + g0, vx0 + g1, vy0 - 1, vy1 + 1, z0 - 1, z0 + gd)))


def vein_parts(rect, z0, along_y=False, step=False):
    """The vein module (x0, x1, y0, y1) standing on z0, long side along x, as a picture only (Waveshare publishes no
    CAD): drawn by hand inside its 59 × 26 × 15 box after the product photos, not measured. A finger scoop over the
    IR lens at +x, the flat dark window at -x, a channel across the bottom and the MX1.25 9P socket low in the -x end
    (the flat window's end, where Waveshare's photo shows the cable leaving level).
    along_y: the long side along y instead (a quarter turn, the socket end at -y).
    step: the measured outline (vein_step_box: the step on top, the groove 18..28 from the 9P end) instead of one box.
    Interference checks use the plain box (or vein_step_box)."""
    if along_y:
        cx, cy = (rect[0] + rect[1]) / 2, (rect[2] + rect[3]) / 2
        hl, hw = (rect[3] - rect[2]) / 2, (rect[1] - rect[0]) / 2
        return [(k, l, c, o, g, s.rotate((cx, cy, 0), (cx, cy, 1), 90))
                for k, l, c, o, g, s in vein_parts((cx - hl, cx + hl, cy - hw, cy + hw), z0, step=step)]
    vx0, vx1, vy0, vy1 = rect
    vz1 = z0 + 15.0
    yc = (vy0 + vy1) / 2
    scoop = (cq.Workplane('XY').workplane(offset=vz1 - 9.0).center(vx1 - 19.0, yc).rect(18.0, 9.0)
             .workplane(offset=9.5).rect(31.0, 21.0).loft())
    if step:
        look = vein_step_box(rect, z0)
    else:
        look = (rbox(*rect, z0, vz1, 2.0).edges('>Z').fillet(1.0)
                .cut(box(vx0 + 26.0, vx0 + 36.0, vy0 - 1, vy1 + 1, z0 - 1, z0 + 1.5)))
    look = look.cut(scoop).cut(box(vx0 + 3.0, vx1 - 36.0, vy0 + 2.5, vy1 - 2.5, vz1 - 0.3, vz1 + 1))
    return [('vein', '指静脈モジュール(外形は公式値、細部は写真からのイメージ、コネクタ位置は未確定)', '#23272a', 1, 'mods', look),
            ('veinwin', '指静脈の平らな窓(イメージ)', '#0b0e10', 1, 'mods',
             box(vx0 + 3.0, vx1 - 36.0, vy0 + 2.5, vy1 - 2.5, vz1 - 0.3, vz1 - 0.05)),
            ('veinlens', '指静脈のレンズ(イメージ)', '#3b4d5e', 1, 'mods', cyl_z(vx1 - 19.0, yc, 3.0, vz1 - 9.0, vz1 - 8.7)),
            ('veinsock', '指静脈の MX1.25 9P(位置はイメージ)', '#f1efe8', 1, 'mods',
             box(vx0 - 0.05, vx0 + 0.5, yc - 6.5, yc + 6.5, z0 + 1.5, z0 + 5.0))]


def write_page(sub_dir, rev, parts, sub, dims, note, z_top, downloads=(), extra='', tz='-18'):
    """site/<sub_dir>/index.html; parts = [(key, label, colour, opacity, group, shape or float32 triangles)],
    downloads = [(label, path)] copied next to the page."""
    model = [dict(key=k, label=l, color=c, opacity=o, group=g,
                   data=base64.b64encode((s if isinstance(s, np.ndarray) else tri(s, z_top)).tobytes()).decode())
             for k, l, c, o, g, s in parts]
    site = os.path.join(ROOT, 'site', sub_dir)
    os.makedirs(site, exist_ok=True)
    rows = []
    for label, p in downloads:
        shutil.copyfile(p, os.path.join(site, os.path.basename(p)))
        rows.append(f'<a href="{os.path.basename(p)}" download>{label}<span>{os.path.basename(p)}</span></a>')
    rows.append(extra)
    table = ''.join(f'        <tr><td>{k}</td><td>{v}</td></tr>\n' for k, v in dims)
    tpl = open(os.path.join(ROOT, 'tools/station_template.html'), encoding='utf-8').read()
    page = os.path.join(site, 'index.html')
    open(page, 'w', encoding='utf-8').write(
        tpl.replace('__MODEL__', json.dumps(model)).replace('__REV__', rev).replace('__SUB__', sub)
        .replace('__DIMS__', table).replace('__NOTE__', note).replace('__TZ__', tz).replace('__DOWNLOADS__', ''.join(rows)))
    print('wrote', page, os.path.getsize(page), 'bytes')


# ---- printed (MJF PA12) cases: a tray and a flat lid screwed down into ledges on the walls ---------------------------
# (station/build_station_print.py, station/build_vein_unit_print.py). z = 0 on the floor's inside face; z_in is the
# lid's underside (the top of the walls), the lid is t_top thick.
T_WALL, T_FLOOR, T_TOP = 1.8, 1.6, 2.2       # the lid 2.2: 1.25 left under a screw's countersink

# the lid's screws: an M2 countersunk tapping screw (M2 x 5) from the top into a ledge on the inside of a wall
LEDGE_D, LEDGE_W, LEDGE_H = 3.9, 6.0, 4.5     # out from the wall, along it, down from the lid (M2 x 5)
SCREW_IN = 1.9                                 # the screw's axis from the wall's inside face (in the wall's 1.8 + ledge)
PILOT, CLEAR, CSK = 1.6, 2.3, 4.2              # tapping pilot, the lid's clearance hole, the countersink (90 deg)


def ledges(xi0, xi1, yi0, yi1, z_in, avoid, lid_cuts=(), n_max=4):
    """Screw ledges along the inside of the walls, clear of every part and wall cut in `avoid` (by bounding box,
    0.3 margin): the free place nearest to each inside corner. Returns [(x, y, ledge box)]."""
    z0 = z_in - LEDGE_H
    bbs = []
    for o in avoid:
        bb = o.val().BoundingBox()
        if bb.zmax > z0 - 0.15:
            bbs.append((bb.xmin - 0.3, bb.xmax + 0.3, bb.ymin - 0.3, bb.ymax + 0.3))
    m = CSK / 2 + 1.0                       # the countersink stays 1.0 off the lid's windows
    wins = [(bb.xmin - m, bb.xmax + m, bb.ymin - m, bb.ymax + m) for bb in (o.val().BoundingBox() for o in lid_cuts)]
    cands = []
    for wall in ('x-', 'x+', 'y-', 'y+'):
        lo, hi = (yi0, yi1) if wall[0] == 'x' else (xi0, xi1)
        for t in np.arange(lo + LEDGE_W / 2 + 1.2, hi - LEDGE_W / 2 - 1.2 + 1e-6, 0.5):
            if wall == 'x-':
                r, (sx, sy) = (xi0, xi0 + LEDGE_D, t - LEDGE_W / 2, t + LEDGE_W / 2), (xi0 + SCREW_IN, t)
            elif wall == 'x+':
                r, (sx, sy) = (xi1 - LEDGE_D, xi1, t - LEDGE_W / 2, t + LEDGE_W / 2), (xi1 - SCREW_IN, t)
            elif wall == 'y-':
                r, (sx, sy) = (t - LEDGE_W / 2, t + LEDGE_W / 2, yi0, yi0 + LEDGE_D), (t, yi0 + SCREW_IN)
            else:
                r, (sx, sy) = (t - LEDGE_W / 2, t + LEDGE_W / 2, yi1 - LEDGE_D, yi1), (t, yi1 - SCREW_IN)
            if all(r[1] <= a or r[0] >= b or r[3] <= c or r[2] >= d for a, b, c, d in bbs) and \
                    all(sx <= a or sx >= b or sy <= c or sy >= d for a, b, c, d in wins):
                cands.append((sx, sy, r))
    picked = []
    for cx, cy in ((xi0, yi0), (xi1, yi0), (xi0, yi1), (xi1, yi1)):
        best = min(cands, key=lambda c: (c[0] - cx) ** 2 + (c[1] - cy) ** 2, default=None)
        if best and all((best[0] - p[0]) ** 2 + (best[1] - p[1]) ** 2 > 15 ** 2 for p in picked):
            picked.append(best)
    while len(picked) < 3 and cands:      # too few near the corners: the free place farthest from those taken
        far = max(cands, key=lambda c: min((c[0] - p[0]) ** 2 + (c[1] - p[1]) ** 2 for p in picked) if picked else 0)
        if picked and min((far[0] - p[0]) ** 2 + (far[1] - p[1]) ** 2 for p in picked) <= 15 ** 2:
            break
        picked.append(far)
    return [(x, y, box(*r, z0, z_in)) for x, y, r in picked[:n_max]]


# stiffening ribs against warping (JLC3DP: nylon flat / framed / hollow parts shrink to the centre or warp along the
# diagonal and the edges, ribs help): a grid on the floor under the board and on the underside of the lid
RIB_W, RIB_PITCH = 1.2, 12.0
RIB_FLOOR = 1.0                  # floor ribs' height: 1.0 under the board (on the bosses at ZB), clear of THT legs
RIB_LID = 1.5                    # lid ribs' depth under the lid


def rib_grid(xi0, xi1, yi0, yi1, z0, z1, avoid):
    """Bars along x and y every RIB_PITCH inside (xi0..xi1, yi0..yi1), each cut over its whole width where it meets
    an (x0, x1, y0, y1) in avoid (no slivers along a bar); stubs under 6 long dropped. Returns a solid or None."""
    w = RIB_W / 2
    bars = []
    nx, ny = int((xi1 - xi0) // RIB_PITCH), int((yi1 - yi0) // RIB_PITCH)
    for i in range(1, nx + 1):
        x = xi0 + (xi1 - xi0) * i / (nx + 1)
        b = box(x - w, x + w, yi0, yi1, z0, z1)
        for x0, x1, y0, y1 in avoid:
            if x0 < x + w and x1 > x - w:
                b = b.cut(box(x - 1, x + 1, y0, y1, z0 - 1, z1 + 1))
        bars += b.solids().vals()
    for i in range(1, ny + 1):
        y = yi0 + (yi1 - yi0) * i / (ny + 1)
        b = box(xi0, xi1, y - w, y + w, z0, z1)
        for x0, x1, y0, y1 in avoid:
            if y0 < y + w and y1 > y - w:
                b = b.cut(box(x0, x1, y - 1, y + 1, z0 - 1, z1 + 1))
        bars += b.solids().vals()
    keep = [v for v in bars if max(v.BoundingBox().xlen, v.BoundingBox().ylen) >= 6.0]
    if not keep:
        return None
    r = cq.Workplane().add(keep[0])
    for v in keep[1:]:
        r = r.union(cq.Workplane().add(v))
    return r


def bb_xy(o, m):
    bb = o.val().BoundingBox()
    return (bb.xmin - m, bb.xmax + m, bb.ymin - m, bb.ymax + m)


def shell_and_lid(xi0, xi1, yi0, yi1, wall_cuts, lid_cuts, z_in, t_top=T_TOP, keep_clear=(), tht=(), floor=(),
                  rib_floor=RIB_FLOOR):
    """A tray (floor + walls up to z_in) and a flat lid (z_in..z_in + t_top) with a locating rim, all corners R3 outside,
    screwed down through the lid into ledges on the walls, both stiffened with a grid of ribs. keep_clear: every part,
    for the rim, the ledges and the lid's ribs; tht: the parts with legs through the board, floor: what stands on the
    floor (bosses, posts), both kept clear by the floor's ribs."""
    Z_IN, Z_TOP = z_in, z_in + t_top
    xo0, xo1, yo0, yo1 = xi0 - T_WALL, xi1 + T_WALL, yi0 - T_WALL, yi1 + T_WALL
    tray = rbox(xo0, xo1, yo0, yo1, -T_FLOOR, Z_IN, 3.0).cut(rbox(xi0, xi1, yi0, yi1, 0, Z_IN + 1, 1.2))
    lid = rbox(xo0, xo1, yo0, yo1, Z_IN, Z_TOP, 3.0)
    screws = ledges(xi0, xi1, yi0, yi1, Z_IN, list(keep_clear) + list(wall_cuts), lid_cuts)
    for x, y, led in screws:
        tray = tray.union(led).cut(cyl_z(x, y, PILOT / 2, Z_IN - LEDGE_H + 1.2, Z_IN + 1))
        cone = cq.Workplane().add(cq.Solid.makeCone(CLEAR / 2, CSK / 2, (CSK - CLEAR) / 2,
                                                    cq.Vector(x, y, Z_TOP - (CSK - CLEAR) / 2), cq.Vector(0, 0, 1)))
        lid = lid.cut(cyl_z(x, y, CLEAR / 2, Z_IN - 3, Z_TOP + 1)).cut(cone)
    keep_clear = list(keep_clear) + [led for _, _, led in screws]
    # the locating rim: bars along the walls, clear of the corners and of anything near the walls; stubs dropped
    z0, z1, a, b = Z_IN - 2.0, Z_IN + 0.01, 0.2, 1.4
    rim = (box(xi0 + a, xi0 + b, yi0 + 4, yi1 - 4, z0, z1).union(box(xi1 - b, xi1 - a, yi0 + 4, yi1 - 4, z0, z1))
           .union(box(xi0 + 4, xi1 - 4, yi0 + a, yi0 + b, z0, z1)).union(box(xi0 + 4, xi1 - 4, yi1 - b, yi1 - a, z0, z1)))
    for o in list(keep_clear) + list(wall_cuts):
        bb = o.val().BoundingBox()
        if bb.zmax < z0 or bb.zmin > z1:
            continue
        x0, x1, y0, y1 = bb.xmin - 1.0, bb.xmax + 1.0, bb.ymin - 1.0, bb.ymax + 1.0
        # a cut that reaches into a bar takes the whole width of it (no slivers along the bar)
        x0, x1 = (xi0 - 1 if x0 < xi0 + b + 0.5 else x0), (xi1 + 1 if x1 > xi1 - b - 0.5 else x1)
        y0, y1 = (yi0 - 1 if y0 < yi0 + b + 0.5 else y0), (yi1 + 1 if y1 > yi1 - b - 0.5 else y1)
        rim = rim.cut(box(x0, x1, y0, y1, z0 - 1, z1 + 1))
    bars = [v for v in rim.solids().vals() if max(v.BoundingBox().xlen, v.BoundingBox().ylen) >= 6.0]
    for v in bars:
        lid = lid.union(cq.Workplane().add(v))
    # ribs: on the floor clear of the THT legs under the board, under the lid clear of every part below it
    fr = rib_grid(xi0, xi1, yi0, yi1, -0.01, rib_floor, [bb_xy(o, 1.0) for o in tht] + [bb_xy(cq.Workplane().add(v), 1.0) for o in floor for v in o.solids().vals()])
    if fr is not None:
        tray = tray.union(fr)
    z0 = Z_IN - RIB_LID
    lr = rib_grid(xi0 + 0.5, xi1 - 0.5, yi0 + 0.5, yi1 - 0.5, z0, Z_IN + 0.01,
                  [bb_xy(o, 0.5) for o in keep_clear if o.val().BoundingBox().zmax > z0 - 0.3] +
                  [bb_xy(o, 1.0) for o in lid_cuts])
    if lr is not None:
        lid = lid.union(lr)
    for c in wall_cuts:
        tray = tray.cut(c)
    for c in lid_cuts:
        lid = lid.cut(c)
    return tray, lid, (xo1 - xo0, yo1 - yo0, Z_TOP + T_FLOOR), [(x, y) for x, y, _ in screws]


def check(case_parts, parts):
    bad = []
    case = case_parts[0].union(case_parts[1])
    for n, o in parts:
        v = case.intersect(o).val().Volume()
        if v > 0.01:
            bad.append(f'case/{n} {v:.2f}')
    for i, (na, a) in enumerate(parts):
        for nb, b in parts[i + 1:]:
            v = a.intersect(b).val().Volume()
            if v > 0.01:
                bad.append(f'{na}/{nb} {v:.2f}')
    return bad
