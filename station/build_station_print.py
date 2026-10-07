"""Vein Station, printed (MJF PA12) instead of a machined Takachi case, with the station board drawn anew to suit:
two concepts to compare, the case and the parts' places only (the board is not routed yet).
  A  one row like SW130 (DB9 | SW1, J3 and the cable | vein module | VoiceS3R), lower: the MAX3232 and its caps go
     under the vein module inside its printed frame, so the module sits 2.9 over the board instead of on spacers.
  B  two rows: the vein module front-left on a stand 3.9 over the board with J3, SW1, MAX3232, C1..C5, R1 / R2 and
     the cable's slack under it, held down by the lid on its step (as Vein Unit P); the VoiceS3R front-right (USB-C to
     +x, the reset to the front) in an open corner (no walls nor lid round it), the DB9 behind it on the +x wall,
     the Grove (NFC) behind that on the back wall.
Both boards are drawn and routed (pcb/station_board/build_board.py print_a / print_b).
Both: a tray (floor 1.6, walls 1.8) with bosses for the board (2 high, M2 self-tapping), a flat lid (1.8) with a
locating rim. A: the vein module on four posts from the floor; the lid is notched round the DB9 (which stands up
through it) and the VoiceS3R's plugs, so it comes down to the cable's slack. B: the vein module on a stand from the
floor (a shelf along -x, a bar under its front end, a post), its 57 x 25 top step through the lid's window, its body
against a 0.7 recess under the lid (0.5 proud); the board an L clear of the stand, notched round the lid screws'
ledges so that it drops in past them (shapes.way_in). Writes site/station-print-{a,b}/ and
station/vein_station_print_{a,b}_{body,lid}.stl, and fails on any interference.
Run from the repository root:  python3 station/build_station_print.py
Coordinates: x across, y along (B: -y = the front, the user's side), z = 0 on the floor's inside face."""
import os
import numpy as np
import cadquery as cq
from shapes import (ROOT, box, rbox, cyl_z, stl_tris, vein_parts, vein_step_box, write_page, shell_and_lid, check,
                    ledge_notches, way_in, xy_box, T_WALL, T_FLOOR, T_TOP, LEDGE_D, LEDGE_W, LEDGE_H, RIB_W, RIB_PITCH,
                    RIB_FLOOR, RIB_LID)

BOSS = 2.0                       # the board stands on printed bosses (M2 self-tapping screws)
ZB = BOSS
ZBT = ZB + 1.6                   # board top
Z_ATOM = ZBT + 2.5               # VoiceS3R bottom on the pin headers (plastic 2.5), top + 16.8
DB9_TOP, HOOD_TOP = ZBT + 12.5, ZBT + 13.25
Z_IN_A = ZBT + 8.7 + 0.4         # A: the DB9 outside the lid (a notch), so the lid goes down to the cable's slack
HC_B = 3.9                       # B: the vein module on a stand this high over the board: J3 (3.4) + 0.5 under it
RECESS_B = 0.7                   # B: the lid's recess for the vein module's body (as Vein Unit P)
Z_IN_B = ZBT + HC_B + 15.0 - 2.0 - RECESS_B   # B: the module's step face on the recess's floor, its top 0.5 proud
VEIN_Z0 = ZBT + 3.3              # A: the vein module on printed posts, 2.9 over the MAX3232 / caps under it
# B's board notches for the lid screws' ledges (shapes.ledge_notches; = NOTCHES in build_board.py print_b)
NOTCHES_B = [(-25.2, -20.5, 25.5, 29.4), (-8.1, -1.5, 25.5, 29.4), (17.0, 21.15, 17.4, 24.0)]


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


def bosses(pts):
    s = None
    for x, y in pts:
        b = cyl_z(x, y, 2.5, 0, ZB).cut(cyl_z(x, y, 0.9, 0.5, ZB + 1))
        s = b if s is None else s.union(b)
    return s



