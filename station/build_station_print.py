"""Vein Station, printed (MJF PA12) instead of a machined Takachi case, with the station board drawn anew to suit:
two concepts to compare, the case and the parts' places only (the board is not routed yet).
  A  one row like SW130 (DB9 | SW1, J3 and the cable | vein module | VoiceS3R), lower: the MAX3232 and its caps go
     under the vein module inside its printed frame, so the module sits 2.9 over the board instead of on spacers.
  B  two rows: the vein module on the left straight on the board (as Vein Unit P, nothing under it), the cable's slack
     folded along both its long sides, under a hood that holds it down on its step (as Vein Unit P) and is screwed up
     from under the floor through the board (v0.55; from under the board v0.50..v0.54), its +x wall cut where the cable leaves it for J3 (vertical, beside the Grove, v0.48); on the
     right, with no walls nor lid, from the front: J3 and the Grove (NFC) on the front edge (opening -y), the DB9 (mating face +x), the VoiceS3R
     at the back (USB-C on the box's back face, its reset on the box's +x face) with SW1, MAX3232, C1..C5 and R1 / R2
     under it; a support along the board's edge all round from the floor up to it. The board is screwed to the floor
     by one of its own (countersunk up from under the floor, a nut on the board; v0.57). v0.56: the board square, the hood
     with a shelf over the right column's front (on three legs, screwed from under the floor) and the Unit NFC on it,
     screwed down through its two holes onto the shelf's posts.
  C  A's one row without the DB9 (no RS232, no NFC: J1 / J2 and J3 only): J3 | the vein module under B's hood (its
     cable's slack along both its long sides) | the VoiceS3R at the +y end (USB-C on the end face), no walls round it,
     held down by B's stepped post and screw. The hood's four screws all go through the board.
The boards are drawn and routed (pcb/station_board/build_board.py print_a / print_b / print_c).
Both: a tray (floor 1.6, walls 1.8) with bosses for the board (2 high, M2 self-tapping), a flat lid (1.8) with a
locating rim. A: the vein module on four posts from the floor; the lid is notched round the DB9 (which stands up
through it) and the VoiceS3R's plugs, so it comes down to the cable's slack. B (v0.50): a floor (2.0) with ribs and
four bosses for the board's own screws (M2 x 8 countersunk up from under the floor, nuts on the board), and a hood over
the vein module and its cable's slack only: its 57 x 25 top step through the window, its body against a 0.7 recess,
walls all round (a closed frame) and four square columns all standing on the board, screwed up from under the floor
through bosses and the board (M2 x 12 countersunk machine screws, as C; v0.55); the VoiceS3R screwed to the board from under it too (M2 x 8 pan head through its M2 hole, v0.55). C: B's hood up to
v0.49: five M2 x 12 countersunk machine screws up from under the floor (the hood's four through the board, the
VoiceS3R's one through a stepped post), none for the board alone (hood_over_vein / atom_post / floor_screws). Writes site/station-print-{a,b,c}/ and
station/vein_station_print_{a,b,c}_v<VERSION>_{body,lid}.stl (B / C: lid = the hood), and fails on any
interference.
Run from the repository root:  python3 station/build_station_print.py
Coordinates: x across, y along (B: -y = the front, the user's side; C: -y = the J3 end), z = 0 on the floor's inside face."""
import math
import os
import cadquery as cq
from shapes import (ROOT, VER, box, rbox, cyl_z, union, vein_parts, vein_step_box, write_page, shell_and_lid, check,
                    rib_grid, xy_box, xy_overlap, T_WALL, T_FLOOR, T_TOP, LEDGE_D, LEDGE_W, LEDGE_H, RIB_W, RIB_PITCH,
                    RIB_FLOOR, RIB_LID, PILOT, CLEAR, CSK, atom_at, pins, db9, grove_at, grove_hole, VEIN_RECESS,
                    CABLE_END, CABLE_SIDE, vein_z_in, vein_lid_cuts, vein_cable, vein_cable_sides, HY20_W, HY20_H, HY20_DEPTH,
                    DB9_PLUG_W, DB9_SHELL_L, DB9_SHELL_W, DB9_PIN_FACE, DB9_HALF_W, DB9_LEGACY)

BOSS = 2.0                       # the board stands on printed bosses (M2 self-tapping screws)
ZB = BOSS
ZBT = ZB + 1.6                   # board top
Z_ATOM = ZBT + 2.5               # VoiceS3R bottom on the pin headers (plastic 2.5), top + 16.8
Z_ATOM_B = ZBT + 3.5             # B: measured on the real one (2026-10-07): its bottom 3.5 over the board, top + 20.3
DB9_TOP, HOOD_TOP = ZBT + 12.5, ZBT + 13.25
Z_IN_A = ZBT + 8.7 + 0.4         # A: the DB9 outside the lid (a notch), so the lid goes down to the cable's slack
HOOD_UP_B = 0.5                  # B / C: the hood's top raised over the stack (ribs + board + module) by the gap the
                                 # user measured on the real B (2026-10-21: the hood's -x walls stood 0.5 off
                                 # the floor with the module on the board; the stack had no margin)
Z_IN_B = vein_z_in(ZBT) + HOOD_UP_B   # B: the vein module straight on the board (as Vein Unit P), held down by the hood
HX1_B = -1.2                     # B: the hood's +x wall's inside (the right column is placed from it)
J3_ROOM = 1.8                    # B: over J3's mated plug (5.7) for the wires' bend (as Vein Unit P's J1_ROOM)
J3_MATED = 5.7                   # J3 (53398-0471) with the 4P plug in it, over the board
# B (v0.48): J3 turned 270 (its pads' row along y, its signal pads to +x; KiCad's footprint): its fitting nails' pads
# (MP) x -3.0..0 and ±5.475 along y off the origin, the signal pads' +x end 1.9, its housing (Fab) x -2.6..1.1 and
# ±5.075, its courtyard x -3.525..2.425 and ±6.005
J3_MP_X, J3_MP_Y, J3_PAD_X = 3.0, 5.475, 1.9    # (J3_MP_X: the origin to the MP's -x end, J3_MP_Y: to its front)
J3_BODY = (-2.6, 1.1, 5.075)
J3_CRT = (-3.525, 2.425, 6.005)
HY20_CRT = 0.575                 # J6's (the HY2.0's) courtyard past its body's -x / +x ends (its footprint)
# The tails under the board, measured on the real v0.38 B (the user, 2026-10-18; the parts list's "tail 3 mm" is the
# standard's value, not the real one): J1 / J2 (XFCN PZ254V-11-05P / 04P-A40, C42419912 / C42419911; mating 4, plastic
# 2.5) 1.5 under the board, the DB9's (J4) thick fixing legs 2.5 (its signal pins are shorter: all taken as 2.5). The
# board's underside is ZB = 2.0 over the floor's top: J1 / J2's tips stay clear of the floor, the DB9's go 0.5 into it,
# so the floor has a hole through it under the DB9's legs (B only; C has no DB9).
TAIL_HDR = 1.5
TAIL_DB9 = 2.5
TAIL_GAP_MIN = 0.5               # the tails' tips off the floor's top (J1 / J2) / off the desk (the DB9's holes)
DB9_HOLE_D = 5.0                 # the DB9's holes: round, through the floor under each fixing leg (the user, 2026-10-18)
DB9_FIX_D = 3.2                  # the fixing legs' diameter (the footprint's drill 3.2, pad 4)
TAIL_DB9_SIG = 1.5               # the DB9's signal pins: the user measured "shorter than 2.0"; 1.5 (as J1 / J2) is a guide

def tail_gap_hdr():
    """J1 / J2's tails' tips over the floor's top, 0.5 at least (the tails do not reach the floor)."""
    gap = ZB - TAIL_HDR
    assert gap >= TAIL_GAP_MIN - 1e-9, f'the pin headers\' tails come {gap:.2f} off the floor'
    return gap


def db9_tail_holes(face, c):
    """B: the DB9's tails (J4: KiCad's DSUB-9_Male_Horizontal_P2.77x2.84mm_EdgePinOffset7.70mm_Housed_..., turned to
    the +x face as build_board.py print_b does: row 1 (pins 1..5, local y 0) DB9_PIN_FACE (10.94, the footprint's F.Fab;
    7.70 before v0.47) in from the flange at `face`, row 2
    (pins 6..9, local y 2.84) 2.84 nearer it, pin pitch 2.77, the two fixing legs (pad 0) at local (-6.96, 1.42) and
    (18.04, 1.42) i.e. 12.5 either side of the row's centre `c`, 1.42 in from row 1) and the round holes through the
    floor under the two fixing legs (2.5 long, 0.5 into the floor). The signal pins are shorter than 2.0 (measured), so
    they get no hole (taken as 1.5, a guide, for the interference check). Returns (tails, holes (x, y, d), the fixing
    tails' tips off the desk)."""
    x1 = face - DB9_PIN_FACE
    sig = [(x1, c + (i - 2) * 2.77) for i in range(5)] + [(x1 + 2.84, c + (j - 1.5) * 2.77) for j in range(4)]
    fix = [(x1 + 1.42, c - 12.5), (x1 + 1.42, c + 12.5)]
    tails = pins(sig, ZB - TAIL_DB9_SIG, ZB)
    for x, y in fix:
        tails = tails.union(cyl_z(x, y, DB9_FIX_D / 2, ZB - TAIL_DB9, ZB))
    desk = T_FLOOR_B + ZB - TAIL_DB9
    assert desk >= TAIL_GAP_MIN, f'the DB9\'s tails come {desk:.2f} over the desk'
    return tails, [(x, y, DB9_HOLE_D) for x, y in fix], desk


DB9_GAP_B = 0.3                  # B: the DB9's flange off the VoiceS3R's back face (as v0.39). Its shell's tip is at the
                                 # board's +x edge, so the serial cable's plug (34.2 wide, measured) is out past it
                                 # and clear of the VoiceS3R (the user's, 2026-10-18)
DB9_CUT_B = DB9_SHELL_W + 0.5    # B: the board and the floor cut under the DB9's shell (flange to the edge), half
                                 # across (build_board.py DB9_CUT)
# B: under the VoiceS3R (its bottom 3.5 over the board): MAX3232, C1..C4 / C5, R1, R2 (0603, long side x) and SW1 (the
# footprints' places in build_board.py print_b: keep them together), H_MAX_B high at most. SW1 is the KINGTEK
# DSHP04TSGET (C40736, half pitch, 2.30 ± 0.20 high, checked at its most; the user's, 2026-10-08): the CTS
# 219-4LPSTRF (4.05) does not go under the VoiceS3R. v0.46: the VoiceS3R turned with its USB-C to +y (it was +x), and
# all of these a quarter turn with it (the same places round its centre as before)
H_MAX_B = Z_ATOM_B - ZBT - 0.3   # 3.2
U1_B = (12.9, 7.8)               # its long side along x
SMALL_B = [(21.3, 4.8), (21.3, 7.3), (21.3, 9.8), (21.3, 12.3), (3.5, 4.8), (3.5, 7.3), (3.5, 9.8)]
SW1_B = (12.9, 23.1)             # its leads along x
SW1_H = 2.5
SW1_XY = (8.89, 6.68 + 0.4)      # its outline: the pads' span (KiCad's footprint) along the leads, the body across
J6_DB9_B = 2.6                   # B: J6's body's back to the DB9's flange: J6's pads (11.0 behind its front) and courtyard
                                 # (11.85) clear of the DB9's courtyard (0.55 past its flange), 0.05 to spare
EDGE_IN, EDGE_W = 0.3, 1.2       # B: the board's edge support: 1.2 wide, 0.3 inside the board's edge, floor to board
VEIN_Z0 = ZBT + 3.3              # A: the vein module on printed posts, 2.9 over the MAX3232 / caps under it
COL_B = 1.8                      # B: the hood's screw columns (half of 3.6 square): countersunk screws (SCREW_B) up
T_FLOOR_B = 2.0                  # B: the floor (1.6 left 0.65 over the screws' countersinks, 0.95 deep)
COL_IN_B = 1.3                   # from under the floor; their axes this far in from the walls' inside (3.1 from the outside:
                                 # the countersink, r 2.1, stays 1.0 inside the floor's edge)
