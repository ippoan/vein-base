"""Vein Station, printed (MJF PA12) instead of a machined Takachi case, with the station board drawn anew to suit:
two concepts to compare, the case and the parts' places only (the board is not routed yet).
  A  one row like SW130 (DB9 | SW1, J3 and the cable | vein module | VoiceS3R), lower: the MAX3232 and its caps go
     under the vein module inside its printed frame, so the module sits 2.9 over the board instead of on spacers.
  B  two rows: the vein module front-left, the VoiceS3R front-right (USB-C to +x, the reset to the front), the DB9
     on the back wall, the Grove (NFC) on the +x wall between the VoiceS3R and the DB9 (the USB-C's side),
     MAX3232 / SW1 behind the VoiceS3R, J3 and the cable back-left.
Both boards are drawn and routed (pcb/station_board/build_board.py print_a / print_b).
Both: a tray (floor 1.6, walls 1.8) with bosses for the board (2 high, M2 self-tapping), a flat lid (1.8) with a
locating rim. A: the vein module on four posts from the floor. B: the vein module stuck on the
board with VHB, held sideways by a frame hanging from the lid, a pad from the floor under it; the lid is notched
round the DB9 (which stands up through it) and the VoiceS3R's plugs, so it comes down to the cable's slack (16.7 high). Writes site/station-print-{a,b}/ and
station/vein_station_print_{a,b}_{body,lid}.stl, and fails on any interference.
Run from the repository root:  python3 station/build_station_print.py
Coordinates: x across, y along (B: -y = the front, the user's side), z = 0 on the floor's inside face."""
import os
import numpy as np
import cadquery as cq
from shapes import ROOT, box, rbox, cyl_z, stl_tris, vein_parts, write_page

T_WALL, T_FLOOR, T_TOP = 1.8, 1.6, 2.2       # the lid 2.2: 1.25 left under a screw's countersink
BOSS = 2.0                       # the board stands on printed bosses (M2 self-tapping screws)
ZB = BOSS
ZBT = ZB + 1.6                   # board top
Z_ATOM = ZBT + 2.5               # VoiceS3R bottom on the pin headers (plastic 2.5), top + 16.8
DB9_TOP, HOOD_TOP = ZBT + 12.5, ZBT + 13.25
Z_IN_A = ZBT + 8.7 + 0.4         # A: the DB9 outside the lid (a notch), so the lid goes down to the cable's slack
Z_IN_B = ZBT + 8.9 + 0.4         # B: the DB9 outside the lid (a notch), so the lid goes down to the cable's slack
Z_IN = Z_IN_A                    # the concept being built (set by concept_a / concept_b)
Z_TOP = Z_IN + T_TOP             # the lid's top face
VEIN_Z0 = ZBT + 3.3              # A: the vein module on printed posts, 2.9 over the MAX3232 / caps under it
VHB_B = 1.1                      # B: the vein module on the board with VHB (5952, 1.1), top 0.3 over the lid's
FRAME_H, FRAME_T = 5.0, 1.6      # B: the lid's frame round the vein module, down from the lid's inside / thick


def atom_at(x, y, ports):
    """The official VoiceS3R STL, ports to 'x+', 'x-', 'y+' or 'y-' (the reset is on the face clockwise of them)."""
    t = stl_tris('voice').copy()
    c = (t.reshape(-1, 3).min(axis=0) + t.reshape(-1, 3).max(axis=0)) / 2
    t[..., :2] -= c[:2]
    ang = {'y-': 0, 'x+': 90, 'y+': 180, 'x-': 270}[ports]    # file: ports on -y
    a = np.radians(ang)
    R = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]], dtype=np.float32)
    t[..., :2] = t[..., :2] @ R.T
    zmin = t.reshape(-1, 3)[:, 2].min()
    t[..., 2] += Z_ATOM - zmin
    t[..., 0] += x
    t[..., 1] += y
    return t.reshape(-1).astype(np.float32)


def on(x0, x1, y0, y1, z0, z1):
    return box(x0, x1, y0, y1, ZBT + z0, ZBT + z1)