def concept_a():
    Z_IN, Z_TOP = Z_IN_A, Z_IN_A + T_TOP
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
    tray, lid, size, screws = shell_and_lid(xi0, xi1, yi0, yi1, wall_cuts, lid_cuts, Z_IN, keep_clear=[o for _, o in parts] + [d9shell],
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
    return view, bad, size, tray, lid, screws, Z_TOP


def concept_b():
    Z_IN, Z_TOP = Z_IN_B, Z_IN_B + T_TOP
    # two rows: the vein module on the left (finger end at the front, -y; socket at the back) up on a stand HC_B over
    # the board, with J3, SW1, MAX3232, C1..C5, R1 / R2 and the cable's slack under it; the VoiceS3R front-right
    # (USB-C to +x, the reset to the front), the DB9 behind it on the +x wall, J6 behind that on the back edge
    # (opening to the back: on the +x wall it would leave no place for a third lid screw).
    # The VoiceS3R's corner is open like an M5Stack ATOMIC base (no walls nor lid round it): its +x and front faces
    # are the box's, the board and the floor run out under it to them, and it is held by its pin headers only.
    # The vein module is held down by the lid on its step (as Vein Unit P) and stands on a stand from the floor: a shelf
    # along the -x wall under its -x side, a bar under its front end and a post under its back +x corner (through
    # the board); the board keeps clear of the shelf and the bar (an L outline), the post goes through a hole.
    # The board is pcb/station_board/build_board.py print_b: these places are its footprints (keep them together)
    vw = 26.0
    xi0 = -28.0
    yi0 = -37.0
    vz0 = ZBT + HC_B
    vy0, vy1 = yi0 + 0.5, yi0 + 0.5 + 59.0               # the socket end at +y (the back)
    vein = (xi0 + 0.5, xi0 + 0.5 + vw, vy0, vy1)
    ax = vein[1] + 0.5 + 12.0                                           # the VoiceS3R 0.5 beside the vein module
    xi1 = ax + 12.0 - T_WALL                                             # the VoiceS3R flush with the +x face
    ay = yi0 - T_WALL + 12.0                                            # the VoiceS3R flush with the front face
    yi1 = 29.7                               # J6 behind the DB9 (their courtyards 0.05 apart), the back ledges
    shelf = box(xi0 - 0.01, vein[0] + 2.0, yi0 - 0.01, vy1, 0, vz0)     # under the module's -x side, its whole length
    bar = box(xi0 - 0.01, vein[1], yi0 - 0.01, vy0 + 2.5, 0, vz0)       # under its front end
    post_xy = (vein[1] - 3.5, vy1 - 2.0)                                # under its back +x corner, through the board's
    post = cyl_z(*post_xy, 1.3, 0, vz0)                                 # 3.2 hole P1
    bx0, bx1, by0, by1 = shelf.val().BoundingBox().xmax + 0.3, xi1 - 0.05, bar.val().BoundingBox().ymax + 0.3, yi1 - 0.3
    # the board: an L (clear of the shelf and the bar), out under the VoiceS3R to the outer faces
    pcb = box(bx0, bx1, by0, by1, ZB, ZBT).union(box(ax - 12.0, ax + 12.0, ay - 12.0, ay + 12.0, ZB, ZBT))
    DY = 1.5                                                          # DB9 centre, mating face to +x on bx1
    d9 = on(bx1 - 10.5, bx1 - 0.5, DY - 15.0, DY + 15.0, 0, 12.5).union(on(bx1 - 1.0, bx1, DY - 15.4, DY + 15.4, 0, 12.5))
    d9shell = on(bx1, bx1 + 6.0, DY - 8.5, DY + 8.5, 2.0, 10.5)
    d9plug = box(bx1 + 0.8, bx1 + 40.0, DY - 15.15, DY + 15.15, ZBT - 0.75, HOOD_TOP)
    # under the vein module (the footprints' extents, build_board.py print_b): J3 opening +y with its plug under the
    # module's socket end, SW1 (lid and module off to set), MAX3232 with C1..C4 / C5 beside it, R1 / R2
    j3x, j3y = -14.5, vy1 - 0.5 - 6.0 - 3.1
    j3 = on(j3x - 6.01, j3x + 6.01, j3y - 3.72, j3y + 3.1, 0, 3.4)
    j3p = on(j3x - 3.0, j3x + 3.0, j3y + 3.1, j3y + 9.1, 0.3, 3.1)
    sw1 = on(-20.72, -8.28, -5.83, 5.83, 0, 3.0)
    u1 = on(-9.72, -2.28, -17.22, -6.6, 0, 1.75)
    caps = on(-12.75, -11.25, -21.0, -6.0, 0, 0.9).union(on(-5.75, -4.25, 3.5, 9.5, 0, 0.9))
    slack = box(vein[0] + 2.3, -13.0, by0 + 0.3, -21.5, ZBT, vz0 - 0.3)  # the vein cable's slack under the module
    # the 9P plug and its wires bent down at the module's back end (2.0 out of it), down into J3's plug
    plug9 = box(j3x - 7.2, j3x + 7.2, vy1, vy1 + 2.0, ZBT + 0.3, vz0 + 5.0).union(
        box(j3x - 3.0, j3x + 3.0, j3y + 9.1, vy1, ZBT + 0.3, ZBT + 3.1))
    gx = 5.4                                                          # J6 on the back edge behind the DB9, opening +y
    gf = by1 - 2.3                                                    # its front, 2.3 inside the board edge
    grove = on(gx - 6.0, gx + 6.0, gf - 7.7, gf, 0, 6.0)
    groveplug = on(gx - 4.5, gx + 4.5, gf, yi1 + 6.0, 0.6, 5.4)
    # J1 / J2 turned a quarter with the VoiceS3R (vein-base's x_vb -> y, y_vb -> -x): J1 (5 pins) at y = ay + 7.62
    # from x = ax - 2.54, J2 (4 pins) at y = ay - 7.62 from x = ax, both to ax + 7.62 (the USB-C side)
    hdr = on(ax - 3.81, ax + 8.89, ay + 6.35, ay + 8.89, 0, 2.5).union(on(ax - 1.27, ax + 8.89, ay - 8.89, ay - 6.35, 0, 2.5))
    atom_box = rbox(ax - 12, ax + 12, ay - 12, ay + 12, Z_ATOM, Z_ATOM + 16.8, 3.0)
    usb = box(ax + 12 + 6.5, ax + 12 + 24, ay - 6, ay + 6, Z_ATOM + 4, Z_ATOM + 11).union(
        box(ax + 12, ax + 12 + 6.5, ay - 4.2, ay + 4.2, Z_ATOM + 6, Z_ATOM + 9))
    porta = box(ax + 12, ax + 12 + 10.2, ay - 4.9, ay + 4.9, Z_ATOM, Z_ATOM + 4)
    vbox = vein_step_box((-(vy1 - vy0) / 2, (vy1 - vy0) / 2, -vw / 2, vw / 2), vz0).rotate((0, 0, 0), (0, 0, 1), -90) \
        .translate(((vein[0] + vein[1]) / 2, (vy0 + vy1) / 2, 0))      # the socket end (the step box's -x) to +y
    holes = [(-22.5, -10.0), (-5.0, 13.0), (4.5, 0.0), (3.5, -27.0)]   # the board's M2 screws (H1..H4)
    bs = bosses(holes)
    # open round the VoiceS3R: the body to 1.0 behind it (a floor rib across there goes whole, no sliver), the lid from
    # inside the vein module's window (no strip between them)
    corner = box(ax - 12.3, xi1 + T_WALL + 1, yi0 - T_WALL - 1, ay + 13.0, 0, Z_TOP + 1)
    corner_lid = box(vein[1] - 0.25 - 1.85, xi1 + T_WALL + 1, yi0 - T_WALL - 1, ay + 12.3, Z_IN - 3, Z_TOP + 1)  # past
                                                    # the window's R1.75 corner (a straight cut at its edge left 0.05)
    wall_cuts = [box(xi1 - 1, xi1 + 5, ay + 12.0, DY + 15.65, ZBT - 1.5, HOOD_TOP + 0.5),       # DB9 on the +x wall,
                                                                     # on into the open corner (no sliver between)
                 corner,
                 box(gx - 5.0, gx + 5.0, yi1 - 1, yi1 + 5, ZBT - 0.3, ZBT + 6.4)]             # the Grove plug (back)
    # the vein module's step through the window (57.5 x 25.5), its body on a 0.7 recess (59.4 x 26.4); the lid stops
    # at the VoiceS3R's corner; the DB9 is under the lid now
    win = (vein[0] + 0.25, vein[1] - 0.25, vein[2] + 0.75, vein[3] - 0.75)
    rec = (vein[0] - 0.2, vein[1] + 0.2, vein[2] - 0.2, vein[3] + 0.2)
    lid_cuts = [rbox(*win, Z_IN - 3, Z_TOP + 1, 1.75), rbox(*rec, Z_IN - 3, Z_IN + RECESS_B, 2.2), corner_lid]
    parts = [('DB9', d9), ('DB9 plug', d9plug), ('MAX3232', u1), ('caps', caps), ('SW1', sw1), ('J3', j3),
             ('J3 plug', j3p), ('cable slack', slack), ('9P plug + wires', plug9), ('Grove', grove),
             ('Grove plug', groveplug), ('headers', hdr), ('VoiceS3R', atom_box), ('USB plug', usb),
             ('PORT.A plug', porta), ('vein', vbox)]
    # what drops in from above with the board (J6 by its courtyard, the screws by a driver's room) keeps the ledges off
    on_board = [('MAX3232', xy_box(u1)), ('caps', xy_box(caps)), ('SW1', xy_box(sw1)), ('J3', xy_box(j3)),
                ('J6', (gx - 6.6, gx + 6.6, gf - 10.2, gf + 0.6)), ('headers', xy_box(hdr)), ('DB9', xy_box(d9))] + \
        [(f'H{i}', (x - 1.9, x + 1.9, y - 1.9, y + 1.9)) for i, (x, y) in enumerate(holes, 1)]
    stand = shelf.union(bar).union(post)
    tray, lid, size, screws = shell_and_lid(xi0, xi1, yi0, yi1, wall_cuts, lid_cuts, Z_IN,
                                            keep_clear=[o for _, o in parts] + [d9shell, corner], tht=[d9, hdr],
                                            floor=[bs, stand], rib_floor=ZB, ledge_avoid=[r for _, r in on_board])
    tray = tray.union(bs).union(stand)
    inner = (xi0, xi1, yi0, yi1)
    notches = ledge_notches(screws, inner, (bx0, bx1, by0, by1))
    assert notches == sorted(NOTCHES_B), f'NOTCHES_B (here and in build_board.py print_b) should be {notches}'
    pcb_v = pcb
    for n in notches:
        pcb_v = pcb_v.cut(box(*n, ZB - 1, ZBT + 1))
    for x, y in holes:
        pcb_v = pcb_v.cut(cyl_z(x, y, 1.1, ZB - 1, ZBT + 1))
    pcb_v = pcb_v.cut(cyl_z(*post_xy, 1.6, ZB - 1, ZBT + 1)).cut(box(bx1 - 1.0, bx1 + 1, by1 - 1.0, by1 + 1, ZB - 1, ZBT + 1))
    # (its back +x corner cut 1.0 square: square, it ran into the R1.2 of the box's inside corner)
    way_in(screws, inner, on_board + [('vein', vbox), ('VoiceS3R', atom_box)], board=pcb_v)
    bad = check((tray.cut(bs), lid), parts + [("board", pcb_v)])
    vp = [(k, l, c, o, g, s.rotate(((vein[0] + vein[1]) / 2, (vy0 + vy1) / 2, 0),
                                   ((vein[0] + vein[1]) / 2, (vy0 + vy1) / 2, 1), 180))
          for k, l, c, o, g, s in vein_parts(vein, vz0, along_y=True, step=True)]
    view = [('shell', 'ふた(指静脈の窓と裏の座ぐり、VoiceS3R の角は開けたまま。M2 皿ねじで本体の受けに締める)', '#2b2f33', 0.45, 'shell', lid),
            ('atom', 'VoiceS3R(公式 CAD、USB-C は右 +x、リセットは手前。右手前の角は壁もふたも無く、右と手前の面は箱の面とそろう。ピンヘッダーだけで支える)', '#1fa49a', 1, 'mods', atom_at(ax, ay, 'x+'))] + vp + [
        ('pcb', 'station 基板 print_b(build_board.py print_b。指静脈の台を避けた L 字、ふたの受けの所は切り欠く)', '#1f7a4d', 1, 'mods', pcb_v),
        ('stand', f'指静脈の台(本体と一体: 左の壁の棚・手前の横木・右奥の柱。基板から {HC_B:g} 上)', '#8fa09c', 1, 'mods', stand),
        ('db9', 'DB9 オス(右の側面、VoiceS3R の後ろ。ふたの下)', '#8a8f96', 1, 'mods', d9.union(d9shell)), ('db9plug', 'DB9 プラグ', '#5c6166', 1, 'mods', d9plug),
        ('u1', 'MAX3232・C1〜C5・R1 / R2(指静脈の下)', '#202326', 1, 'mods', u1.union(caps)),
        ('sw1', 'SW1 DIP(指静脈の下。ふたと指静脈を外して切り替え)', '#c0392b', 1, 'mods', sw1),
        ('j3', 'J3 とプラグ(指静脈のソケットの端の下、口は奥)', '#f1efe8', 1, 'mods', j3.union(j3p)),
        ('plug9', '指静脈の 9P プラグと J3 へ下りる線(奥の端から 2.0)', '#e7e1cf', 1, 'mods', plug9),
        ('slack', '指静脈のケーブルの余り(指静脈の下、左手前)', '#d9775c', 1, 'mods', slack),
        ('grove', 'J6 Grove とプラグ(奥の端、DB9 の後ろ。口は奥)', '#c47f0e', 1, 'mods', grove.union(groveplug)),
        ('usb', 'USB-C / PORT.A プラグ(右の側面)', '#24292d', 1, 'mods', usb.union(porta)),
        ('lid', '本体(床・壁・ボス・リブ・指静脈の台・ふたのねじの受け、MJF PA12 で造形)', '#8fa09c', 0.9, 'lid', tray)]
    return view, bad, size, tray, lid, screws, Z_TOP


VEIN_NOTE = {'a': 'ふたは DB9 の上を切り欠いて(DB9 とプラグのフードはふたより上に出る)、中のケーブルの余りの上まで下げた。'
                  f'指静脈はふたから {VEIN_Z0 + 15.0 - (Z_IN_A + T_TOP):.1f} 出る。本体と一体の柱 4 本(基板の穴を通す)に VHB で載せる',
             'b': f'指静脈は本体と一体の台(左の壁の棚・手前の横木・右奥の柱、基板から {HC_B:g} 上)に載せ、ふたで押さえる(指静脈 Unit P と同じ段差受け)。'
                  f'上の段(57 × 25、高さ 2.0)がふたの窓 57.5 × 25.5 を通り、下の胴(59 × 26)がふたの裏の座ぐり(深さ {RECESS_B:g}、59.4 × 26.4)に当たって、'
                  f'上面はふたから {HC_B + 15.0 - (Z_IN_B + T_TOP - ZBT):.1f} 出る。指静脈の下に J3・SW1・MAX3232・C1〜C5・R1 / R2 とケーブルの余り'
                  '(SW1 はふたと指静脈を外して切り替える)。VoiceS3R の角は壁もふたも無く、ピンヘッダーだけで支える'}
RIB_SHOWN = {'a': RIB_FLOOR, 'b': ZB}   # the floor ribs' height in the table (B: up to the board)
out = os.path.join(ROOT, 'station')
failed = []
for key, fn, title in (('a', concept_a, 'A 一列(薄型)'), ('b', concept_b, 'B 2 列(短い)')):
    view, bad, size, tray, lid, screws, z_top = fn()
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
            ('リブ', f'反り止め(JLC3DP の勧め)。幅 {RIB_W:g} を約 {RIB_PITCH:g} おきの格子に、床(高さ {RIB_SHOWN[key]:g}、基板の下。THT の足とボスを避ける)と'
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
               '(m5stack/M5_Hardware、MIT License)。単位 mm。', z_top, stls)
if failed:
    raise SystemExit('interference: ' + ', '.join(failed))