# B: all five screws (the hood's four, the VoiceS3R's one) are one kind: M2 x 12 countersunk machine screws up from
# under the floor, heads flush. The VoiceS3R's bottom hole (at its centre, the one vein-base screws into) takes an M2
# machine screw (M5's ATOM Mate fixes an Atom by it with M2 x 6 / x 8 machine screws); the official STL has it 2.5
# across in a boss 3.0 high, in a 0.2 recess of the bottom face. The hood's columns are pilot-drilled for the same
# screw to cut its thread in the PA12.
SCREW_B = 12.0                   # M2 x L (a countersunk screw's L includes its head)
PILOT_B = PILOT                  # the pilot for the M2 machine screw in PA12 (1.6, about its core: it cuts its thread
                                 # in the nylon; 1.7 left the 3.6 square columns 0.95 round it, under the 1.0 check)
ATOM_RECESS = 0.2                # the VoiceS3R's bottom face is 0.2 up round its hole (official STL)
# B (v0.50, the user's, 2026-10-21, after the real B: "screwed from below the board, both sit steadier"): the hood is
# screwed to the board from under it (M2 pan-head screws up through H1..H4 into its four columns), the VoiceS3R too
# (a pan-head screw up through the board into its M2 hole: a cut-out and a washer v0.50..v0.54, an M2 hole v0.55; no post: its pins set its
# height), and the board to the floor by four of its own (M2 countersunk screws up from under the floor through bosses
# and the board, nuts on the board's top: H5..H8, build_board.py print_b).
# v0.55 (the user's, 2026-10-29: with the floor on the board first the hood's screws under the board could not be put
# in): the hood's four go up from under the floor through bosses and the board into its columns, as C's (SCREW_B, M2
# machine screws, the user's: no self-tapping), so the floor, the board and the hood are screwed in one go. The
# VoiceS3R's stays under the board (put in first, with the board alone).
SCREW_PAN_B = 8.0                # M2 x 8 pan head (head 4.0 across, 1.3 high): the VoiceS3R's (into its M2 hole)
PAN_D, PAN_K = 4.0, 1.3          # (v0.55: through the board's M2 hole H9 with its pad, no washer: v0.50..v0.54 had a
                                 # 4.8 cut-out there and a 6.0 washer over it)
SCREW_FLOOR_B = 8.0              # M2 x 8 countersunk (L includes the head): floor 2.0 + boss 2.0 + board 1.6 + nut 1.6
NUT_S, NUT_M = 4.0, 1.6          # M2 nut: 4.0 across the flats, 1.6 high
FLOOR_SCREWS = [(21.8, 0.5)]     # H8 (build_board.py print_b HOLES_NOCRT): the right column's, at its +x side behind the
                                 # DB9 (v0.54, the user's, 2026-10-21; the left part's two, H6 / H7, nuts in the hood's
                                 # pockets v0.52..v0.56, are columns of the hood from v0.57). (21.8, -36.95) (H5) was one up to v0.55: a leg of the
                                 # hood's shelf from v0.56 (NFC_LEGS)
# v0.56 (the user's, 2026-10-29, with a photo of the real B with the Unit NFC tied on beside the hood): the board square
# (the right column's front out to the hood's), J6 on its front edge, and the hood with a shelf over the right
# column's front, from the DB9's front to the board's edge, screwed up from under the floor through the board (three
# legs, SCREW_B, as the hood's columns); the Unit NFC (M5Stack U216, official STL: 48 x 24 x 8, two 4.8 holes 12 from
# its Grove end, 8 either side of the middle, through it) on it, its Grove end to the front: two posts of the shelf
# through its holes, an M2 pan-head screw and a washer from above into each
NFC_LEGS = [(21.8, -43.5), (21.8, -36.95), (21.8, -30.3)]   # H10 / H5 / H11 (build_board.py print_b)
NFC_L, NFC_W, NFC_H = 48.0, 24.0, 8.0
NFC_HOLE_Y, NFC_HOLE_X, NFC_HOLE_D = 12.0, 8.0, 4.8
NFC_POST_D = 4.4                 # through its holes, 0.3 under its top (the washer bears on the unit)
SCREW_NFC_B = 8.0                # M2 x 8 pan head
NFC_WASHER_D, NFC_WASHER_T = 6.0, 0.5   # over the 4.8 holes
NFC_OFF_DB9 = 3.0                # B: the Unit NFC's underside over the DB9's top (v0.59). Up to v0.58 it lay on the
                                 # shelf 0.3 over the DB9 and read no card there (the shell's eddy currents, the real
                                 # B 2026-10-29: 2.0 of floor slipped under it and it read); a pad on the shelf lifts it
CSK_FLOOR_B = 4.0                # their countersinks (the M2 countersunk head 3.8 across at most): H7 / H8's 1.1 inside
                                 # the floor's +x face (CSK 4.2 left 0.71 under the 1.0 check)
BOARD_CH = 1.5                   # the board's corners under the hood's -x / front-+x corners chamfered (print_b CH)
ATOM_POST_R = CLEAR / 2 + 1.0    # B: the VoiceS3R's screw post above the board (1.0 round the screw's hole)
ATOM_POST_R0 = 3.5               # its foot under the board (the shoulder the board sits on)
ATOM_CUT_R = ATOM_POST_R + 0.25  # the board's round cut-out for it (build_board.py print_b POST_CUTS)


def on(x0, x1, y0, y1, z0, z1):
    return box(x0, x1, y0, y1, ZBT + z0, ZBT + z1)


def bosses(pts):
    s = None
    for x, y in pts:
        b = cyl_z(x, y, 2.5, 0, ZB).cut(cyl_z(x, y, 0.9, 0.5, ZB + 1))
        s = b if s is None else s.union(b)
    return s


# ---- B / C: the hood over the vein module (screwed up from under the floor into its four columns) and the VoiceS3R's
# stepped screw post (the board clamped between its shoulder and the VoiceS3R's pins)
def thru_bosses(pts):
    """Bosses (2 high) under the board for the hood's screws that go through it (drilled through, no thread: the
    hood's columns clamp the board on them)."""
    bs = None
    for x, y in pts:
        b = cyl_z(x, y, 2.5, 0, ZB).cut(cyl_z(x, y, CLEAR / 2, -1, ZB + 1))
        bs = b if bs is None else bs.union(b)
    return bs


def atom_post(ax, ay):
    """The VoiceS3R's screw post at its centre: a foot (the shoulder the board sits on) up to the board, then through
    the board's round cut-out up to the VoiceS3R's bottom round its M2 hole (in the 0.2 recess), where its pins bottom
    out (measured): longer would lift it off them, shorter would pull it down on them. Returns (post, z of the hole)."""
    z_atom_hole = Z_ATOM_B + ATOM_RECESS
    post = cyl_z(ax, ay, ATOM_POST_R0, 0, ZB).union(cyl_z(ax, ay, ATOM_POST_R, ZB - 0.01, z_atom_hole))
    assert ATOM_POST_R + 0.2 <= ATOM_CUT_R < ATOM_POST_R0 - 0.5, 'the board drops over the post onto its shoulder'
    assert ATOM_POST_R - CLEAR / 2 >= 1.0, 'the post is 1.0 thick round the screw'
    return post, z_atom_hole


def hood_over_vein(vein, outer, inner, walls, cols, thru, z_in, z_top):
    """The hood: the top (window + recess, vein_lid_cuts), walls (walls = [(x0, x1, y0, y1, z0)], each up to the top:
    z0 = 0 down to the floor, ZBT on the board where it runs under them), four columns in its corners (cols, those in
    thru on the board), a 45° fillet under the top along the front and back walls between the columns (the ±x walls
    are the cable's slack's room off the module); all of it inside one R3 outline (the columns too: past it they stood
    0.5 proud of the walls' rounded corners, a slit down each corner); pilot-drilled from below for SCREW_B.
    outer / inner = the hood's outside / inside (x0, x1, y0, y1)."""
    xo0, xh1, yo0, yo1 = outer
    hx0, hx1, hy0, hy1 = inner
    top = rbox(xo0, xh1, yo0, yo1, z_in, z_top, 3.0)
    w = None
    for x0, x1, y0, y1, z0 in walls:
        b = box(x0, x1, y0, y1, z0, z_in + 0.01)
        w = b if w is None else w.union(b)
    for x, y in cols:
        w = w.union(box(x - COL_B, x + COL_B, y - COL_B, y + COL_B, ZBT if (x, y) in thru else 0, z_in + 0.01))
    FIL = 1.5
    for y_w, s in ((hy0, 1), (hy1, -1)):                 # the fillets, between the columns
        x_a, x_b = hx0 + COL_IN_B + COL_B, hx1 - COL_IN_B - COL_B
        f = cq.Workplane('YZ').polyline([(y_w, z_in + 0.01), (y_w + s * FIL, z_in + 0.01), (y_w, z_in - FIL)]).close() \
            .extrude(x_b - x_a).translate((x_a, 0, 0))
        w = w.union(f)
    hood = top.union(w.intersect(rbox(xo0, xh1, yo0, yo1, -1, z_in + 1, 3.0)))
    for c in vein_lid_cuts(vein, z_in, z_top, along_y=True):
        hood = hood.cut(c)
    tip = -T_FLOOR_B + SCREW_B
    for x, y in cols:
        z_col = ZBT if (x, y) in thru else 0.0
        assert tip - z_col >= 6.0 and tip + 1.0 < z_in, 'the hood screw: 6.0 of thread in its column, under the top'
        hood = hood.cut(cyl_z(x, y, PILOT_B / 2, -1, tip + 1.0))
    return hood


def edge_support(edge, cuts, corners, floor):
    """B: a wall along the board's outline (edge, a rectilinear polygon) all round, EDGE_W wide and EDGE_IN inside the
    edge, from the floor's top up to the board's underside (ZB). Each side's strip (between the strips across it) is
    cut over its whole width where it meets an (x0, x1, y0, y1) in cuts (the floor ribs' avoid boxes, the hood's
    columns, where the hood's walls already clamp the board; as rib_grid: no slivers along it), stopped 3.0 short of
    the floor's R3 corners (no slivers over their curve) and kept on the floor; pieces under 1.0 across dropped.
    Returns (the solid or None, [(the side's two ends, its length, the length the support keeps along it)])."""
    area = sum(a * e - d * c for (a, c), (d, e) in zip(edge, edge[1:] + edge[:1])) / 2
    s = 1 if area > 0 else -1               # the inside is on the left of each side (counter-clockwise)
    lo, hi = EDGE_IN, EDGE_IN + EDGE_W
    pieces, sides = [], []
    for (a, c), (d, e) in zip(edge, edge[1:] + edge[:1]):
        if a == d:                          # along y: the inside to -x going +y (counter-clockwise)
            k = -s if e > c else s
            x0, x1 = sorted((a + k * lo, a + k * hi))
            y0, y1 = min(c, e) - hi, max(c, e) + hi
            st = box(x0, x1, y0, y1, -0.01, ZB)
            for u0, u1, v0, v1 in cuts:
                if u0 < x1 and u1 > x0 and v0 < y1 and v1 > y0:
                    st = st.cut(box(x0 - 1, x1 + 1, v0, v1, -1, ZB + 1))
        else:                               # along x: the inside to +y going +x
            k = s if d > a else -s
            y0, y1 = sorted((c + k * lo, c + k * hi))
            x0, x1 = min(a, d) - hi, max(a, d) + hi
            st = box(x0, x1, y0, y1, -0.01, ZB)
            for u0, u1, v0, v1 in cuts:
                if u0 < x1 and u1 > x0 and v0 < y1 and v1 > y0:
                    st = st.cut(box(u0, u1, y0 - 1, y1 + 1, -1, ZB + 1))
        for cx, cy in corners:
            st = st.cut(box(cx - 3.0, cx + 3.0, cy - 3.0, cy + 3.0, -1, ZB + 1))
        # inside the outline 0.3 off it (the strip's ends run past the corners: the outline's inset trims them)
        st = st.intersect(cq.Workplane('XY').polyline(edge).close().offset2D(-lo, 'intersection')
                          .extrude(ZB + 2).translate((0, 0, -1))).intersect(floor)
        keep = [v for v in st.solids().vals() if min(v.BoundingBox().xlen, v.BoundingBox().ylen) >= 1.0 - 1e-6]
        pieces += keep
        sides.append((((a, c), (d, e)), abs(d - a) + abs(e - c),
                      sum(max(v.BoundingBox().xlen, v.BoundingBox().ylen) for v in keep)))
    if not pieces:
        return None, sides
    r = cq.Workplane().add(pieces[0])
    for v in pieces[1:]:
        r = r.union(cq.Workplane().add(v))
    return r, sides