def db9(cx, y_face, facing):
    """DB9 male RA on the board, its flange at y_face, mating face to 'y-' or 'y+'. Returns (parts, plug)."""
    s = -1 if facing == 'y-' else 1
    def yy(a, b):        # a, b measured outwards from the flange face
        return (min(y_face + s * a, y_face + s * b), max(y_face + s * a, y_face + s * b))
    body = on(cx - 15.0, cx + 15.0, *yy(-10.5, -0.5), 0, 12.5)
    flange = on(cx - 15.4, cx + 15.4, *yy(-1.0, 0.0), 0, 12.5)
    shell = on(cx - 8.5, cx + 8.5, *yy(0.0, 6.0), 2.0, 10.5)
    plug = box(cx - 15.15, cx + 15.15, *yy(0.8, 40.0), ZBT - 0.75, HOOD_TOP)
    return body.union(flange), shell, plug


# the lid's screws: an M2 countersunk tapping screw (M2 x 5) from the top into a ledge on the inside of a wall
LEDGE_D, LEDGE_W, LEDGE_H = 3.9, 6.0, 4.5     # out from the wall, along it, down from the lid (M2 x 5)
SCREW_IN = 1.9                                 # the screw's axis from the wall's inside face (in the wall's 1.8 + ledge)
PILOT, CLEAR, CSK = 1.6, 2.3, 4.2              # tapping pilot, the lid's clearance hole, the countersink (90 deg)


def ledges(xi0, xi1, yi0, yi1, avoid, lid_cuts=(), n_max=4):
    """Screw ledges along the inside of the walls, clear of every part and wall cut in `avoid` (by bounding box,
    0.3 margin): the free place nearest to each inside corner. Returns [(x, y, ledge box)]."""
    z0 = Z_IN - LEDGE_H
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
    return [(x, y, box(*r, z0, Z_IN)) for x, y, r in picked[:n_max]]


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


def shell_and_lid(xi0, xi1, yi0, yi1, wall_cuts, lid_cuts, keep_clear=(), tht=(), floor=(), rib_floor=RIB_FLOOR):
    """A tray (floor + walls up to Z_IN) and a flat lid (Z_IN..Z_TOP) with a locating rim, all corners R3 outside,
    screwed down through the lid into ledges on the walls, both stiffened with a grid of ribs. keep_clear: every part,
    for the rim, the ledges and the lid's ribs; tht: the parts with legs through the board, floor: what stands on the
    floor (bosses, posts), both kept clear by the floor's ribs."""
    xo0, xo1, yo0, yo1 = xi0 - T_WALL, xi1 + T_WALL, yi0 - T_WALL, yi1 + T_WALL
    tray = rbox(xo0, xo1, yo0, yo1, -T_FLOOR, Z_IN, 3.0).cut(rbox(xi0, xi1, yi0, yi1, 0, Z_IN + 1, 1.2))
    lid = rbox(xo0, xo1, yo0, yo1, Z_IN, Z_TOP, 3.0)
    screws = ledges(xi0, xi1, yi0, yi1, list(keep_clear) + list(wall_cuts), lid_cuts)
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


def bosses(pts):
    s = None
    for x, y in pts:
        b = cyl_z(x, y, 2.5, 0, ZB).cut(cyl_z(x, y, 0.9, 0.5, ZB + 1))
        s = b if s is None else s.union(b)
    return s


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


def set_lid(z_in):
    global Z_IN, Z_TOP
    Z_IN, Z_TOP = z_in, z_in + T_TOP


