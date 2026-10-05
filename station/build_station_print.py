"""Vein Station, printed (MJF PA12) instead of a machined Takachi case, with the station board drawn anew to suit:
two concepts to compare, the case and the parts' places only (the board is not routed yet).
  A  one row like SW130 (DB9 | SW1, J3 and the cable | vein module | VoiceS3R), lower: the MAX3232 and its caps go
     under the vein module inside its printed frame, so the module sits 2.9 over the board instead of on spacers.
  B  two rows: the vein module front-left, the VoiceS3R front-right (USB-C to +x, the reset to the front), the DB9
     on the back wall, the Grove (NFC) on the +x wall between the VoiceS3R and the DB9 (the USB-C's side),
     MAX3232 / SW1 behind the VoiceS3R, J3 and the cable back-left.
Both: a tray (floor 1.6, walls 1.8) with bosses for the board (2 high, M2 self-tapping), a flat lid (1.8) with a
locating rim, the vein module 2.5 proud of the lid. Writes site/station-print-{a,b}/ and
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
Z_IN = HOOD_TOP + 0.35           # inside of the top plate
Z_TOP = Z_IN + T_TOP             # the lid's top face
VEIN_Z0 = Z_TOP + 2.5 - 15.0     # the vein module 2.5 proud of the lid, on a printed frame


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
    return [(x, y, box(*r, z0, Z_IN)) for x, y, r in picked[:n_max]]


def shell_and_lid(xi0, xi1, yi0, yi1, wall_cuts, lid_cuts, keep_clear=()):
    """A tray (floor + walls up to Z_IN) and a flat lid (Z_IN..Z_TOP) with a locating rim, all corners R3 outside,
    screwed down through the lid into ledges on the walls. keep_clear: every part, for the rim and the ledges."""
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


def concept_a():
    # inside 34 wide; along y: DB9 | electronics, J3 and the cable | vein module | VoiceS3R
    xi0, xi1 = -17.5, 17.5                  # 35: room for the lid screws beside the VoiceS3R's window
    yi0 = -56.4
    ydb = yi0 + 0.05                         # DB9 flange on the -y wall
    vein = (-13.0, 13.0, yi0 + 27.0, yi0 + 86.0)   # socket at -y
    ay = vein[3] + 2.0 + 12.0               # VoiceS3R centre
    yi1 = ay + 12.0 + 0.3
    bx0, bx1, by0, by1 = xi0 + 0.3, xi1 - 0.3, yi0 + 0.3, yi1 - 0.3
    pcb = box(bx0, bx1, by0, by1, ZB, ZBT)
    d9, d9shell, d9plug = db9(0.0, ydb, 'y-')
    # MAX3232 and its caps under the vein module, inside its frame (2.9 under the module: they are 1.75 / 0.9 high)
    u1 = on(-5.0, 4.9, vein[2] + 10.0, vein[2] + 13.9, 0, 1.75)
    caps = on(-7.0, 6.5, vein[2] + 16.0, vein[2] + 17.5, 0, 0.9)
    sw1 = on(-16.2, -5.0, yi0 + 12.5, yi0 + 19.2, 0, 3.0)          # DIP on -x behind the DB9 (lid off)
    j3 = on(-4.0, 6.0, yi0 + 21.5, yi0 + 25.4, 0, 3.4)             # under the vein socket's end, opening -y
    j3p = on(-2.0, 4.0, yi0 + 21.5 - 6.0, yi0 + 21.5, 0.3, 3.1)
    slack = box(-16.0, 4.5, yi0 + 12.0, yi0 + 26.0, ZBT + 3.7, ZBT + 8.7)   # the vein cable's slack over SW1 / J3, under the lid's screw ledges
    gy = yi0 + 19.0                                                 # J6 (Grove) on +x behind the DB9
    grove = on(xi1 - 0.3 - 2.3 - 7.7, xi1 - 0.3 - 2.3, gy - 6.0, gy + 6.0, 0, 6.0)
    groveplug = on(xi1 - 2.6, xi1 + 6.0, gy - 4.5, gy + 4.5, 0.6, 5.4)
    hdr = on(-8.9, -6.3, ay - 3.8, ay + 8.9, 0, 2.5).union(on(6.3, 8.9, ay - 1.3, ay + 8.9, 0, 2.5))
    atom_box = rbox(-12, 12, ay - 12, ay + 12, Z_ATOM, Z_ATOM + 16.8, 3.0)
    usb = box(-6, 6, ay + 12 + 6.5, ay + 12 + 24, Z_ATOM + 4, Z_ATOM + 11).union(
        box(-4.2, 4.2, ay + 12, ay + 12 + 6.5, Z_ATOM + 6, Z_ATOM + 9))
    porta = box(-4.9, 4.9, ay + 12, ay + 12 + 10.2, Z_ATOM, Z_ATOM + 4)
    vbox = rbox(*vein, VEIN_Z0, VEIN_Z0 + 15.0, 2.0)
    frame = rbox(vein[0] - 1.6, vein[1] + 1.6, vein[2] - 1.6, vein[3] + 1.6, ZBT, VEIN_Z0, 2.0).cut(
        rbox(vein[0] + 3, vein[1] - 3, vein[2] + 3, vein[3] - 3, 0, 40, 1.0)).cut(
        rbox(*vein, VEIN_Z0 - 1.0, VEIN_Z0 + 1, 2.0))      # a printed frame under the module's rim
    holes = [(bx0 + 3, yi0 + 6), (bx1 - 3, yi0 + 6), (bx0 + 3, ay), (bx1 - 3, ay - 15)]
    bs = bosses(holes)
    wall_cuts = [box(-15.65, 15.65, yi0 - 5, yi0 + 1, ZBT - 1.5, Z_IN + 0.1),            # DB9, open to the lid
                 box(-5.3, 5.3, yi1 - 1, yi1 + 5, Z_ATOM - 0.4, Z_ATOM + 9.4),          # USB-C over PORT.A
                 box(xi1 - 1, xi1 + 5, gy - 6.3, gy + 6.3, ZBT - 0.3, ZBT + 6.4),        # Grove
                 box(xi1 - 1, xi1 + 5, ay - 7.0, ay - 1.0, Z_ATOM + 1.0, Z_IN + 0.1)]    # the reset, open to the lid
    lid_cuts = [rbox(vein[0] - 0.2, vein[1] + 0.2, vein[2] - 0.2, vein[3] + 0.2, Z_IN - 3, Z_TOP + 1, 2.2),
                rbox(-12.2, 12.2, ay - 12.2, ay + 12.2, Z_IN - 3, Z_TOP + 1, 3.2)]
    parts = [('DB9', d9), ('DB9 plug', d9plug), ('MAX3232', u1), ('caps', caps), ('SW1', sw1), ('J3', j3),
             ('J3 plug', j3p), ('cable slack', slack), ('Grove', grove), ('Grove plug', groveplug), ('headers', hdr),
             ('VoiceS3R', atom_box), ('USB plug', usb), ('PORT.A plug', porta), ('vein', vbox), ('vein frame', frame)]
    tray, lid, size, screws = shell_and_lid(xi0, xi1, yi0, yi1, wall_cuts, lid_cuts, [o for _, o in parts] + [d9shell])
    tray = tray.union(bs)
    bad = check((tray.cut(bs), lid), parts)
    view = [('shell', 'ふた(天板・指静脈と VoiceS3R の窓、M2 皿ねじで本体の受けに締める)', '#2b2f33', 0.45, 'shell', lid),
            ('atom', 'VoiceS3R(公式 CAD、USB-C は +y)', '#1fa49a', 1, 'mods', atom_at(0, ay, 'y+'))] + \
        vein_parts(vein, VEIN_Z0, along_y=True) + [
        ('pcb', '新しい基板(配置だけ、未配線)', '#1f7a4d', 1, 'mods', pcb),
        ('frame', '指静脈を載せる枠(箱と一体で造形)', '#8fa09c', 1, 'mods', frame),
        ('db9', 'DB9 オス(−y の端面)', '#8a8f96', 1, 'mods', d9.union(d9shell)), ('db9plug', 'DB9 プラグ', '#5c6166', 1, 'mods', d9plug),
        ('u1', 'MAX3232 と C1〜C5(指静脈の下、枠の内側)', '#202326', 1, 'mods', u1.union(caps)),
        ('sw1', 'SW1 DIP(DB9 の後ろの −x、ふたを開けて切り替え)', '#c0392b', 1, 'mods', sw1),
        ('j3', 'J3 とプラグ(指静脈のソケットの手前)', '#f1efe8', 1, 'mods', j3.union(j3p)),
        ('slack', '指静脈のケーブルの余り(SW1 と J3 の上)', '#d9775c', 1, 'mods', slack),
        ('grove', 'J6 Grove とプラグ(+x の側面、DB9 の後ろ)', '#c47f0e', 1, 'mods', grove.union(groveplug)),
        ('usb', 'USB-C / PORT.A プラグ', '#24292d', 1, 'mods', usb.union(porta)),
        ('lid', '本体(床・壁・ボス・ふたのねじの受け、MJF PA12 で造形)', '#8fa09c', 0.9, 'lid', tray)]
    return view, bad, size, tray, lid, screws


def concept_b():
    # two rows: the vein module on the left (finger end at the front, -y), the VoiceS3R front-right (USB-C to +x,
    # the reset to the front), MAX3232 / SW1 behind it, the DB9 at the back on the right, J3 and the cable back-left
    vw = 26.0
    xi0 = -28.0
    yi0 = -37.0
    vy0, vy1 = yi0 + 0.5, yi0 + 0.5 + 59.0               # the socket end at +y (the back)
    vein = (xi0 + 0.5, xi0 + 0.5 + vw, vy0, vy1)
    ax = vein[1] + 3.0 + 12.0
    xi1 = ax + 12.0 + 0.3
    ay = yi0 + 0.3 + 12.0
    yi1 = vy1 + 16.0
    bx0, bx1, by0, by1 = xi0 + 0.3, xi1 - 0.3, yi0 + 0.3, yi1 - 0.3
    pcb = box(bx0, bx1, by0, by1, ZB, ZBT)
    dcx = xi1 - 0.3 - 17.0                                             # the notch 1.65 off the +x wall
    d9, d9shell, d9plug = db9(dcx, yi1 - 0.05, 'y+')
    u1 = on(ax - 11, ax - 1.1, ay + 15.0, ay + 18.9, 0, 1.75)
    caps = on(ax - 11, ax - 1.1, ay + 20.5, ay + 22.0, 0, 0.9)
    sw1 = on(ax + 0.5, ax + 11.7, ay + 14.0, ay + 20.7, 0, 3.0)      # DIP behind the VoiceS3R (lid off)
    j3 = on(dcx - 25.5, dcx - 15.5, vy1 + 1.7, vy1 + 5.6, 0, 3.4)        # behind the vein socket, opening +y
    j3p = on(dcx - 23.5, dcx - 17.5, vy1 + 5.6, vy1 + 11.6, 0.3, 3.1)
    gy = ay + 30.0                                                        # J6 on the +x wall (the USB-C's side),
    grove = on(xi1 - 0.3 - 2.3 - 7.7, xi1 - 0.3 - 2.3, gy - 6.0, gy + 6.0, 0, 6.0)   # between the VoiceS3R and the DB9
    groveplug = on(xi1 - 2.6, xi1 + 6.0, gy - 4.5, gy + 4.5, 0.6, 5.4)
    slack = box(xi0 + 1.5, dcx - 16.0, vy1 + 2.0, yi1 - 1.5, ZBT + 6.1, ZBT + 8.9)    # one layer (2.5) over J6 and J3
    # J1 / J2 turned a quarter with the VoiceS3R (approximate)
    hdr = on(ax - 8.9, ax + 3.8, ay - 8.9, ay - 6.3, 0, 2.5).union(on(ax - 8.9, ax + 1.3, ay + 6.3, ay + 8.9, 0, 2.5))
    atom_box = rbox(ax - 12, ax + 12, ay - 12, ay + 12, Z_ATOM, Z_ATOM + 16.8, 3.0)
    usb = box(ax + 12 + 6.5, ax + 12 + 24, ay - 6, ay + 6, Z_ATOM + 4, Z_ATOM + 11).union(
        box(ax + 12, ax + 12 + 6.5, ay - 4.2, ay + 4.2, Z_ATOM + 6, Z_ATOM + 9))
    porta = box(ax + 12, ax + 12 + 10.2, ay - 4.9, ay + 4.9, Z_ATOM, Z_ATOM + 4)
    vbox = rbox(*vein, VEIN_Z0, VEIN_Z0 + 15.0, 2.0)
    frame = rbox(vein[0] - 0.3, vein[1] + 1.6, vein[2] - 0.3, vein[3] + 1.6, ZBT, VEIN_Z0, 2.0).cut(
        rbox(vein[0] + 3, vein[1] - 3, vein[2] + 3, vein[3] - 3, 0, 40, 1.0)).cut(
        rbox(*vein, VEIN_Z0 - 1.0, VEIN_Z0 + 1, 2.0))
    holes = [(bx0 + 3, by1 - 3), (ax + 9, ay + 26), (vein[1] + 1.6, yi0 + 4)]
    bs = bosses(holes)
    wall_cuts = [box(dcx - 15.65, dcx + 15.65, yi1 - 1, yi1 + 5, ZBT - 1.5, Z_IN + 0.1),        # DB9 at the back
                 box(xi1 - 1, xi1 + 5, ay - 5.3, ay + 5.3, Z_ATOM - 0.4, Z_ATOM + 9.4),        # USB-C / PORT.A (+x)
                 box(ax - 7.0, ax - 1.0, yi0 - 5, yi0 + 1, Z_ATOM + 1.0, Z_IN + 0.1),           # the reset (front)
                 box(xi1 - 1, xi1 + 5, gy - 5.0, gy + 5.0, ZBT - 0.3, ZBT + 6.4)]             # the Grove plug (+x)
    lid_cuts = [rbox(vein[0] - 0.2, vein[1] + 0.2, vein[2] - 0.2, vein[3] + 0.2, Z_IN - 3, Z_TOP + 1, 2.2),
                rbox(ax - 12.2, ax + 12.2, ay - 12.2, ay + 12.2, Z_IN - 3, Z_TOP + 1, 3.2)]
    parts = [('DB9', d9), ('DB9 plug', d9plug), ('MAX3232', u1), ('caps', caps), ('SW1', sw1), ('J3', j3),
             ('J3 plug', j3p), ('cable slack', slack), ('Grove', grove), ('Grove plug', groveplug), ('headers', hdr),
             ('VoiceS3R', atom_box), ('USB plug', usb), ('PORT.A plug', porta), ('vein', vbox), ('vein frame', frame)]
    tray, lid, size, screws = shell_and_lid(xi0, xi1, yi0, yi1, wall_cuts, lid_cuts, [o for _, o in parts] + [d9shell])
    tray = tray.union(bs)
    bad = check((tray.cut(bs), lid), parts)
    vp = [(k, l, c, o, g, s.rotate(((vein[0] + vein[1]) / 2, (vy0 + vy1) / 2, 0),
                                   ((vein[0] + vein[1]) / 2, (vy0 + vy1) / 2, 1), 180))
          for k, l, c, o, g, s in vein_parts(vein, VEIN_Z0, along_y=True)]
    view = [('shell', 'ふた(天板・指静脈と VoiceS3R の窓、M2 皿ねじで本体の受けに締める)', '#2b2f33', 0.45, 'shell', lid),
            ('atom', 'VoiceS3R(公式 CAD、USB-C は右 +x、リセットは手前)', '#1fa49a', 1, 'mods', atom_at(ax, ay, 'x+'))] + vp + [
        ('pcb', '新しい基板(配置だけ、未配線)', '#1f7a4d', 1, 'mods', pcb),
        ('frame', '指静脈を載せる枠(箱と一体で造形)', '#8fa09c', 1, 'mods', frame),
        ('db9', 'DB9 オス(奥の端面、右寄り)', '#8a8f96', 1, 'mods', d9.union(d9shell)), ('db9plug', 'DB9 プラグ', '#5c6166', 1, 'mods', d9plug),
        ('u1', 'MAX3232 と C1〜C5(VoiceS3R の後ろ)', '#202326', 1, 'mods', u1.union(caps)),
        ('sw1', 'SW1 DIP(VoiceS3R の後ろ、ふたを開けて切り替え)', '#c0392b', 1, 'mods', sw1),
        ('j3', 'J3 とプラグ(指静脈のソケットの後ろ)', '#f1efe8', 1, 'mods', j3.union(j3p)),
        ('slack', '指静脈のケーブルの余り(左奥、J3 の上)', '#d9775c', 1, 'mods', slack),
        ('grove', 'J6 Grove とプラグ(右の側面、VoiceS3R と DB9 の間。USB-C と同じ面)', '#c47f0e', 1, 'mods', grove.union(groveplug)),
        ('usb', 'USB-C / PORT.A プラグ(右の側面)', '#24292d', 1, 'mods', usb.union(porta)),
        ('lid', '本体(床・壁・ボス・ふたのねじの受け、MJF PA12 で造形)', '#8fa09c', 0.9, 'lid', tray)]
    return view, bad, size, tray, lid, screws


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
            ('基板', '箱に合わせて作り直す(この図は配置だけ、未配線)。床のボス(高さ 2)に M2 のタッピングねじで留める。THT の足は 2 に切る'),
            ('指静脈', 'ふたから 2.5 出る。箱と一体の枠に載せる(スペーサー・VHB なし)'),
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