def floor_screws(body, cols, ax, ay, z_atom_hole):
    """The floor drilled and countersunk for the screws (one kind, SCREW_B, up from under it, heads flush): the hood's
    into its columns, the VoiceS3R's through its post into its M2 hole."""
    eng = -T_FLOOR_B + SCREW_B - z_atom_hole
    assert 2.0 <= eng <= 3.0, f'the VoiceS3R screw: {eng:.1f} into its hole (the STL boss is 3.0)'
    for x, y in cols + [(ax, ay)]:
        cone = cq.Workplane().add(cq.Solid.makeCone(CSK / 2, CLEAR / 2, (CSK - CLEAR) / 2,
                                                    cq.Vector(x, y, -T_FLOOR_B), cq.Vector(0, 0, 1)))
        top_c = z_atom_hole + 1 if (x, y) == (ax, ay) else 1
        body = body.cut(cyl_z(x, y, CLEAR / 2, -T_FLOOR_B - 1, top_c)).cut(cone)
    return body


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
    # (the plug as it was modelled, 30.3 wide: the real one (34.2 at most, measured 2026-10-18) hits the front wall's
    # DB9 hole (±15.65). A is not ordered (B was chosen, 2026-10-08), so its shape stays: widen the hole if it is).
    # So does its plug's start, 0.8 off the flange (the real one stops at the shell's tip, 6.0; from there A's lid
    # rim fails to build in shell_and_lid)
    # (A keeps the DB9's shape before v0.47, DB9_LEGACY, as its board keeps pin 1's row 7.70 in from the edge: A is not
    # ordered)
    d9, d9shell, d9plug = db9(0.0, ydb, 'y-', ZBT, HOOD_TOP, plug_w=15.15, plug_from=0.8, **DB9_LEGACY)
    row = by0 + 10.6                         # behind the DB9's body
    # MAX3232, C1..C5 and R1 / R2 under the vein module (2.9 under it: 1.75 / 0.9 / 0.5 high), footprints with pads
    u1 = on(-5.4, 5.3, -17.2, -9.7, 0, 1.75)
    caps = on(-7.9, 7.9, -7.75, -6.25, 0, 0.9).union(on(8.75, 10.25, -13.5, -7.0, 0, 0.5))
    sw1 = on(-16.4, -4.8, row, row + 12.45, 0, 4.05)                 # DIP on -x behind the DB9 (lid off to set)
    j3x, j3y = -0.15, vein[2] - 3.9
    j3 = on(j3x - 5.0, j3x + 5.0, j3y - 3.1, j3y + 3.7, 0, 3.4)     # just in front of the vein socket, opening -y
    j3p = on(j3x - 3.0, j3x + 3.0, j3y - 9.1, j3y - 3.1, 0.3, 3.1)   # its plug between SW1 and J6
    slack = box(xi0 + LEDGE_D + 0.8, 4.5, row + 1.0, row + 15.0, ZBT + 4.35, ZBT + 8.7)   # the vein cable's slack over
                                                    # SW1 / J3 (from SW1 4.05 + 0.3), clear of a lid screw's ledge on the -x wall
    gy = row + 6.62                                                 # J6 (Grove) on +x behind the DB9
    gf = bx1 - 2.3                                                  # its front, 2.3 inside the board edge
    grove, groveplug = grove_at(gy, gf, 'x+', ZBT, out=xi1 + 6.0 - gf)
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
                 grove_hole(gy, xi1, 'x+', ZBT, w=5.0),                                 # the Grove plug
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
            ('atom', 'VoiceS3R(公式 CAD、USB-C は +y)', '#1fa49a', 1, 'mods', atom_at(0, ay, 'y+', Z_ATOM, Z_TOP)),
            ('hdr', 'ピンヘッダー J1 / J2(樹脂の台 2.5 とピン)', '#202326', 1, 'mods',
             hdr.union(pins([(-7.62, ay - 2.54 + 2.54 * i) for i in range(5)] + [(7.62, ay + 2.54 * i) for i in range(4)],
                            ZB, Z_ATOM)))] + \
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
    # two rows. Left: the vein module (its 9P socket end and cable at the front, -y; the finger end at the back)
    # straight on the board (2026-10-08, as Vein Unit P: nothing under it but flat pads and tracks, the floor's ribs
    # carry the board, so the finger's push goes down through them), J3 just in front of it, under a hood: a top (the
    # window and the recess that hold the module down on its step, as Vein Unit P) and walls all round, down to the
    # floor on -x, the front and the back, down to the board on +x (a closed frame; the recess locates the module
    # sideways). The cable's slack lies as in Vein Unit P: folded along both long sides (CABLE_SIDE) and in the
    # groove under the module, between it and the hood's ±x walls. The hood is held by four countersunk screws
    # (SCREW_B) up from under the floor into columns at its four corners (no screw heads on top). Right (v0.46, the
    # user's, 2026-10-18), from the front: J6 on the front edge (opening -y), the DB9 (mating face +x), the VoiceS3R
    # at the back (USB-C +y on the box's back face, the reset on the box's +x face; on its pin headers and a fifth
    # screw up through a stepped post into its M2 hole at its centre) with MAX3232, C1..C5, R1 / R2 and SW1 under it
    # (set with the VoiceS3R off): no walls nor top, the board and the floor only. The body is the floor with the
    # bosses under the hood's through screws, the VoiceS3R's post, the floor ribs and a support along the board's
    # edge. J3 is a vertical MX1.25 4P (Molex 53398-0471) beside J6 on the right column's front (v0.48, the user's,
    # 2026-10-18; it stood just in front of the 9P plug before), its pads' row along y, its locking window (the tails'
    # side) to +x: the cable is made with its two latches on one face, leaves the 9P latch up to -y, turns +x in front
    # of the module's end, goes out through a cut in the hood's +x wall and into J3 from above, so the wires keep their
    # order (-y to +y: 3V3, GND, RXD, TXD). The board's left part and the hood stay out to -y where v0.47 had them.
    # The board is pcb/station_board/build_board.py print_b: these places are its footprints (keep them together)
    vw = 26.0
    vx0, vy0 = -29.2, -36.5
    vz0 = ZBT
    vein = (vx0, vx0 + vw, vy0, vy0 + 59.0)                             # the socket end at -y (the front)
    vx1, vy1 = vein[1], vein[3]
    # the left part's front (yf): where v0.47 had it (past J3, which stood just in front of the 9P plug then); v0.48
    # keeps it and the hood's front (the cable runs across in front of the module's end to J3 beside J6; build_board.py
    # print_b: YF)
    yf = -44.8
    # the cable's way for tools/check_cable_order.py (read as literals): out of the 9P end face (its outward normal),
    # the turns it takes flat on its way (+90 = to the left), then down into J3
    face9_n, cable_turns = (0.0, -1.0), (90,)
    # the hood's inside: the cable's slack (CABLE_SIDE) on either side of the module, 0.3 past the board's front, its
    # back columns past the module's end. Its +x wall stays where it was with the module on a stand (the right column
    # is placed from it): the module and the left part moved to -x for the slack on +x, the -x wall for the slack on -x
    hx0, hy0, hy1 = vx0 - CABLE_SIDE, yf - 0.3, vy1 + COL_IN_B + COL_B + 0.3
    hx1 = vx1 + CABLE_SIDE                                # the +x wall's inside
    assert abs(hx1 - HX1_B) < 1e-9, f'the hood\'s +x wall moved: {hx1:.2f} (the right column stands on {HX1_B})'
    xo0, yo0, yo1 = hx0 - T_WALL, hy0 - T_WALL, hy1 + T_WALL
    xh1 = hx1 + T_WALL                                    # the hood's +x face (its +x wall: a closed frame)
    cols = [(hx0 + COL_IN_B, hy0 + COL_IN_B), (hx1 - COL_IN_B, hy0 + COL_IN_B), (hx0 + COL_IN_B, hy1 - COL_IN_B),
            (hx1 - COL_IN_B, hy1 - COL_IN_B)]             # in the hood's four corners, all alike
    ax = xh1 + 0.3 + 12.0                                 # the VoiceS3R 0.3 past the hood
    xo1 = ax + 12.0                                       # its +x face is the box's
    # the right column from the back (v0.46): the VoiceS3R at the back, its USB-C face (+y) the box's back face (the
    # hood's, yo1), its reset (on the face clockwise of the ports, +x) on the box's +x face; the DB9 before it (its
    # flange ±15.4, DB9_GAP_B off the VoiceS3R's front face; the footprint's F.Fab has it ±15.425 (DB9_HALF_W), so the
    # gaps are 0.025 less: the places stay as v0.46), face to +x; J6 before that (opening -y), its front 0.8 inside the
    # right column's front edge (yr0), which follows
    ay = yo1 - 12.0
    DY = ay - 12.0 - DB9_GAP_B - 15.4
    # v0.56: the board square, the right column's front out to the hood's (yo0), J6 on it (its front 0.8 inside);
    # J3 stays where it was up to v0.55, by the right column's front edge then (yj)
    yj = DY - 15.4 - J6_DB9_B - HY20_DEPTH - 0.8
    yr0 = yo0                                             # the right column's front edge
    gx, gf = ax, yr0 + 0.8                                # J6's front
    # J3 (v0.48, the user's, 2026-10-18): vertical beside J6 on the right column's front, between the hood's +x face
    # and J6, its pads' row along y and its locking window (the tails' side, Molex 533980000-SD) to +x (J6's side): the
    # cable (both latches on one face, the wires straight) leaves the 9P latch up to -y, turns +x in front of the
    # module's end, goes through a cut in the hood's +x wall and down into J3 from above, so its latch ends facing +x,
    # the way it last went. Its fitting nails' pads 0.3 off the hood's +x face and 0.5 off the right column's front
    # edge (the board's copper-to-edge clearance, as J6's)
    j3x, j3y = xh1 + 0.3 + J3_MP_X, yj + 0.5 + J3_MP_Y
    j6x0 = gx - HY20_W                                    # J6's body's -x end
    j3_gaps = (j3x - J3_MP_X - xh1, j6x0 - (j3x + J3_PAD_X), j3y - J3_MP_Y - yj,
               (j6x0 - HY20_CRT) - (j3x + J3_CRT[1]))
    assert min(j3_gaps[:2]) >= 0.3 - 1e-9 and j3_gaps[2] >= 0.5 - 1e-9, \
        f'J3 is {j3_gaps[0]:.2f} / {j3_gaps[1]:.2f} / {j3_gaps[2]:.2f} off the hood\'s +x face / J6 / the edge'
    assert j3_gaps[3] >= -1e-9, f'J3\'s courtyard runs {-j3_gaps[3]:.2f} into J6\'s'
    # the hood's +x wall cut for the cable: from the +x front column's back to 1.0 behind J3's body, the board's top up
    # to the hood's top (the top is not cut)
    yc0, yc1 = cols[1][1] + COL_B, j3y + J3_BODY[2] + 1.0
    # the board (v0.50): under the whole hood, out to its faces (its walls and four columns all stand on it, screwed to
    # it from under it), and the right column out to the box's front, +x and back faces; the corners under the hood's
    # -x and front-+x corners chamfered (BOARD_CH)
    # v0.52 (the user's, 2026-10-21: the floor to the board, the hood to the board, nothing from the floor into the
    # hood; "cut the hood round the nuts"): under the left part too, the floor is screwed to the board as in the right
    # column (countersunk up from under the floor, a nut on the board), the nuts in the middle of the hood's front and
    # back walls, in hex pockets cut up into the walls' feet (flats along the wall, NUT_POCKET across; 1.0 of wall left
    # outside, the cable's run across the front / the module's back end just clear inside). The pocket holds the nut
    # while the screw goes in from below. (v0.51 had columns there and the screws into them.)
    # v0.57 (the user's, 2026-10-29: "this screw through too", with the hood screwed up from under the floor through the
    # board from v0.55): columns there again, as the corners' (the cable's run across the front just behind the front
    # one, the module's back end just before the back one, as the corners'), and SCREW_B into them; no nuts
    mids = [((hx0 + hx1) / 2, cols[0][1]), ((hx0 + hx1) / 2, cols[2][1])]
    thru = cols + mids
    # the DB9's mating face to +x, its shell's tip at the box's +x face (the VoiceS3R's): the serial cable's plug,
    # which stops at the tip, is all out past the board's edge. The board and the floor are cut under the shell
    bx1 = xo1 - DB9_SHELL_L                               # the DB9's flange
    cy0, cy1 = DY - DB9_CUT_B, DY + DB9_CUT_B             # the board and the floor cut under the DB9's shell
    brd = ((xo0, xh1, yo0, yo1), (xh1, bx1, yr0, yo1), (bx1, xo1, yr0, cy0), (bx1, xo1, cy1, yo1))
    # its outline without the chamfers (for the edge support, which stops short of those corners) and with them
    # (build_board.py print_b's EDGE)
    edge = [(xo0, yo0), (xo1, yo0), (xo1, cy0), (bx1, cy0), (bx1, cy1), (xo1, cy1), (xo1, yo1), (xo0, yo1)]
    ch = BOARD_CH
    edge_ch = [(xo0 + ch, yo0), (xo1 - ch, yo0), (xo1, yo0 + ch)] + edge[2:7] + [(xo0 + ch, yo1), (xo0, yo1 - ch),
                                                                                (xo0, yo0 + ch)]
    pcb = cq.Workplane('XY').polyline(edge_ch).close().extrude(ZBT - ZB).translate((0, 0, ZB))
    d9, d9shell, d9plug = db9(DY, bx1, 'x+', ZBT, HOOD_TOP)
    d9tails, d9holes, d9desk = db9_tail_holes(bx1, DY)    # the DB9's legs 2.5 under the board, holes through the floor
    gap9 = d9plug.val().BoundingBox().xmin - xo1
    assert gap9 >= -1e-6, f'the DB9 plug comes {-gap9:.2f} in over the board\'s +x edge'
    # J3 with the 4P plug in it: its housing (KiCad's footprint, Fab; turned 270, the pads to +x) up to the mated
    # height 5.7 (as Vein Unit P's J1)
    j3 = on(j3x + J3_BODY[0], j3x + J3_BODY[1], j3y - J3_BODY[2], j3y + J3_BODY[2], 0, J3_MATED)
    # under the VoiceS3R (the footprints' extents, the pads' too; build_board.py print_b): MAX3232 (SOIC-16) along x
    # in front of the post (the DB9's side), C1..C4 on +x of it, C5 and R1 / R2 on -x, SW1 behind the post between the
    # header rows (its leads along x). All of them H_MAX_B under the VoiceS3R at most
    u1 = on(U1_B[0] - 5.2, U1_B[0] + 5.2, U1_B[1] - 3.5, U1_B[1] + 3.5, 0, 1.75)
    caps = None
    for i, (x, y) in enumerate(SMALL_B):
        c = on(x - 1.5, x + 1.5, y - 0.75, y + 0.75, 0, 0.9 if i < 5 else 0.5)
        caps = c if caps is None else caps.union(c)
    sw1 = on(SW1_B[0] - SW1_XY[0] / 2, SW1_B[0] + SW1_XY[0] / 2, SW1_B[1] - SW1_XY[1] / 2, SW1_B[1] + SW1_XY[1] / 2,
             0, SW1_H)
    assert all(abs(a - b) < 1e-6 for a, b in ((U1_B[0], ax), (U1_B[1], ay - 7.9), (SW1_B[0], ax), (SW1_B[1], ay + 7.4),
                                              (SMALL_B[0][0], ax + 8.4), (SMALL_B[0][1], ay - 10.9),
                                              (SMALL_B[4][0], ax - 9.4), (SMALL_B[4][1], ay - 10.9))), \
        'they go with the VoiceS3R'
    cut = (ax - ATOM_CUT_R - 0.7, ax + ATOM_CUT_R + 0.7, ay - ATOM_CUT_R - 0.7, ay + ATOM_CUT_R + 0.7)
    gaps = []
    for name, o in (('MAX3232', u1), ('C / R', caps), ('SW1', sw1)):
        bb = o.val().BoundingBox()
        assert bb.zmax <= ZBT + H_MAX_B + 1e-6, f'{name} reaches the VoiceS3R ({bb.zmax - ZBT:.2f} over the board)'
        assert bb.xmin >= ax - 12 and bb.xmax <= ax + 12 and bb.ymin >= ay - 12 and bb.ymax <= ay + 12, \
            f'{name} is not under the VoiceS3R'
        assert not any(xy_overlap(xy_box(cq.Workplane().add(v)), cut) for v in o.val().Solids()), \
            f"{name} on the post's cut-out (0.7 round it kept free of copper)"
        gaps.append(bb.xmin - xh1)
    # the hood's +x wall stands on the board (x hx1..xh1) beside them: C1 and C5 come nearest
    assert min(gaps) >= 0.6, f'a part under the VoiceS3R is {min(gaps):.2f} off the hood\'s +x wall'
    # the module's 9P plug with its wires bent round its front end (as shapes.vein_cable's, turned: CABLE_END out of the
    # end face, from the +x side's fold to 7.2 past the middle; its runs are C's / Vein Unit P's way round the -x corner
    # to a J3 in front of it, so they are not used here) and the room for the cable: folded along both long sides
    # and across in the groove (vein_cable_sides), across in front of the module's end (between the 9P plug and the
    # hood's +x front column) to +x, through the cut in the hood's +x wall and over J3 into its plug from above (the
    # mated plug 5.7, J3_ROOM over it for the wires' bend); clear of the hood's columns
    plug9 = rbox((vx0 + vx1) / 2 - 7.2, vx1 + CABLE_SIDE, vy0 - CABLE_END, vy0, vz0, vz0 + 1.5 + 3.5, 0.6)
    zc = ZBT + J3_MATED + J3_ROOM
    yb0, yb1 = yc0 + 0.3, vy0 - CABLE_END                # the run across: off the +x front column, up to the 9P plug
    runs = vein_cable_sides(vein, vz0, Z_IN - 0.3, along_y=True) + \
        [box(hx0, j3x + J3_BODY[0], yb0, yb1, ZBT, zc),
         box(j3x + J3_BODY[0], j3x + J3_BODY[1], yb0, j3y + J3_BODY[2], ZBT + J3_MATED, zc)]
    # the run across goes under the hood's top (through the wall's cut): its top 0.5 under the top's underside at least
    j3_gap = Z_IN - zc
    assert j3_gap >= 0.5, f'the cable over J3 is {j3_gap:.2f} under the hood\'s top'
    colz = None
    for x, y in thru:
        c = box(x - COL_B - 0.3, x + COL_B + 0.3, y - COL_B - 0.3, y + COL_B + 0.3, -1, Z_IN)
        colz = c if colz is None else colz.union(c)
    runs = [r.cut(colz) for r in runs]
    cable = union(*runs)
    # J6 on the front edge before the DB9, opening -y: the HY2.0 (C722729), its front 0.8 inside the edge, the Grove
    # plug out past it
    grove, groveplug = grove_at(gx, gf, 'y-', ZBT, out=gf - (yr0 - 8.0), back=HY20_DEPTH, w=HY20_W, h=HY20_H)
    j6_gap = DY - DB9_HALF_W - (gf + HY20_DEPTH)
    assert j6_gap >= 0.3 - 1e-9, f'J6 is {j6_gap:.2f} off the DB9\'s flange'
    assert groveplug.val().BoundingBox().ymin < yr0, 'the Grove plug stays over the board'
    # J3's mated plug and the wires' bend over it (5.7 + J3_ROOM) beside J6 and the Grove plug in it: apart in xy (their
    # heights overlap), 0.3 at least
    ju = xy_box(on(j3x + J3_BODY[0], j3x + J3_BODY[1], j3y - J3_BODY[2], j3y + J3_BODY[2], 0, zc))
    j3_j6 = []
    for o in (grove, groveplug):
        r = xy_box(o)
        j3_j6.append(max(r[0] - ju[1], ju[0] - r[1], r[2] - ju[3], ju[2] - r[3]))
    assert min(j3_j6) >= 0.3, f'J3\'s plug is {min(j3_j6):.2f} off J6 / the Grove plug'
    # J1 / J2 as A / C (turned half a turn, USB-C / PORT.A to +y): J1 (5 pins) at x = ax - 7.62 from y = ay - 2.54, J2
    # (4 pins) at x = ax + 7.62 from y = ay, both to ay + 7.62
    hdr = on(ax - 8.89, ax - 6.35, ay - 3.81, ay + 8.89, 0, 2.5).union(on(ax + 6.35, ax + 8.89, ay - 1.27, ay + 8.89, 0, 2.5))
    hdr_pts = [(ax - 7.62, ay - 2.54 + 2.54 * i) for i in range(5)] + [(ax + 7.62, ay + 2.54 * i) for i in range(4)]
    tails = pins(hdr_pts, ZB - TAIL_HDR, ZB)    # under the board as measured
    tip_gap = tail_gap_hdr()
    atom_box = rbox(ax - 12, ax + 12, ay - 12, ay + 12, Z_ATOM_B, Z_ATOM_B + 16.8, 3.0) \
        .cut(cyl_z(ax, ay, 2.75, Z_ATOM_B - 1, Z_ATOM_B + ATOM_RECESS))    # the recess round its hole (STL)
    ye = ay + 12.0                                        # its USB-C face: the box's back face
    assert abs(ye - yo1) < 1e-9
    usb = box(ax - 6, ax + 6, ye + 6.5, ye + 24, Z_ATOM_B + 4, Z_ATOM_B + 11).union(
        box(ax - 4.2, ax + 4.2, ye, ye + 6.5, Z_ATOM_B + 6, Z_ATOM_B + 9))
    porta = box(ax - 4.9, ax + 4.9, ye, ye + 10.2, Z_ATOM_B, Z_ATOM_B + 4)
    vbox = vein_step_box((-(vy1 - vy0) / 2, (vy1 - vy0) / 2, -vw / 2, vw / 2), vz0).rotate((0, 0, 0), (0, 0, 1), 90) \
        .translate(((vein[0] + vein[1]) / 2, (vy0 + vy1) / 2, 0))      # the socket end (the step box's -x) to -y
    # the VoiceS3R's screw under the board (v0.50, its head between the board and the floor), the board's
    # own four (countersunk up from under the floor through bosses, nuts on the board) and the hood's four (v0.55, up
    # from under the floor through bosses and the board into its columns)
    z_atom_hole = Z_ATOM_B + ATOM_RECESS
    eng = ZB + SCREW_PAN_B - z_atom_hole
    assert 2.0 <= eng <= 3.0, f'the VoiceS3R screw: {eng:.1f} into its hole (the STL boss is 3.0)'
    heads = cyl_z(ax, ay, PAN_D / 2, ZB - PAN_K, ZB)
    head_gap = ZB - PAN_K
    assert head_gap >= 0.2 - 1e-9, f'the VoiceS3R screw\'s head is {head_gap:.2f} over the floor'
    fb = None
    nuts = None
    for x, y in FLOOR_SCREWS:
        b_ = cyl_z(x, y, 2.5, -0.01, ZB)
        fb = b_ if fb is None else fb.union(b_)
        n = cq.Workplane('XY').polygon(6, NUT_S / math.cos(math.pi / 6)).extrude(NUT_M).translate((x, y, ZBT)) \
            .union(cyl_z(x, y, 1.0, ZBT, -T_FLOOR_B + SCREW_FLOOR_B))    # the screw's end past the nut
        nuts = n if nuts is None else nuts.union(n)
    past = -T_FLOOR_B + SCREW_FLOOR_B - (ZBT + NUT_M)
    assert 0.0 <= past <= 1.5, f'the floor screws end {past:.2f} past their nuts'
    # the body: the floor (R3 corners), the bosses, floor ribs up to the board (clear of the THT legs, the screws'
    # heads and the bosses) where the board is
    # (the right column's floor from the hood's +x face on, from yr0: a step at the hood's front corner)
    body = rbox(xo0, xh1 + 3.0, yr0, yo1, -T_FLOOR_B, 0, 3.0).union(rbox(xh1, xo1, yr0, yo1, -T_FLOOR_B, 0, 3.0)) \
        .union(box(xh1, xh1 + 3.0, yr0, yo1, -T_FLOOR_B, 0)).union(rbox(xo0, xh1, yo0, yo1, -T_FLOOR_B, 0, 3.0)) \
        .cut(box(bx1, xo1 + 1, cy0, cy1, -T_FLOOR_B - 1, 1)) \
        .union(fb).union(thru_bosses(thru + NFC_LEGS))
    tht = [bb for o in (d9, hdr) for bb in [xy_box(o)]]
    av = [(a - 1.0, b + 1.0, c - 1.0, d + 1.0) for a, b, c, d in tht] + \
        [(x - 3.5, x + 3.5, y - 3.5, y + 3.5) for x, y in thru + NFC_LEGS] + \
        [(ax - PAN_D / 2 - 1.0, ax + PAN_D / 2 + 1.0, ay - PAN_D / 2 - 1.0, ay + PAN_D / 2 + 1.0)] + \
        [(x - 3.5, x + 3.5, y - 3.5, y + 3.5) for x, y in FLOOR_SCREWS] + \
        [(bx1 - 1.0, xo1, cy0 - 1.0, cy1 + 1.0)] + \
        [(x - d / 2 - 1.0, x + d / 2 + 1.0, y - d / 2 - 1.0, y + d / 2 + 1.0) for x, y, d in d9holes]    # the floor's cut before the DB9 (a rib's end came 0.9 off its corner), the holes under its legs
    for r in brd:
        g = rib_grid(r[0] + 0.5, r[1] - 0.5, r[2] + 0.5, r[3] - 0.5, -0.01, ZB, av)
        if g is not None:
            body = body.union(g)
    # the board's edge support (v0.46, the user's, 2026-10-18): along its outline all round, off what the ribs keep off
    # (1.0) and the hood's columns (1.0 round them)
    floor = rbox(xo0, xh1 + 3.0, yr0, yo1, -1, ZB + 1, 3.0).union(rbox(xh1, xo1, yr0, yo1, -1, ZB + 1, 3.0)) \
        .union(box(xh1, xh1 + 3.0, yr0, yo1, -1, ZB + 1)).union(rbox(xo0, xh1, yo0, yo1, -1, ZB + 1, 3.0)) \
        .cut(box(bx1, xo1 + 1, cy0, cy1, -2, ZB + 2))
    sup, sides = edge_support(edge, av + [(x - COL_B - 1.0, x + COL_B + 1.0, y - COL_B - 1.0, y + COL_B + 1.0)
                                          for x, y in thru],
                              [(xo1, yo0), (xo1, yo1), (xo0, yo0), (xo0, yo1)], floor)
    if sup is not None:
        body = body.union(sup)
    # the hood: walls all round (a closed frame, all of it on the board; the +x wall in two, cut yc0..yc1 for the
    # cable), the four columns on the board, pilot-drilled for SCREW_B up from under the floor through the bosses and
    # the board (v0.55); the floor under them and the board's own screws drilled and countersunk for their heads
    walls = [(xo0, hx0, yo0, yo1, ZBT), (xo0, xh1, yo0, hy0, ZBT), (xo0, xh1, hy1, yo1, ZBT), (hx1, xh1, yo0, yc0, ZBT),
             (hx1, xh1, yc1, yo1, ZBT)]
    hood = hood_over_vein(vein, (xo0, xh1, yo0, yo1), (hx0, hx1, hy0, hy1), walls, thru, thru, Z_IN, Z_TOP)
    # v0.56: the shelf over the right column's front (from the DB9's front to the board's front edge, from the hood's
    # +x wall to the box's +x face, its top at the hood top's underside: the Unit NFC on it 0.3 over the DB9), on
    # a wall on the board (three legs v0.56), pilot-drilled for SCREW_B from under the floor as the columns; two posts on it through
    # the Unit NFC's holes, pilot-drilled for its screws from above
    ys1 = yc1                                             # the back of the +x wall's cut, 0.58 before the DB9's front
                                                          # (out to the DB9's front: a wall under 1.0 by the cut's end)
    assert ys1 <= DY - DB9_HALF_W
    zs0 = Z_IN - T_TOP
    # (into the hood's +x wall, inside the hood's R3 outline there: past it a sliver at its front corner)
    shelf = rbox(xh1 - 3.0, xo1, yo0, ys1, zs0, Z_IN, 3.0).intersect(box(xh1, xo1, yo0, ys1, zs0 - 1, Z_IN + 1)) \
        .union(box(hx1, xh1 + 0.01, yo0, ys1, zs0, Z_IN).intersect(rbox(xo0, xh1, yo0, yo1, zs0 - 1, Z_IN + 1, 3.0)))
    # its support (v0.57, the user's, 2026-10-29: "a wall rather than columns"): one wall along the box's +x face, on
    # the board from the front edge to the shelf's back, as thick as the columns were out to the +x face (the
    # screws' places in it as the columns'; the shelf's R3 corners)
    wall_s = (NFC_LEGS[0][0] - COL_B, xo1, yo0, ys1)
    shelf = shelf.union(box(*wall_s, ZBT, zs0 + 0.01).intersect(rbox(xh1 - 3.0, xo1, yo0, ys1, ZBT - 1, Z_IN, 3.0)))
    assert all(abs(x - NFC_LEGS[0][0]) < 1e-9 and yo0 + COL_B <= y <= ys1 - COL_B for x, y in NFC_LEGS)
    nx0, ny0 = ax - NFC_W / 2, yo0                        # the Unit NFC: its Grove end on the front face
    nfc_holes = [(ax + s * NFC_HOLE_X, ny0 + NFC_HOLE_Y) for s in (-1, 1)]
    # v0.59: the pad on the shelf under the Unit NFC (its footprint over the shelf) lifts it NFC_OFF_DB9 off the DB9
    Z_NFC = DB9_TOP + NFC_OFF_DB9
    assert Z_NFC >= Z_IN, 'the Unit NFC under the shelf\'s top'
    shelf = shelf.union(rbox(nx0, nx0 + NFC_W, ny0, ny0 + NFC_L, Z_IN - 0.01, Z_NFC, 2.0)
                        .intersect(box(nx0, nx0 + NFC_W, yo0, ys1, Z_IN - 1, Z_NFC + 1)))
    # v0.60 (the user's, 2026-10-29): the pad runs on under the rest of the Unit NFC, over the DB9 (0.3 off its top),
    # so nothing is left open between the two
    shelf = shelf.union(rbox(nx0, nx0 + NFC_W, ny0, ny0 + NFC_L, DB9_TOP + 0.3, Z_NFC, 2.0)
                        .intersect(box(nx0, nx0 + NFC_W, ys1 - 0.01, ny0 + NFC_L + 1, DB9_TOP, Z_NFC + 1)))
    # v0.60 (the user's): a column from the board up to the pad under the Unit NFC's back corner on the -x side (by
    # the VoiceS3R; the DB9's body takes the +x half there), its faces 0.3 in from the NFC's sides
    col_n = (nx0 + 0.3, nx0 + 0.3 + 2 * COL_B, ny0 + NFC_L - 0.3 - 2 * COL_B, ny0 + NFC_L - 0.3)
    shelf = shelf.union(box(*col_n, ZBT, DB9_TOP + 0.31))
    for x, y in nfc_holes:
        shelf = shelf.union(cyl_z(x, y, NFC_POST_D / 2, Z_NFC - 0.01, Z_NFC + NFC_H - 0.3))
    tip = -T_FLOOR_B + SCREW_B
    assert tip - ZBT >= 6.0 and tip + 1.0 < zs0, 'the shelf\'s legs: 6.0 of thread, under the shelf'
    for x, y in NFC_LEGS:
        shelf = shelf.cut(cyl_z(x, y, PILOT_B / 2, ZBT - 1, tip + 1.0))
    z_head = Z_NFC + NFC_H + NFC_WASHER_T                 # the NFC screws' heads on the washers
    eng_nfc = (Z_NFC + NFC_H - 0.3) - (z_head - SCREW_NFC_B)
    assert eng_nfc >= 6.0 and z_head - SCREW_NFC_B > zs0 + 1.0, f'the NFC screws: {eng_nfc:.1f} into the posts'
    for x, y in nfc_holes:
        shelf = shelf.cut(cyl_z(x, y, PILOT_B / 2, z_head - SCREW_NFC_B - 1.0, Z_NFC + NFC_H))
    hood = hood.union(shelf)
    nfc = rbox(nx0, nx0 + NFC_W, ny0, ny0 + NFC_L, Z_NFC, Z_NFC + NFC_H, 2.0)
    nfc_scr = None
    for x, y in nfc_holes:
        nfc = nfc.cut(cyl_z(x, y, NFC_HOLE_D / 2, Z_NFC - 1, Z_NFC + NFC_H + 1))
        w_ = cyl_z(x, y, NFC_WASHER_D / 2, Z_NFC + NFC_H, z_head).union(cyl_z(x, y, PAN_D / 2, z_head, z_head + PAN_K))
        nfc_scr = w_ if nfc_scr is None else nfc_scr.union(w_)
    nfc_gaps = (nx0 - xh1, ay - 12.0 - (ny0 + NFC_L), Z_NFC - DB9_TOP, xo1 - (nx0 + NFC_W))
    assert min(nfc_gaps[:2]) >= 0.3 - 1e-9 and nfc_gaps[2] >= NFC_OFF_DB9 - 1e-9 and nfc_gaps[3] >= -1e-9, \
        'the Unit NFC is %.2f / %.2f / %.2f off the hood / the VoiceS3R / the DB9' % nfc_gaps[:3]
    for x, y, d in [(x, y, CSK) for x, y in thru + NFC_LEGS] + [(x, y, CSK_FLOOR_B) for x, y in FLOOR_SCREWS]:
        cone = cq.Workplane().add(cq.Solid.makeCone(d / 2, CLEAR / 2, (d - CLEAR) / 2,
                                                    cq.Vector(x, y, -T_FLOOR_B), cq.Vector(0, 0, 1)))
        body = body.cut(cyl_z(x, y, CLEAR / 2, -T_FLOOR_B - 1, ZB + 1)).cut(cone)
    for x, y, d in d9holes:
        body = body.cut(cyl_z(x, y, d / 2, -T_FLOOR_B - 1, 1))
    pcb_v = pcb
    for x, y in thru + NFC_LEGS + FLOOR_SCREWS + [(ax, ay)]:
        pcb_v = pcb_v.cut(cyl_z(x, y, 1.1, ZB - 1, ZBT + 1))
    parts = [('screw heads', heads), ('nuts', nuts), ('DB9', d9), ('DB9 tails', d9tails), ('DB9 plug', d9plug), ('MAX3232', u1), ('C / R', caps), ('SW1', sw1), ('J3 + 4P plug', j3),
             ('9P plug', plug9), ('cable', cable), ('Grove', grove), ('Grove plug', groveplug), ('headers', hdr), ('header tails', tails),
             ('NFC', nfc), ('NFC screws', nfc_scr), ('VoiceS3R', atom_box), ('USB plug', usb), ('PORT.A plug', porta), ('vein', vbox), ('board', pcb_v)]
    # the way in: the board with its parts and the vein module drop in first, then the hood comes down past them and
    # the VoiceS3R: its walls and columns (which go down to the floor) keep off them in xy
    down = [(xo0, hx0, yo0, yo1), (xo0, xh1, yo0, hy0), (xo0, xh1, hy1, yo1), (hx1, xh1, yo0, yc0),
            (hx1, xh1, yc1, yo1), wall_s, col_n] + [(x - COL_B, x + COL_B, y - COL_B, y + COL_B) for x, y in thru]
    for name, o in parts:
        if name in ('DB9 plug', 'Grove plug', 'USB plug', 'PORT.A plug', 'cable', '9P plug', 'board', 'screw heads', 'nuts',
                    'NFC', 'NFC screws'):
            continue
        assert not any(xy_overlap(xy_box(o), r) for r in down), f'{name} is under the walls / columns of the hood'
    assert not xy_overlap(xy_box(atom_box), (xo0, xh1, yo0, yo1)), 'the VoiceS3R under the top of the hood'
    # J3 and its plug stand out of the hood (no top over them): 0.5 off the way the hood comes down, the cut's edges too
    jb = xy_box(j3)
    j3_down = min(max(r[0] - jb[1], jb[0] - r[1], r[2] - jb[3], jb[2] - r[3]) for r in down)
    assert j3_down >= 0.5 and jb[0] >= xh1 + 0.5, f'J3 is {j3_down:.2f} off the hood\'s walls / columns'
    bad = check((body, hood), parts)
    v = body.intersect(hood).val().Volume()
    if v > 0.01:
        bad.append(f'body/hood {v:.2f}')
    size = (xo1 - xo0, yo1 - yo0, max(Z_ATOM_B + 16.8, Z_NFC + NFC_H) + T_FLOOR_B)
    screws = thru + NFC_LEGS + [(ax, ay)] + FLOOR_SCREWS + nfc_holes
    vp = vein_parts(vein, vz0, along_y=True, step=True)                  # (the socket end at -y)
    print('b: under the VoiceS3R, the nearest part %.2f off the hood\'s +x wall' % min(gaps))
    print('b: J3 at (%.3f, %.3f) turned 270: its fitting nails %.2f off the hood\'s +x face, its pads %.2f off J6, %.2f off the edge, '
          'courtyards %.2f apart; %.2f off the hood\'s walls / columns; the cable over it %.2f under the hood\'s top; '
          'the +x wall cut y %.2f..%.2f; J3\'s plug and bend %.2f off J6, %.2f off the Grove plug'
          % (j3x, j3y, *j3_gaps, j3_down, j3_gap, yc0, yc1, *j3_j6))
    print('b: the DB9 plug starts %.2f past the board\'s +x edge, its flange %.2f off the VoiceS3R, J6 %.2f off it; '
          'the right column y %.2f..%.2f, the VoiceS3R at (%.2f, %.2f), the DB9 at y %.2f, J6 at x %.2f (front %.2f)'
          % (gap9, ay - 12.0 - (DY + DB9_HALF_W), j6_gap, yr0, yo1, ax, ay, DY, gx, gf))
    for (p0, p1), n, kept in sides:
        print('b: edge support (%.2f, %.2f)-(%.2f, %.2f): %.1f of %.1f' % (*p0, *p1, kept, n))
    print(f'b: J1 / J2\'s tails ({TAIL_HDR:g}, measured) end {tip_gap:.2f} over the floor\'s top (keep {TAIL_GAP_MIN:g}); the DB9\'s tails ({TAIL_DB9:g}, '
          f'measured) end {d9desk:.2f} over the desk (keep {TAIL_GAP_MIN:g}); holes through the floor under them: '
          + ', '.join('⌀%.1f at (%.2f, %.2f)' % (r[2], r[0], r[1]) for r in d9holes))
    view = [('shell', f'フード(指静脈の窓と裏の座ぐり、4 面の壁(一周の枠、+x の壁は J3 へのケーブルの所を切り抜き)と柱 6 本(四隅と手前・奥の壁の真ん中、v0.57)。どれも基板の上に立ち、床の裏から M2 × {SCREW_B:g} の皿小ねじ 6 本が床のボスと基板を通って柱に入る(v0.55)。v0.56: 右の列の手前に DB9 の手前から基板の縁まで覆う棚(上面はフードの天板の裏の高さ、+x の面に沿った壁(v0.57、v0.56 は足 3 本)で基板の上に立ち、床の裏から M2 × {SCREW_B:g} の皿小ねじ 3 本で締める)と、NFC の穴に通す柱 2 本)', '#2b2f33', 0.45, 'shell', hood),
            ('nfc', f'Unit NFC(M5Stack U216、公式 STL の外形 48 × 24 × 8、穴 ⌀{NFC_HOLE_D:g} × 2 は Grove の端から {NFC_HOLE_Y:g}・中心から ±{NFC_HOLE_X:g})。棚に載せ、Grove の端を手前に。棚の柱を穴に通し、上から M2 × {SCREW_NFC_B:g} のなべ小ねじとワッシャー(外径 {NFC_WASHER_D:g})で留める。棚の上の台 (v0.59) で持ち上げ、裏は DB9 の上面から {Z_NFC - DB9_TOP:.1f}', '#e8e4da', 1, 'mods', nfc.union(nfc_scr)),
            ('atom', f'VoiceS3R(公式 CAD、右の列の奥の端。USB-C は奥 +y で箱の奥の面、リセットはポートの面の時計回りの隣 = 右 +x の面で箱の右の面にそろい、どちらも前に何も無い。基板から 3.5 浮き、下に MAX3232・SW1 など。基板の下から M2 × {SCREW_PAN_B:g} のなべ小ねじで底の中心の穴に留める)', '#1fa49a', 1, 'mods', atom_at(ax, ay, 'y+', Z_ATOM_B, Z_TOP)),
            ('hdr', 'ピンヘッダー J1 / J2(樹脂の台 2.5 とピン。VoiceS3R の底は基板から 3.5 で、ピンが底に当たる)', '#202326', 1, 'mods',
             hdr.union(pins(hdr_pts, ZB - TAIL_HDR, Z_ATOM_B)))] + vp + [
        ('pcb', 'station 基板 print_b(build_board.py print_b。フードの下全体と右の列。指静脈の下は平らで、パッドと配線だけ。フードは床の裏からのねじで基板ごと床に締め、VoiceS3R は基板の下からねじで留め、基板はほかに右の列の DB9 の +x 側の 1 か所で床に留める(基板の上にナット))', '#1f7a4d', 1, 'mods', pcb_v),
        ('screws', f'ねじ: VoiceS3R のなべ小ねじの頭(基板の下)、床と基板の皿小ねじのナット(基板の上)', '#9aa0a6', 1, 'mods', heads.union(nuts)),
        ('db9', 'DB9 オス(右の列の J6 と VoiceS3R の間、口は右。口の筒の先端は右の縁で、筒の下の基板と床は切り抜いてある)', '#8a8f96', 1, 'mods', d9.union(d9shell)), ('db9plug', 'DB9 プラグ', '#5c6166', 1, 'mods', d9plug),
        ('u1', 'MAX3232・C1〜C5・R1 / R2(VoiceS3R の下)', '#202326', 1, 'mods', u1.union(caps)),
        ('sw1', f'SW1 DIP 4P KINGTEK DSHP04TSGET(C40736、ハーフピッチ、高さ 2.30 ± 0.20。VoiceS3R の下で、VoiceS3R を外して切り替え)', '#c0392b', 1, 'mods', sw1),
        ('j3', 'J3 MX1.25 4P 縦型(53398-0471)と 4P プラグ(右の列の手前、フードの +x の外面と J6 の間、上から挿す)。ロックの窓(シルクの △ LOCK)は +x(J6 の側)。手前(−y)から 3V3・GND・RXD・TXD', '#f1efe8', 1, 'mods', j3),
        ('plug9', f'指静脈の 9P プラグと手前の端を回る線(端面から {CABLE_END:g}。窓を上にして手前から見て左が 1 番、3〜6 = 赤・黒・緑・黄)', '#e7e1cf', 1, 'mods', plug9),
        ('cable', f'9P → 4P のケーブル(自作、両端のロックが同じ面でまっすぐ)の置き場: 余りは指静脈の両側面に厚さ {CABLE_SIDE:g} で折り返し、底の溝も使える。9P から手前(−y)へ出て指静脈の端の手前を +x へ、フードの +x の壁の切り抜きを通って J3 の上へ、上から挿す。巻き方は実物で合わせる', '#d9775c', 1, 'mods', cable),
        ('grove', 'J6 Grove(HY2.0 4P 横型、C722729)とプラグ(右の列の手前の縁(v0.56 から基板は四角で、縁はフードの手前の面と同じ)、口は手前。NFC のケーブルは箱の手前で折り返して挿す)', '#c47f0e', 1, 'mods', grove.union(groveplug)),
        ('usb', 'USB-C / PORT.A プラグ(奥の面)', '#24292d', 1, 'mods', usb.union(porta)),
        ('lid', f'本体(床・フード・棚と基板を留めるねじのボス 10 本(床の裏から皿穴)・リブと基板の縁の受け(幅 {EDGE_W:g}、縁から {EDGE_IN:g} 内側、床から基板の裏まで)、MJF PA12 で造形)', '#8fa09c', 0.9, 'lid', body)]
    return view, bad, size, body, hood, screws, Z_TOP