def concept_a():
    set_lid(Z_IN_A)
    # inside 35 wide; along y: DB9 | SW1 (-x) and J6 (+x), J3 behind them | vein module | VoiceS3R.
    # The board is pcb/station_board/build_board.py print_a: these places are its footprints (keep them together)
    xi0, xi1 = -17.5, 17.5                  # 35: room for the lid screws beside the VoiceS3R's window
    yi0 = -56.4
    ydb = yi0 + 0.05                         # DB9 flange on the -y wall (the board's -y edge)
    vein = (-13.0, 13.0, -25.4, 33.6)        # socket at -y
    ay = vein[3] + 2.0 + 12.0               # VoiceS3R centre (47.6)
    yi1 = ay + 12.0 + 0.3
    bx0, bx1, by0, by1 = -17.2, 17.2, ydb, yi1 - 0.3
    pcb = box(bx0, bx1, by0, by1, ZB, ZBT)
    d9, d9shell, d9plug = db9(0.0, ydb, 'y-')
    row = by0 + 10.6                         # behind the DB9's body
    # MAX3232, C1..C5 and R1 / R2 under the vein module (2.9 under it: 1.75 / 0.9 / 0.5 high), footprints with pads
    u1 = on(-5.4, 5.3, -17.2, -9.7, 0, 1.75)
    caps = on(-7.9, 7.9, -7.75, -6.25, 0, 0.9).union(on(8.75, 10.25, -13.5, -7.0, 0, 0.5))
    sw1 = on(-16.4, -4.8, row, row + 12.45, 0, 3.0)                 # DIP on -x behind the DB9 (lid off to set)
    j3x, j3y = -0.15, vein[2] - 3.9
    j3 = on(j3x - 5.0, j3x + 5.0, j3y - 3.1, j3y + 3.7, 0, 3.4)     # just in front of the vein socket, opening -y
    j3p = on(j3x - 3.0, j3x + 3.0, j3y - 9.1, j3y - 3.1, 0.3, 3.1)   # its plug between SW1 and J6
    slack = box(xi0 + LEDGE_D + 0.8, 4.5, row + 1.0, row + 15.0, ZBT + 3.7, ZBT + 8.7)   # the vein cable's slack over
                                                    # SW1 / J3, clear of a lid screw's ledge on the -x wall
    gy = row + 6.62                                                 # J6 (Grove) on +x behind the DB9
    gf = bx1 - 2.3                                                  # its front, 2.3 inside the board edge
    grove = on(gf - 7.7, gf, gy - 6.0, gy + 6.0, 0, 6.0)
    groveplug = on(gf, xi1 + 6.0, gy - 4.5, gy + 4.5, 0.6, 5.4)
    hdr = on(-8.9, -6.3, ay - 3.8, ay + 8.9, 0, 2.5).union(on(6.3, 8.9, ay - 1.3, ay + 8.9, 0, 2.5))
    atom_box = rbox(-12, 12, ay - 12, ay + 12, Z_ATOM, Z_ATOM + 16.8, 3.0)
    usb = box(-6, 6, ay + 12 + 6.5, ay + 12 + 24, Z_ATOM + 4, Z_ATOM + 11).union(
        box(-4.2, 4.2, ay + 12, ay + 12 + 6.5, Z_ATOM + 6, Z_ATOM + 9))
    porta = box(-4.9, 4.9, ay + 12, ay + 12 + 10.2, Z_ATOM, Z_ATOM + 4)
    vbox = rbox(*vein, VEIN_Z0, VEIN_Z0 + 15.0, 2.0)
    # the vein module stands on four posts from the floor through the board's 4.3 holes (P1..P4), VHB on top
    posts_xy = [(-10.5, vein[2] + 2.5), (10.5, vein[2] + 2.5), (-10.5, vein[3] - 2.5), (10.5, vein[3] - 2.5)]
    frame = None
    for x, y in posts_xy:
        c = cyl_z(x, y, 1.8, 0, VEIN_Z0)
        frame = c if frame is None else frame.union(c)
    holes = [(-7.5, 24.0), (7.5, 24.0), (0.0, 2.0), (-14.2, ay), (14.2, ay)]   # the board's M2 screws (H1..H5)
    bs = bosses(holes)
    wall_cuts = [box(-15.65, 15.65, yi0 - 5, yi0 + 1, ZBT - 1.5, Z_IN + 0.1),            # DB9, open to the lid
                 box(-5.3, 5.3, yi1 - 1, yi1 + 5, Z_ATOM - 0.4, Z_ATOM + 9.4),          # USB-C over PORT.A
                 box(xi1 - 1, xi1 + 5, gy - 5.0, gy + 5.0, ZBT - 0.3, ZBT + 6.4),        # the Grove plug
                 box(xi1 - 1, xi1 + 5, ay - 7.0, ay - 1.0, Z_ATOM + 1.0, Z_IN + 0.1)]    # the reset, open to the lid
    # the DB9 stands up through a notch in the lid at the -y end, and the VoiceS3R's window runs out over the +y
    # wall for the USB-C / PORT.A plugs (they are over the lid too)
    lid_cuts = [rbox(vein[0] - 0.2, vein[1] + 0.2, vein[2] - 0.2, vein[3] + 0.2, Z_IN - 3, Z_TOP + 1, 2.2),
                rbox(-12.2, 12.2, ay - 12.2, ay + 12.2, Z_IN - 3, Z_TOP + 1, 3.2),
                box(-6.2, 6.2, ay + 6.0, yi1 + T_WALL + 1, Z_IN - 3, Z_TOP + 1),
                box(-15.65, 15.65, yi0 - T_WALL - 1, yi0 + 11.0, Z_IN - 3, Z_TOP + 1)]
    parts = [('DB9', d9), ('DB9 plug', d9plug), ('MAX3232', u1), ('caps', caps), ('SW1', sw1), ('J3', j3),
             ('J3 plug', j3p), ('cable slack', slack), ('Grove', grove), ('Grove plug', groveplug), ('headers', hdr),
             ('VoiceS3R', atom_box), ('USB plug', usb), ('PORT.A plug', porta), ('vein', vbox)]
    tray, lid, size, screws = shell_and_lid(xi0, xi1, yi0, yi1, wall_cuts, lid_cuts, [o for _, o in parts] + [d9shell],
                                            tht=[d9, hdr], floor=[bs, frame])
    tray = tray.union(bs).union(frame)
    pcb_v = pcb
    for x, y in posts_xy:
        pcb_v = pcb_v.cut(cyl_z(x, y, 2.15, ZB - 1, ZBT + 1))
    for x, y in holes:
        pcb_v = pcb_v.cut(cyl_z(x, y, 1.1, ZB - 1, ZBT + 1))
    bad = check((tray.cut(bs), lid), parts)
    view = [('shell', 'ふた(天板・指静脈と VoiceS3R の窓、M2 皿ねじで本体の受けに締める)', '#2b2f33', 0.45, 'shell', lid),
            ('atom', 'VoiceS3R(公式 CAD、USB-C は +y)', '#1fa49a', 1, 'mods', atom_at(0, ay, 'y+'))] + \
        vein_parts(vein, VEIN_Z0, along_y=True) + [
        ('pcb', 'station 基板 print_a(配線済み、build_board.py print_a)', '#1f7a4d', 1, 'mods', pcb_v),
        ('frame', '指静脈を載せる柱 4 本(本体と一体、基板の穴を通す。上に VHB)', '#8fa09c', 1, 'mods', frame),
        ('db9', 'DB9 オス(−y の端面)', '#8a8f96', 1, 'mods', d9.union(d9shell)), ('db9plug', 'DB9 プラグ', '#5c6166', 1, 'mods', d9plug),
        ('u1', 'MAX3232・C1〜C5・R1 / R2(指静脈の下)', '#202326', 1, 'mods', u1.union(caps)),
        ('sw1', 'SW1 DIP(DB9 の後ろの −x、ふたを開けて切り替え)', '#c0392b', 1, 'mods', sw1),
        ('j3', 'J3 とプラグ(指静脈のソケットの手前)', '#f1efe8', 1, 'mods', j3.union(j3p)),
        ('slack', '指静脈のケーブルの余り(SW1 と J3 の上)', '#d9775c', 1, 'mods', slack),
        ('grove', 'J6 Grove とプラグ(+x の側面、DB9 の後ろ)', '#c47f0e', 1, 'mods', grove.union(groveplug)),
        ('usb', 'USB-C / PORT.A プラグ', '#24292d', 1, 'mods', usb.union(porta)),
        ('lid', '本体(床・壁・ボス・ふたのねじの受け、MJF PA12 で造形)', '#8fa09c', 0.9, 'lid', tray)]
    return view, bad, size, tray, lid, screws