def concept_c():
    Z_IN, Z_TOP = Z_IN_B, Z_IN_B + T_TOP
    # one row as A without the DB9 (so no MAX3232, C1..C5, R1 / R2, SW1 nor J6: the board has J1 / J2 and J3 only; no
    # NFC), for places that need no RS232 (by a blood pressure monitor, say). Along y: J3 (vertical, its locking window
    # to -y) | the vein module (its 9P end at -y) straight on the board under B's hood, the cable's slack folded along
    # both its long sides inside it (as Vein Unit P / B) | the VoiceS3R at the +y end on J1 / J2 (USB-C / PORT.A to
    # +y as A, on the box's end face), with no walls nor top round it (the board and the floor only), held down as B's
    # by a screw up through a stepped post into its M2 hole. The board runs under the whole hood (its corners
    # chamfered inside the floor's R3): all four columns stand on it and their screws go through it (the hood clamps
    # the board to the floor's bosses there, as B's +x columns).
    # The board is pcb/station_board/build_board.py print_c: these places are its footprints (keep them together)
    vw = 26.0
    vx0, vy0 = -13.0, -29.5
    vz0 = ZBT
    vein = (vx0, vx0 + vw, vy0, vy0 + 59.0)                             # the 9P end at -y
    vx1, vy1 = vein[1], vein[3]
    # J3 as in B: its fitting nails' pads 0.3 off the 9P plug, x the module's middle; the lock mark's room before it
    j3x, j3y = vx0 + vw / 2, vy0 - CABLE_END - 0.3 - 3.0
    yf = j3y - 1.9 - 0.15 - 0.6 - 0.35
    hx0, hx1 = vx0 - CABLE_SIDE, vx1 + CABLE_SIDE                      # the slack's room on both sides (as B)
    hy0, hy1 = yf - 0.3, vy1 + COL_IN_B + COL_B + 0.3
    xo0, xo1, yo0, yo1 = hx0 - T_WALL, hx1 + T_WALL, hy0 - T_WALL, hy1 + T_WALL
    cols = [(hx0 + COL_IN_B, hy0 + COL_IN_B), (hx1 - COL_IN_B, hy0 + COL_IN_B), (hx0 + COL_IN_B, hy1 - COL_IN_B),
            (hx1 - COL_IN_B, hy1 - COL_IN_B)]
    thru = cols                                          # all four on the board, through it
    ax, ay = (xo0 + xo1) / 2, yo1 + 0.3 + 12.0           # the VoiceS3R 0.3 past the hood (as B)
    ye = ay + 12.0                                       # its USB-C face is the box's +y end
    CH = 3.0                                             # the board's corners chamfered inside the floor's R3
    brd = (xo0, xo1, yo0, ye)
    edge = [(xo0 + CH, yo0), (xo1 - CH, yo0), (xo1, yo0 + CH), (xo1, ye - CH), (xo1 - CH, ye), (xo0 + CH, ye),
            (xo0, ye - CH), (xo0, yo0 + CH)]
    pcb = cq.Workplane('XY').workplane(offset=ZB).polyline(edge).close().extrude(ZBT - ZB)
    j3 = on(j3x - 5.075, j3x + 5.075, j3y - 1.1, j3y + 2.6, 0, J3_MATED)    # J3 with the 4P plug in it (as B)
    plug9, runs = vein_cable(vein, vz0, Z_IN - 0.3, (j3x, j3y), J3_ROOM, along_y=True)
    colz = None
    for x, y in cols:
        c = box(x - COL_B - 0.3, x + COL_B + 0.3, y - COL_B - 0.3, y + COL_B + 0.3, -1, Z_IN)
        colz = c if colz is None else colz.union(c)
    cable = union(*[r.cut(colz) for r in runs])
    # J1 / J2 as A (turned half a turn, USB-C / PORT.A to +y): J1 (5 pins) at x = ax - 7.62 from y = ay - 2.54, J2
    # (4 pins) at x = ax + 7.62 from y = ay, both to ay + 7.62
    hdr = on(ax - 8.89, ax - 6.35, ay - 3.81, ay + 8.89, 0, 2.5).union(on(ax + 6.35, ax + 8.89, ay - 1.27, ay + 8.89, 0, 2.5))
    hdr_pts = [(ax - 7.62, ay - 2.54 + 2.54 * i) for i in range(5)] + [(ax + 7.62, ay + 2.54 * i) for i in range(4)]
    tails = pins(hdr_pts, ZB - TAIL_HDR, ZB)    # under the board as measured
    tip_gap = tail_gap_hdr()
    # J3's mated plug and the wires' bend over it stay under the hood's top (its underside Z_IN)
    j3_gap = Z_IN - (ZBT + J3_MATED + J3_ROOM)
    assert j3_gap >= 0.5, f'J3\'s plug and the bend over it are {j3_gap:.2f} under the hood\'s top'
    atom_box = rbox(ax - 12, ax + 12, ay - 12, ay + 12, Z_ATOM_B, Z_ATOM_B + 16.8, 3.0) \
        .cut(cyl_z(ax, ay, 2.75, Z_ATOM_B - 1, Z_ATOM_B + ATOM_RECESS))    # the recess round its hole (STL)
    usb = box(ax - 6, ax + 6, ye + 6.5, ye + 24, Z_ATOM_B + 4, Z_ATOM_B + 11).union(
        box(ax - 4.2, ax + 4.2, ye, ye + 6.5, Z_ATOM_B + 6, Z_ATOM_B + 9))
    porta = box(ax - 4.9, ax + 4.9, ye, ye + 10.2, Z_ATOM_B, Z_ATOM_B + 4)
    vbox = vein_step_box((-(vy1 - vy0) / 2, (vy1 - vy0) / 2, -vw / 2, vw / 2), vz0).rotate((0, 0, 0), (0, 0, 1), 90) \
        .translate(((vein[0] + vein[1]) / 2, (vy0 + vy1) / 2, 0))      # the 9P end (the step box's -x) to -y
    bs = thru_bosses(thru)
    post, z_atom_hole = atom_post(ax, ay)
    # the body: the floor (R3 corners), the bosses, the VoiceS3R's post, floor ribs up to the board (clear of the THT
    # legs, the bosses and the post)
    body = rbox(*brd, -T_FLOOR_B, 0, 3.0).union(bs).union(post)
    av = [(a - 1.0, b + 1.0, c - 1.0, d + 1.0) for a, b, c, d in [xy_box(hdr)]] + \
        [(x - 3.5, x + 3.5, y - 3.5, y + 3.5) for x, y in thru] + \
        [(ax - ATOM_POST_R0 - 1.0, ax + ATOM_POST_R0 + 1.0, ay - ATOM_POST_R0 - 1.0, ay + ATOM_POST_R0 + 1.0)]
    g = rib_grid(brd[0] + 0.5, brd[1] - 0.5, brd[2] + 0.5, brd[3] - 0.5, -0.01, ZB, av)
    if g is not None:
        body = body.union(g)
    # the hood (B's): walls all round, all on the board
    walls = [(xo0, hx0, yo0, yo1, ZBT), (xo0, xo1, yo0, hy0, ZBT), (xo0, xo1, hy1, yo1, ZBT), (hx1, xo1, yo0, yo1, ZBT)]
    hood = hood_over_vein(vein, (xo0, xo1, yo0, yo1), (hx0, hx1, hy0, hy1), walls, cols, thru, Z_IN, Z_TOP)
    body = floor_screws(body, cols, ax, ay, z_atom_hole)
    pcb_v = pcb.cut(cyl_z(ax, ay, ATOM_CUT_R, ZB - 1, ZBT + 1))
    for x, y in thru:
        pcb_v = pcb_v.cut(cyl_z(x, y, 1.1, ZB - 1, ZBT + 1))
    parts = [('J3 + 4P plug', j3), ('9P plug', plug9), ('cable', cable), ('headers', hdr), ('header tails', tails),
             ('VoiceS3R', atom_box),
             ('USB plug', usb), ('PORT.A plug', porta), ('vein', vbox), ('board', pcb_v)]
    # the way in (as B): the board with its parts and the vein module, then the hood comes down past them
    down = [(xo0, hx0, yo0, yo1), (xo0, xo1, yo0, hy0), (xo0, xo1, hy1, yo1), (hx1, xo1, yo0, yo1)] + \
        [(x - COL_B, x + COL_B, y - COL_B, y + COL_B) for x, y in cols]
    for name, o in parts:
        if name in ('USB plug', 'PORT.A plug', 'cable', '9P plug', 'board'):
            continue
        assert not any(xy_overlap(xy_box(o), r) for r in down), f'{name} is under the walls / columns of the hood'
    assert not xy_overlap(xy_box(atom_box), (xo0, xo1, yo0, yo1)), 'the VoiceS3R under the top of the hood'
    bad = check((body.cut(bs), hood), parts)
    v = body.intersect(hood).val().Volume()
    if v > 0.01:
        bad.append(f'body/hood {v:.2f}')
    size = (xo1 - xo0, ye - yo0, Z_ATOM_B + 16.8 + T_FLOOR_B)
    screws = cols + [(ax, ay)]
    vp = vein_parts(vein, vz0, along_y=True, step=True)
    print(f'c: J3 + plug + bend {J3_MATED + J3_ROOM:g} over the board, {j3_gap:.2f} under the hood\'s top; J1 / J2\'s tails '
          f'({TAIL_HDR:g}, measured) end {tip_gap:.2f} over the floor\'s top (keep {TAIL_GAP_MIN:g})')
    view = [('shell', f'フード(B と同じ作り。指静脈の窓と裏の座ぐり、4 面の壁(一周の枠、どれも基板の上に立つ)と四隅の柱。床の裏から M2 × {SCREW_B:g} の皿小ねじ 4 本で、基板を挟んで締める)', '#2b2f33', 0.45, 'shell', hood),
            ('atom', f'VoiceS3R(公式 CAD、+y の端。USB-C は +y の端面で、まわりに壁もふたも無い。基板から 3.5 浮き、床の裏から段付きの柱を通した M2 × {SCREW_B:g} の皿小ねじで底の中心の穴に留める)', '#1fa49a', 1, 'mods', atom_at(ax, ay, 'y+', Z_ATOM_B, Z_TOP)),
            ('hdr', 'ピンヘッダー J1 / J2(樹脂の台 2.5 とピン。VoiceS3R の底は基板から 3.5 で、ピンが底に当たる)', '#202326', 1, 'mods',
             hdr.union(pins(hdr_pts, ZB - TAIL_HDR, Z_ATOM_B)))] + vp + [
        ('pcb', 'station 基板 print_c(build_board.py print_c。部品は J1 / J2 / J3 だけ。指静脈の下は平らで、パッドと配線だけ。基板だけのねじは無く、フードの 4 本の柱のねじで床のボスとの間に挟まり、VoiceS3R の柱の肩とピンの間に挟まる)', '#1f7a4d', 1, 'mods', pcb_v),
        ('j3', 'J3 MX1.25 4P 縦型(53398-0471)と 4P プラグ(指静脈の 9P プラグのすぐ手前、上から挿す)。ロックの窓(シルクの △ LOCK)は −y(外向き)。−x から 3V3・GND・RXD・TXD', '#f1efe8', 1, 'mods', j3),
        ('plug9', f'指静脈の 9P プラグと −y の端を回る線(端面から {CABLE_END:g}。窓を上にして −y から見て左が 1 番、3〜6 = 赤・黒・緑・黄)', '#e7e1cf', 1, 'mods', plug9),
        ('cable', f'9P → 4P のケーブル(自作、両端のロックが同じ面でまっすぐ)の置き場: 余りは指静脈の両側面に厚さ {CABLE_SIDE:g} で折り返し、底の溝も使える。−y の端の −x の角を回って J3 の上へ、上から挿す。巻き方は実物で合わせる', '#d9775c', 1, 'mods', cable),
        ('usb', 'USB-C / PORT.A プラグ(+y の端面)', '#24292d', 1, 'mods', usb.union(porta)),
        ('lid', '本体(床・ボス・VoiceS3R の段付きの柱・リブ、MJF PA12 で造形)', '#8fa09c', 0.9, 'lid', body)]
    return view, bad, size, body, hood, screws, Z_TOP


VEIN_NOTE = {'a': 'ふたは DB9 の上を切り欠いて(DB9 とプラグのフードはふたより上に出る)、中のケーブルの余りの上まで下げた。'
                  f'指静脈はふたから {VEIN_Z0 + 15.0 - (Z_IN_A + T_TOP):.1f} 出る。本体と一体の柱 4 本(基板の穴を通す)に VHB で載せる',
             'b': f'指静脈は 9P の端(ケーブル)を手前に向け、指静脈 Unit P と同じく基板にじかに載せてフードで押さえる(段差受け)。指静脈の下は平らで、基板にはパッドと配線だけ(床のリブが基板を受け、指で押す力もそこで受ける)。'
                  f'上の段(57 × 25、高さ 2.0)がフードの窓 57.5 × 25.5 を通り、下の胴(59 × 26)がフードの裏の座ぐり(深さ {VEIN_RECESS:g}、59.4 × 26.4)に当たって、'
                  f'上面はフードから {ZBT + 15.0 - (Z_IN_B + T_TOP):.1f} 出る(図の上。フードは指静脈を載せた積み上げより {HOOD_UP_B:g} 高い)。フードは指静脈の部分だけで、4 面の壁(一周の枠)と四隅の角柱を持ち、'
                  f'壁も柱もすべて基板の上に立つ。床の裏から M2 × {SCREW_B:g} の皿小ねじ 4 本が床のボスと基板を通って柱に入り、床・基板・フードを一度に締める(上面にねじ頭なし)(v0.55。v0.50〜v0.54 は基板の下からで、床を先に付けると締められなかった)。'
                  'J3 は縦型(53398-0471)で 9P プラグのすぐ手前に立ち、ロックの窓は手前(外向き)。'
                  f'ケーブルは自作(両端のロックが同じ面でまっすぐ、9P の 3〜6 → 4P の −x から順)で、J3 に上から挿す。余り(約 7 cm)は指静脈 Unit P と同じく指静脈の両側面(フードの ±x の壁との間)に厚さ {CABLE_SIDE:g} で折り返す(底の溝も使える。巻き方は実物で合わせる)。そのために指静脈と左の部分を −x へ寄せ、+x の壁は動かしていない。フードと基板の左の部分は J3 の上まで手前へ伸ばした(右の列の手前の面は変えない)。'
                  '右の列は手前から J6(Grove、手前の縁、口は手前。v0.56 から基板を四角にして、縁はフードの手前の面と同じ)→ DB9(口は右)→ VoiceS3R(奥の端、USB-C は奥の面、リセットは右の面。どちらも箱の外面にそろう)で(v0.46)、壁もふたも無く、基板と床だけ。'
                  f'J6 の本体の後ろ端と DB9 の枠の間は {J6_DB9_B:g}(J6 のパッドとコートヤードが DB9 のコートヤードに重ならない)。'
                  f'DB9 の口の筒の先端は基板の右の縁(VoiceS3R のリセットの面と同じ)にそろえ、筒の下の基板と床は切り抜く。挿したシリアルケーブルのプラグ(実測で最大幅 {2 * DB9_PLUG_W:g}、厚み 14.6)は筒の先端で止まるので基板の外に出て、VoiceS3R にも J6 のプラグにも当たらない(DB9 の枠と VoiceS3R の手前の面の間は {DB9_GAP_B:g})。'
                  f'MAX3232・C1〜C5・R1 / R2・SW1 は VoiceS3R の真下(部品は基板から {H_MAX_B:.1f} 以下。SW1 は KINGTEK DSHP04TSGET、高さ最大 {SW1_H:g}、VoiceS3R を外して切り替える)。'
                  f'VoiceS3R は基板から 3.5 浮き(実測、ピンが底に当たる)、基板の M2 の穴 H9(ほかの M2 の穴と同じパッド付き、v0.55。v0.50〜v0.54 は ⌀4.8 の切り欠きとワッシャー)を通した M2 × {SCREW_PAN_B:g} のなべ小ねじで底の中心の M2 穴に留める'
                  f'(穴に {ZB + SCREW_PAN_B - Z_ATOM_B - ATOM_RECESS:.1f} 入る。柱は無い: v0.49 までの床からの柱は実物で長く、VoiceS3R が浮いた)。'
                  f'NFC(v0.56): フードに右の列の手前を DB9 の手前から基板の縁まで覆う棚(厚さ {T_TOP:g}、上面はフードの天板の裏の高さで DB9 の上面から {Z_IN_B - DB9_TOP:.1f} 上)を付け、J6 の +x 側で箱の +x の面に沿った壁(x {NFC_LEGS[0][0] - COL_B:.1f} から箱の +x の面まで、v0.57。v0.56 は 3.6 角の足 3 本)で基板に立て、壁の中の 3 か所(基板の H10 / H5 / H11)を床の裏から M2 × {SCREW_B:g} の皿小ねじで締める。'
                  f'Unit NFC(48 × 24 × 8)は棚に載せて Grove の端を手前の面にそろえ、棚の柱 ⌀{NFC_POST_D:g} 2 本を NFC の穴 ⌀{NFC_HOLE_D:g} に通して、上から M2 × {SCREW_NFC_B:g} のなべ小ねじとワッシャー(外径 {NFC_WASHER_D:g} × {NFC_WASHER_T:g})で留める(柱に {SCREW_NFC_B - NFC_WASHER_T - 0.3:.1f} 入る)。後ろの 3/4 は DB9 の上に出るので、棚の上に NFC の足元全体の台を足し、NFC の裏を DB9 の上面から {NFC_OFF_DB9:g} 離す(v0.59。v0.58 までは 0.3 で、DB9 の金属でカードを読まなかった)。DB9 の上の部分も、DB9 の上面から 0.3 まで台で埋め、NFC の奥の -x 側の角の下に基板から台まで柱を立てる(v0.60)。NFC の上面は VoiceS3R の上面より {DB9_TOP + NFC_OFF_DB9 + NFC_H - (Z_ATOM_B + 16.8):.1f} 高い'}