def concept_b():
    set_lid(Z_IN_B)
    # two rows: the vein module on the left (finger end at the front, -y), the VoiceS3R front-right (USB-C to +x,
    # the reset to the front), the DB9 behind it on the +x wall (so the lid is cut along its +x edge only, no thin
    # strip at the back), MAX3232 / C1..C5 between the vein module and the DB9, J6 (+x) / SW1 / J3 along the back.
    # The VoiceS3R's corner is open like an M5Stack ATOMIC base (no walls round it): its +x and front faces are the
    # box's, the board and the floor run out under it to them, and it is held sideways by its pin headers only.
    vw = 26.0
    xi0 = -28.0
    yi0 = -37.0
    vy0, vy1 = yi0 + 0.5, yi0 + 0.5 + 59.0               # the socket end at +y (the back)
    vein = (xi0 + 0.5, xi0 + 0.5 + vw, vy0, vy1)
    ax = vein[1] + 0.5 + 12.0                                           # the VoiceS3R 0.5 beside the vein module
    xi1 = ax + 12.0 - T_WALL                                             # the VoiceS3R flush with the +x face
    ay = yi0 - T_WALL + 12.0                                            # the VoiceS3R flush with the front face
    yi1 = vy1 + 16.0
    bx0, bx1, by0, by1 = xi0 + 0.3, xi1 - 0.05, yi0 + 0.3, yi1 - 0.3      # the DB9 flange on the +x edge
    pcb = box(bx0, bx1, by0, by1, ZB, ZBT).union(box(ax - 12.0, ax + 12.0, ay - 12.0, ay + 12.0, ZB, ZBT))
    # the board is pcb/station_board/build_board.py print_b: these places are its footprints (keep them together)
    DY = 1.5                                                          # DB9 centre, mating face to +x on bx1
    d9 = on(bx1 - 10.5, bx1 - 0.5, DY - 15.0, DY + 15.0, 0, 12.5).union(on(bx1 - 1.0, bx1, DY - 15.4, DY + 15.4, 0, 12.5))
    d9shell = on(bx1, bx1 + 6.0, DY - 8.5, DY + 8.5, 2.0, 10.5)
    d9plug = box(bx1 + 0.8, bx1 + 40.0, DY - 15.15, DY + 15.15, ZBT - 0.75, HOOD_TOP)
    u1 = on(1.95, 6.05, 1.05, 10.95, 0, 1.75)                        # MAX3232 between the vein module and the DB9
    caps = on(0.5, 3.5, -11.75, -1.44, 0, 0.9).union(on(3.5, 6.5, 19.25, 22.75, 0, 0.5))   # C1..C5, R1 / R2
    sw1 = on(-3.86, 7.86, 26.65, 33.35, 0, 3.0)                       # DIP behind the vein module's +x end (lid off)
    j3x, j3y = -18.2, vy1 + 3.9                                       # behind the vein socket, opening +y
    j3 = on(j3x - 5.0, j3x + 5.0, j3y - 3.7, j3y + 3.1, 0, 3.4)
    j3p = on(j3x - 3.0, j3x + 3.0, j3y + 3.1, j3y + 9.1, 0.3, 3.1)
    gy = 25.0                                                         # J6 on the +x wall behind the DB9
    grove = on(bx1 - 2.3 - 7.7, bx1 - 2.3, gy - 6.0, gy + 6.0, 0, 6.0)
    groveplug = on(bx1 - 2.3, xi1 + 6.0, gy - 4.5, gy + 4.5, 0.6, 5.4)
    slack = box(xi0 + LEDGE_D + 0.8, -12.0, vy1 + 2.0, yi1 - 1.5, ZBT + 6.1, ZBT + 8.9)   # one layer (2.5) over J3,
                                                                    # clear of a lid screw's ledge in the back-left corner
    # J1 / J2 turned a quarter with the VoiceS3R (vein-base's x_vb -> y, y_vb -> -x): J1 (5 pins) at y = ay + 7.62
    # from x = ax - 2.54, J2 (4 pins) at y = ay - 7.62 from x = ax, both to ax + 7.62 (the USB-C side)
    hdr = on(ax - 3.81, ax + 8.89, ay + 6.35, ay + 8.89, 0, 2.5).union(on(ax - 1.27, ax + 8.89, ay - 8.89, ay - 6.35, 0, 2.5))
    atom_box = rbox(ax - 12, ax + 12, ay - 12, ay + 12, Z_ATOM, Z_ATOM + 16.8, 3.0)
    usb = box(ax + 12 + 6.5, ax + 12 + 24, ay - 6, ay + 6, Z_ATOM + 4, Z_ATOM + 11).union(
        box(ax + 12, ax + 12 + 6.5, ay - 4.2, ay + 4.2, Z_ATOM + 6, Z_ATOM + 9))
    porta = box(ax + 12, ax + 12 + 10.2, ay - 4.9, ay + 4.9, Z_ATOM, Z_ATOM + 4)
    # the vein module is stuck straight on the board with VHB (no spacers): its top 0.3 over the lid's (the box's
    # height is set by the DB9's hood). The lid stops at the module's +x and +y sides (no thin strips round it): the
    # body's -x and front walls run up to the lid's top face beside it, two bars hanging from the lid's edges hold it
    # on +x and +y, and the floor ribs come up to the board (2.0) to take the finger's push.
    vz0 = ZBT + VHB_B
    vbox = rbox(*vein, vz0, vz0 + 15.0, 2.0)
    fz0 = Z_IN - FRAME_H
    frame = box(vein[1] + 0.2, vein[1] + 0.2 + FRAME_T, ay + 12.3, vein[3] + 0.2 + FRAME_T, fz0, Z_IN + 0.01).union(
        box(vein[0] + 4.0, vein[1] + 0.2 + FRAME_T, vein[3] + 0.2, vein[3] + 0.2 + FRAME_T, fz0, Z_IN + 0.01))
    holes = [(-24.7, 35.2), (12.0, 34.5), (5.0, 15.0), (3.5, -27.0)]     # the board's M2 screws (H1..H4)
    bs = bosses(holes)
    corner = box(ax - 12.3, xi1 + T_WALL + 1, yi0 - T_WALL - 1, ay + 12.3, 0, Z_TOP + 1)   # open round the VoiceS3R
    wall_cuts = [box(xi1 - 1, xi1 + 5, ay + 12.0, DY + 15.65, ZBT - 1.5, Z_IN + 0.1),           # DB9 on the +x wall,
                                                                     # on into the open corner (no sliver between)
                 corner,
                 box(xi1 - 1, xi1 + 5, gy - 5.0, gy + 5.0, ZBT - 0.3, ZBT + 6.4)]             # the Grove plug (+x)
    # the DB9 stands up through a notch in the lid along the +x edge (its body and the plug's hood over the lid)
    xo0, yo0 = xi0 - T_WALL, yi0 - T_WALL
    lid_cuts = [box(xo0 - 1, vein[1] + 0.2, yo0 - 1, vein[3] + 0.2, Z_IN - 3, Z_TOP + 1),        # the vein module
                box(xo0 - 1, xi1 + T_WALL + 1, yo0 - 1, ay + 12.3, Z_IN - 3, Z_TOP + 1),        # all of the front
                corner,
                box(bx1 - 11.0, xi1 + T_WALL + 1, ay + 12.0, DY + 15.65, Z_IN - 3, Z_TOP + 1)]
    parts = [('DB9', d9), ('DB9 plug', d9plug), ('MAX3232', u1), ('caps', caps), ('SW1', sw1), ('J3', j3),
             ('J3 plug', j3p), ('cable slack', slack), ('Grove', grove), ('Grove plug', groveplug), ('headers', hdr),
             ('VoiceS3R', atom_box), ('USB plug', usb), ('PORT.A plug', porta), ('vein', vbox)]
    tray, lid, size, screws = shell_and_lid(xi0, xi1, yi0, yi1, wall_cuts, lid_cuts,
                                            [o for _, o in parts] + [d9shell, frame, corner], tht=[d9, hdr], floor=[bs],
                                            rib_floor=ZB)
    # the -x and front walls beside the vein module up to the lid's top face (where the lid is cut away)
    hi = box(xo0, xi0, yo0, vein[3] + 0.2, Z_IN - 0.01, Z_TOP).union(box(xo0, ax - 12.3, yo0, yi0, Z_IN - 0.01, Z_TOP))
    tray = tray.union(hi.intersect(rbox(xo0, xi1 + T_WALL, yo0, yi1 + T_WALL, Z_IN - 1, Z_TOP, 3.0)))
    tray = tray.union(bs)
    lid = lid.union(frame)
    pcb_v = pcb
    for x, y in holes:
        pcb_v = pcb_v.cut(cyl_z(x, y, 1.1, ZB - 1, ZBT + 1))
    bad = check((tray.cut(bs), lid), parts)
    vp = [(k, l, c, o, g, s.rotate(((vein[0] + vein[1]) / 2, (vy0 + vy1) / 2, 0),
                                   ((vein[0] + vein[1]) / 2, (vy0 + vy1) / 2, 1), 180))
          for k, l, c, o, g, s in vein_parts(vein, vz0, along_y=True)]
    view = [('shell', 'ふた(天板・指静脈と VoiceS3R の窓、M2 皿ねじで本体の受けに締める)', '#2b2f33', 0.45, 'shell', lid),
            ('atom', 'VoiceS3R(公式 CAD、USB-C は右 +x、リセットは手前。右手前の角は壁なしで、右の面は箱の面とそろう。横はピンヘッダーだけで支える)', '#1fa49a', 1, 'mods', atom_at(ax, ay, 'x+'))] + vp + [
        ('pcb', 'station 基板 print_b(build_board.py print_b)', '#1f7a4d', 1, 'mods', pcb_v),
        ('frame', f'指静脈の +x と奥を押さえる枠(ふたの縁から {FRAME_H:g} 下がる。−x と手前は天板の高さまで上げた本体の壁)', '#2b2f33', 1, 'mods', frame),
        ('db9', 'DB9 オス(右の側面、VoiceS3R の後ろ。ふたの右の縁を切り欠いて上に出る)', '#8a8f96', 1, 'mods', d9.union(d9shell)), ('db9plug', 'DB9 プラグ', '#5c6166', 1, 'mods', d9plug),
        ('u1', 'MAX3232 と C1〜C5(指静脈と DB9 の間)', '#202326', 1, 'mods', u1.union(caps)),
        ('sw1', 'SW1 DIP(奥、指静脈の右端の後ろ。ふたを開けて切り替え)', '#c0392b', 1, 'mods', sw1),
        ('j3', 'J3 とプラグ(指静脈のソケットの後ろ)', '#f1efe8', 1, 'mods', j3.union(j3p)),
        ('slack', '指静脈のケーブルの余り(左奥、J3 の上)', '#d9775c', 1, 'mods', slack),
        ('grove', 'J6 Grove とプラグ(右の側面、DB9 の後ろ。USB-C と同じ面)', '#c47f0e', 1, 'mods', grove.union(groveplug)),
        ('usb', 'USB-C / PORT.A プラグ(右の側面)', '#24292d', 1, 'mods', usb.union(porta)),
        ('lid', '本体(床・壁・ボス・ふたのねじの受け、MJF PA12 で造形)', '#8fa09c', 0.9, 'lid', tray)]
    return view, bad, size, tray, lid, screws