VEIN_NOTE['c'] = (
    'B と同じく、指静脈は 9P の端(ケーブル)を −y に向け、基板にじかに載せてフードで押さえる(段差受け)。指静脈の下は平らで、基板にはパッドと配線だけ(床のリブが基板を受ける)。'
    f'上面はフードから {ZBT + 15.0 - (Z_IN_B + T_TOP):.1f} 出る。フードは B と同じ作り(4 面の壁と四隅の角柱、窓 57.5 × 25.5 + 座ぐり {VEIN_RECESS:g})で、壁も柱もすべて基板の上に立ち、'
    f'床の裏から M2 × {SCREW_B:g} の皿小ねじ 4 本が床のボスと基板を通って柱に入り、基板もフードと床の間に挟む。'
    'J3 は縦型(53398-0471)で 9P プラグのすぐ手前(−y)に立ち、ロックの窓は −y(外向き)。'
    f'ケーブルは B / 指静脈 Unit P と同じ自作(両端のロックが同じ面でまっすぐ、9P の 3〜6 → 4P の −x から順)で、J3 に上から挿す。余り(約 7 cm)は指静脈の両側面(フードの ±x の壁との間)に厚さ {CABLE_SIDE:g} で折り返す(底の溝も使える)。'
    'DB9 を外したので、MAX3232・C1〜C5・R1 / R2・SW1・J6(Grove)も無い。NFC なし(RS232 の要らない所向け)。'
    f'VoiceS3R は +y の端で、USB-C は +y の端面。まわりに壁もふたも無く(基板と床だけ)、基板から 3.5 浮き(実測)、床から立てた段付きの柱(⌀{2 * ATOM_POST_R0:g} の肩が基板を受け、⌀{2 * ATOM_POST_R:g} が基板の丸い切り欠き ⌀{2 * ATOM_CUT_R:g} を通る)を通した '
    f'M2 × {SCREW_B:g} の皿小ねじで底の中心の M2 穴に留める(穴に {-T_FLOOR_B + SCREW_B - Z_ATOM_B - ATOM_RECESS:.1f} 入る)')