VEIN_NOTE = {'a': 'ふたは DB9 の上を切り欠いて(DB9 とプラグのフードはふたより上に出る)、中のケーブルの余りの上まで下げた。'
                  f'指静脈はふたから {VEIN_Z0 + 15.0 - (Z_IN_A + T_TOP):.1f} 出る。本体と一体の柱 4 本(基板の穴を通す)に VHB で載せる',
             'b': 'ふたは DB9 の上を切り欠いて(DB9 とプラグのフードはふたより上に出る)、中のケーブルの余りの上まで下げた。'
                  f'指静脈は基板に VHB({VHB_B:g})でじかに貼る(上面はふたより {VHB_B + 15.0 - (Z_IN_B + T_TOP - ZBT):.1f} 出る)。'
                  f'ふたは指静脈のまわりと手前を切り、−x と手前は本体の壁を天板の高さまで上げた(ふたに細い部分を作らない)。'
                  f'+x と奥はふたの縁から下がる枠(深さ {FRAME_H:g}、厚さ {FRAME_T:g})で押さえる。'
                  '指で押す力は、基板の下面まで上げた床のリブ(高さ 2.0)が受ける'}
out = os.path.join(ROOT, 'station')
failed = []
for key, fn, title in (('a', concept_a, 'A 一列(薄型)'), ('b', concept_b, 'B 2 列(短い)')):
    view, bad, size, tray, lid, screws = fn()
    vol = (tray.val().Volume() + lid.val().Volume()) / 1000
    print(key, 'outer %.1f x %.1f x %.1f' % size, 'volume %.1f cm3' % vol, 'screws', [(round(x, 1), round(y, 1)) for x, y in screws],
          'interference:', bad or 'none')
    if len(screws) < 3:
        failed.append(f'{key}: only {len(screws)} places for the lid screws')
    failed += [f'{key}: {b}' for b in bad]
    stls = []
    for n, s, label in (('body', tray, '本体'), ('lid', lid, 'ふた')):
        p = os.path.join(out, f'vein_station_print_{key}_{n}.stl')
        cq.exporters.export(s, p, tolerance=0.02, angularTolerance=0.1)
        stls.append((f'{label}の STL(MJF PA12 で造形)', p))
    dims = [('外形', '%.1f × %.1f × %.1f(幅 × 奥行 × 高さ、ふた込み)' % size), ('体積', '%.1f cm³(本体 + ふた)' % vol),
            ('肉厚', f'壁 {T_WALL}、床 {T_FLOOR}、天板 {T_TOP}(MJF PA12)'),
            ('リブ', f'反り止め(JLC3DP の勧め)。幅 {RIB_W:g} を約 {RIB_PITCH:g} おきの格子に、床(高さ {RIB_FLOOR:g}、基板の下。THT の足とボスを避ける)と'
                     f'ふたの裏(深さ {RIB_LID:g}、部品と窓を避ける)'),
            ('基板', f'station 基板 print_{key}(箱に合わせて配置・配線済み、build_board.py print_{key})。床のボス(高さ 2)に M2 のタッピングねじで留める。THT の足は 2 に切る'),
            ('指静脈', VEIN_NOTE[key]),
            ('ふた', f'M2 皿タッピングねじ × {len(screws)} 本(M2 × 5)で、上から壁の内側の受け({LEDGE_D:g} × {LEDGE_W:g}、高さ {LEDGE_H:g})に締める。'
                     '受けの位置は部品と壁の穴を避けて四隅の近くを自動で選ぶ: ' + ', '.join(f'({x:.1f}, {y:.1f})' for x, y in screws)),
            ('干渉', 'なし' if not bad else ', '.join(bad))]
    write_page(f'station-print-{key}', f'案 {title}', view,
               f'Vein Station を 3D 印刷の箱にする試作案 {title}。基板も作り直す前提で、部品の置き場所だけを決めた形。'
               'ドラッグで回転、ホイール/ピンチで拡大。', dims,
               '試作の形(配置だけ)。基板は未配線、部品は KiCad のフットプリント寸法からの簡略形状。VoiceS3R は M5Stack 公式 STL'
               '(m5stack/M5_Hardware、MIT License)。単位 mm。', Z_TOP, stls)
if failed:
    raise SystemExit('interference: ' + ', '.join(failed))