RIB_SHOWN = {'a': RIB_FLOOR, 'b': ZB, 'c': ZB}   # the floor ribs' height in the table (B: up to the board)
out = os.path.join(ROOT, 'station')
failed = []
for key, fn, title in (('a', concept_a, 'A 一列(薄型)'), ('b', concept_b, 'B 2 列(短い)'), ('c', concept_c, 'C 一列(DB9 なし)')):
    view, bad, size, tray, lid, screws, z_top = fn()
    vol = (tray.val().Volume() + lid.val().Volume()) / 1000
    print(key, 'outer %.1f x %.1f x %.1f' % size, 'volume %.1f cm3' % vol, 'screws', [(round(x, 1), round(y, 1)) for x, y in screws],
          'interference:', bad or 'none')
    if len(screws) < 3:
        failed.append(f'{key}: only {len(screws)} places for the lid screws')
    failed += [f'{key}: {b}' for b in bad]
    stls = []
    for n, s, label in (('body', tray, '本体'), ('lid', lid, 'ふた')):
        p = os.path.join(out, f'vein_station_print_{key}_v{VER}_{n}.stl')
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
    if key == 'b':        # B: a floor and a hood, no walls round the right column, no lid ribs, screwed from below
        dims[0] = ('外形', '%.1f × %.1f × %.1f(幅 × 奥行 × 高さ、VoiceS3R の上面まで。フードは %.1f)' % (size + (z_top + T_FLOOR_B,)))
        dims[1] = ('体積', '%.1f cm³(本体 + フード)' % vol)
        dims[2] = ('肉厚', f'床 {T_FLOOR_B}、フードの壁 {T_WALL}・天板 {T_TOP}(MJF PA12)')
        dims[3] = ('リブ', f'反り止め(JLC3DP の勧め)。幅 {RIB_W:g} を約 {RIB_PITCH:g} おきの格子に、床(高さ {RIB_SHOWN[key]:g}、基板の下。THT の足とボスを避ける)')
        dims[4] = ('基板', 'station 基板 print_b(箱に合わせて配置・配線済み、build_board.py print_b)。フードの下全体(フードの外面まで)と右の列。フードの 4 本のねじ(床の裏から)が基板を床のボスとの間に挟み、VoiceS3R は基板の下からねじで留め、'
                           '棚の壁の 3 本のねじ(H10 / H5 / H11)も基板を床のボスとの間に挟む。基板はほかに右の列の DB9 の +x 側の 1 か所(H8)で床に留める(床の裏から皿小ねじ、基板の上にナット)。フードの手前・奥の真ん中(H6 / H7)は v0.57 からフードの柱へ通す(v0.52〜v0.56 はナットとフードの六角の逃げ)。v0.56 から基板は四角(右の列の手前の縁をフードの手前の面まで出した)。指静脈の下は床のリブが受ける。'
                           f'基板の縁ぐるりに、床の上面から基板の裏まで届く受け(幅 {EDGE_W:g}、縁から {EDGE_IN:g} 内側)を入れる。床のリブと同じものを 1.0 離して避け、フードの壁が基板を挟む所・フードの柱・床の R3 の角(手前 3.0 で止める)には入れない。'
                           f'J1 / J2 の足は実測 {TAIL_HDR:g}(床の上面から {ZB - TAIL_HDR:.1f} 上で止まり、床に当たらない)。DB9 の固定の足 2 本は実測 {TAIL_DB9:g}で床に {TAIL_DB9 - ZB:.1f} 食い込むので、その真下の床に ⌀{DB9_HOLE_D:g} の丸い貫通穴を 1 つずつ開ける。信号の足 9 本は実測で 2.0 より短く床に当たらないので穴は無い(干渉チェックでは目安の {TAIL_DB9_SIG:g})(固定の足の先は机から {T_FLOOR_B + ZB - TAIL_DB9:.1f})')
        dims[6] = ('ねじ', f'M2 × {SCREW_B:g} 皿小ねじ × 9(フードの柱 6・棚の壁 3、床の裏から床のボスと基板を通って下穴へ)、M2 × {SCREW_PAN_B:g} なべ小ねじ × 1(VoiceS3R、基板の M2 の穴 H9 から)、'
                           f'M2 × {SCREW_NFC_B:g} なべ小ねじ + ワッシャー(外径 {NFC_WASHER_D:g})× 2(NFC、上から棚の柱へ)、'
                           f'M2 × {SCREW_FLOOR_B:g} 皿小ねじ + M2 ナット × 1(床と基板。右の列の DB9 の +x 側。床の裏から上へ、頭は床と面一、ナットは基板の上)。'
                           f'フードの四隅の角柱(3.6 角)の下穴 ⌀{PILOT_B:g} に PA12 をねじ切りながら締める(C と同じ)。VoiceS3R のねじは締めすぎない。位置: '
                           + ', '.join(f'({x:.1f}, {y:.1f})' for x, y in screws))
    if key == 'c':        # C: B's hood and floor, the VoiceS3R at the +y end with no walls round it
        dims[0] = ('外形', '%.1f × %.1f × %.1f(幅 × 奥行 × 高さ、VoiceS3R の上面まで。フードは %.1f)' % (size + (z_top + T_FLOOR_B,)))
        dims[1] = ('体積', '%.1f cm³(本体 + フード)' % vol)
        dims[2] = ('肉厚', f'床 {T_FLOOR_B}、フードの壁 {T_WALL}・天板 {T_TOP}(MJF PA12)')
        dims[3] = ('リブ', f'反り止め(JLC3DP の勧め)。幅 {RIB_W:g} を約 {RIB_PITCH:g} おきの格子に、床(高さ {RIB_SHOWN[key]:g}、基板の下。THT の足とボスを避ける)')
        dims[4] = ('基板', 'station 基板 print_c(箱に合わせて配置・配線済み、build_board.py print_c。部品は J1 / J2 / J3 だけ)。基板だけを留めるねじは無い: フードの 4 本の柱のねじ(床のボスとの間に挟む)と VoiceS3R の段付きの柱の肩。'
                           f'指静脈の下は床のリブが受けて指静脈に押さえられ、横はフードの壁で決まる。J1 / J2 の足は実測 {TAIL_HDR:g}(床の上面から {ZB - TAIL_HDR:.1f} 上で止まり、床に当たらない)')
        dims[6] = ('ねじ', f'M2 × {SCREW_B:g} 皿小ねじ × {len(screws)}(フード 4、VoiceS3R 1)。どれも床の裏から上へ、頭は床と面一。'
                           f'フードの四隅の角柱(3.6 角)は下穴 ⌀{PILOT_B:g} に PA12 をねじ切りながら締める(4 本とも基板を通す)。'
                           'VoiceS3R のねじは締めすぎない(基板は柱の肩とピンの間に挟まるだけ)。位置: '
                           + ', '.join(f'({x:.1f}, {y:.1f})' for x, y in screws))
    bom = (f'ねじの部品表: M2 × {SCREW_B:g} 皿小ねじ × 9(フード 6、棚 3)、M2 × {SCREW_PAN_B:g} なべ小ねじ × 1(VoiceS3R)、M2 × {SCREW_FLOOR_B:g} 皿小ねじ × 1、M2 ナット × 1、M2 × {SCREW_NFC_B:g} なべ小ねじ × 2 とワッシャー(外径 {NFC_WASHER_D:g})× 2(NFC)。'
           '組み立て: SW1 を 1+2 ON にして、VoiceS3R を J1 / J2 に挿し、基板の下からねじで留める(締めすぎない)。指静脈を基板に載せてケーブルを J3 に上から挿し、余りを指静脈の両側面に折り返して、'
           'フードをかぶせて床に載せる。床の裏から皿小ねじ 10 本を一度に締める: M2 × {SCREW_B:g} の 9 本はフードの柱と棚の壁へ(基板も挟まる)、M2 × {SCREW_FLOOR_B:g} の 1 本は基板の上のナットへ(ナットは手で押さえる)。'
           'NFC を棚に載せて(Grove の端を手前に)柱を穴に通し、上からワッシャーを入れたねじ 2 本で留め、ケーブルを手前で折り返して J6 に挿す。') if key == 'b' else \
        (f'ねじの部品表: M2 × {SCREW_B:g} 皿小ねじ × 5(フード 4、VoiceS3R 1)。組み立て: 基板を床に落とし込み(VoiceS3R の柱の肩に載る)、VoiceS3R を J1 / J2 に挿して床の裏からねじで留める。'
         '指静脈を基板に載せてケーブルを J3 に上から挿し、余りを指静脈の両側面に折り返して、フードをかぶせ、床の裏から 4 本で締める(基板も挟まる)。VoiceS3R のねじは締めすぎない。') if key == 'c' else ''
    write_page(f'station-print-{key}', f'案 {title}', view,
               f'Vein Station を 3D 印刷の箱にする試作案 {title}。基板も作り直す前提で、部品の置き場所だけを決めた形。'
               + bom + 'ドラッグで回転、ホイール/ピンチで拡大。', dims,
               '試作の形(配置だけ)。基板は未配線、部品は KiCad のフットプリント寸法からの簡略形状。VoiceS3R は M5Stack 公式 STL'
               '(m5stack/M5_Hardware、MIT License)。単位 mm。', z_top, stls)
if failed:
    raise SystemExit('interference: ' + ', '.join(failed))
