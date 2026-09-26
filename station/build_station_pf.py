"""Vein Station PF: the station in an off-the-shelf Takachi PF13-4-9 (125 × 40 × 85, ABS, front/back panels, ¥710)
instead of a printed enclosure. Nothing is printed: the station board r12 (pcb/station_board, `build_board.py pf`)
stands on the case's own PCB bosses (Takachi TPS-M2.3-7 tapping spacers), and the modules stand on stock M3
male-female spacers on the board. The only machining is the two top plate windows (cut by hand on the prototypes).
Run from the repository root:  python3 station/build_station_pf.py
Writes the hole drawing for Takachi's machining service (station/vein_station_pf<N>_top.dxf), a 1:1 paper
template for cutting the same windows by hand (station/vein_station_pf<N>_top_template_1to1.pdf, A4) and the
3D preview site/station-pf/index.html, and fails if the case collides with a module, plug, spacer or the board, or
two of those collide with each other.

Case coordinates (Takachi's): x across the 125 side, y across the 85 side, the back panel is on -y, z = 0 at the
base's seat; floor top -1.5, top plate underside 33 (3.0 thick). Nobody may redistribute Takachi's STP, so the case
here is a simplified model written from numbers measured on it (PF13-4-9 D.stp, takachi-el.co.jp, 2026-09):
  inside 117 × 79 × 34.5; side walls |x| >= 58.4; panels 2.0 thick, inside face y = ±(40.45 - 0.035 (z - 2)),
  top lip |y| >= 38.8 above z 30.4 (28.3 at |x| >= 37), panel guides inside the panels (|x| >= 41.9 at |y| 38..39.4, >= 41.0 at 39..39.4); floor marks 0.2 high;
  top plate underside 33 in the middle, down to 32.3 at |y| 29..37.4, 32.0 over the
  panel grooves (|y| >= 37.4) and 29 at their ends (|x| >= 37); 32.9 / 32.3 at |x| >= 44 / 51;
  corner screw bosses (±51, ±31) with ribs (|x| >= 46.3 and |y| >= 26.3, full height);
  PCB bosses 87 × 47 (±43.5, ±23.5), r 2.4: on the floor up to z 3.5, from the top plate down to z 28.
The model is conservative (it holds the STP's material in the space the parts use); checked against the STP locally.
The preview shows the VoiceS3R and the Unit NFC from M5Stack's official STL (station/m5_cad.py); the checks use their
outline boxes.

Stack (z): floor PCB bosses (top 3.5) | Takachi TPS-M2.3-7 tapping spacers (hex 5, 7 long, M2.3 tapping stud 4 into
the boss, M2.3 female 5 deep) | board 10.5..12.1, M2.3 × 5 pan head screws on top | VoiceS3R 14.6..31.4 on the Ext.Pin
(0.6 under the panel-groove ledge; its button is not used) | vein module on 12 mm spacers and 1.0 VHB tape, 25.1..40.1:
it stands 4.1 proud of the top plate through a window of its outline + 0.2, so the 3 mm plate holds its top sideways
and the tape on the four spacer tops holds its bottom (without the tape it could tilt about the 3 mm window band and
lift out; its flange size is not needed; its bottom must be 8.9 + proud above the board, and J3 and its plug sit
under it) | Unit NFC on 12 mm spacers, 24.1..32.1, stuck to the top plate's underside with foam tape (gap 0.2..0.9), no
window: it reads through the 3 mm ABS (flush in a window would put its Grove plug into the top plate).
The module spacers are stock M3 male-female, male end down through the board with a nut under it (H1..H8).
The board is 92 wide (case x -46..46) to reach the bosses and stay clear of the corner screw bosses (|x| >= 46.3).
Layout: back row VoiceS3R + DB9 on the board (the DB9 posts are 0.1 from the panel guides, the row cannot move right);
the NFC at the front left (its Grove plug inside, the cable leaves through the open back to PORT.A outside), right of
the left PCB bosses; the vein module on the right, behind the right front PCB boss (both bosses stay).
The back panel is left off: every connection is on that side, so there is nothing to machine there (no D-sub cutout,
no counterbore). The DB9 plug's push goes into the board and the bosses instead of the panel.
"""
import os
import numpy as np
import ezdxf
from shapes import box, rbox, cyl_z, cyl_y, sym, quad, stl_at, vein_parts, write_page
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REV = 'pf9'

# ---- case (simplified from the measured STP) ---------------------------------------------------------------
FLOOR, CEIL, TOP = -1.5, 33.0, 36.0
PANEL_X = 44.52                                   # panel half width
PANEL_IN = 39.4                                   # conservative inside face of the panels (|y|)
PANEL_OUT = 42.45                                 # outside face at the bottom (it leans in by 0.035 / mm)
cover = rbox(-62.5, 62.5, -42.5, 42.5, 0.5, TOP, 17.0)
cover = cover.cut(box(-58.4, 58.4, -PANEL_IN, PANEL_IN, 0, CEIL))
cover = cover.cut(box(-PANEL_X, PANEL_X, -43, 43, 0, CEIL))            # the panels' openings
cover = (cover.union(quad(0, 58.4, 29.0, 42.5, 32.3, CEIL)).union(quad(0, 58.4, 37.4, 42.5, 32.0, CEIL))
         .union(quad(0, 58.4, 38.8, 42.5, 30.4, CEIL)).union(quad(37.0, 58.4, 37.4, 42.5, 28.3, CEIL))  # panel lips
         .union(quad(41.9, 58.4, 38.0, 39.4, FLOOR, CEIL)).union(quad(41.0, 58.4, 39.0, 39.4, FLOOR, CEIL))
         .union(quad(40.1, 58.4, 38.9, 39.4, 26.2, CEIL))                                   # panel guides
         .union(quad(44.0, 58.4, 0, 42.5, 32.85, CEIL))
         .union(quad(51.0, 58.4, 0, 42.5, 32.3, CEIL))
         .union(quad(46.3, 58.4, 26.3, 42.5, FLOOR, CEIL))                               # corner bosses + ribs
         .union(sym(lambda sx, sy: cyl_z(sx * 43.5, sy * 23.5, 2.4, 28.0, CEIL))))         # PCB bosses, top
base = (rbox(-62.5, 62.5, -42.5, 42.5, -4.0, FLOOR, 17.0).union(sym(lambda sx, sy: cyl_z(sx * 43.5, sy * 23.5, 2.4, FLOOR, 3.5)))
        .union(box(12.4, 29.7, -24.9, -20.0, FLOOR, FLOOR + 0.2)).union(box(14.0, 28.1, 23.3, 25.6, FLOOR, FLOOR + 0.2))
        .union(box(15.3, 27.2, 17.5, 20.1, FLOOR, FLOOR + 0.2)))                                   # moulded marks
panel = box(-PANEL_X, PANEL_X, -PANEL_OUT, -PANEL_IN, -0.5, CEIL).union(box(-PANEL_X, PANEL_X, -PANEL_IN, -38.7, 32.4, CEIL))
front_panel = panel.mirror('XZ')                 # the back panel (on -y) is left off

# ---- board r12 (pf outline) and its parts (board coords of pcb/station_board: x_case = VXP - bx, y_case = VYP + by) --------
VXP, VYP = -6.0, -26.7         # VoiceS3R centre = board origin
BOSS_TOP, TPS = 3.5, 7.0       # the case's PCB bosses, Takachi TPS-M2.3-7
ZB = BOSS_TOP + TPS            # board bottom 10.5
ZBT = ZB + 1.6
Z_ATOM = ZBT + 2.5             # VoiceS3R bottom (header plastic 2.5)
BX0, BX1, BY0, BY1 = -52.0, 40.0, -11.0, 60.0     # pf outline (build_board.py pf)
# H1..H8 (M3, module spacers) and B1..B4 (M2.3 over the case's PCB bosses) in board coords, the same lists as
# build_board.py (keep them together)
HOLES = [(27.0, 17.5), (14.9, 17.5), (27.0, 55.5), (14.9, 55.5), (5.2, 27.5), (-43.8, 27.5), (5.2, 42.5),
         (-43.8, 42.5)]
BOSSES = [(37.5, 3.2), (-49.5, 3.2), (37.5, 50.2), (-49.5, 50.2)]
NFC_H, VEIN_H = (1, 2, 3, 4), (5, 6, 7, 8)
MALE, NUT = 6.0, 2.4                                  # male thread length of the spacers, M3 nut height
SP_NFC, SP_VEIN = 12.0, 12.0

def at(bx, by):
    return VXP - bx, VYP + by


def board(bx0, bx1, by0, by1, z0, z1):
    """Box in board coords (z from the VoiceS3R bottom face) -> case coords."""
    return box(VXP - bx1, VXP - bx0, VYP + by0, VYP + by1, Z_ATOM + z0, Z_ATOM + z1)


pcb = board(BX0, BX1, BY0, BY1, -4.1, -2.5)
for bx, by in HOLES:
    x, y = at(bx, by)
    pcb = pcb.cut(cyl_z(x, y, 1.6, ZB - 1, ZBT + 1))
for bx, by in BOSSES:
    x, y = at(bx, by)
    pcb = pcb.cut(cyl_z(x, y, 1.3, ZB - 1, ZBT + 1))
hdr_plastic = hdr_pins = None
for bx, bys in ((7.62, (2.54, 0, -2.54, -5.08, -7.62)), (-7.62, (0, -2.54, -5.08, -7.62))):
    for by in bys:
        pl = board(bx - 1.27, bx + 1.27, by - 1.27, by + 1.27, -2.5, 0)
        pn = board(bx - 0.32, bx + 0.32, by - 0.32, by + 0.32, -7.1, -2.5)
        hdr_plastic = pl if hdr_plastic is None else hdr_plastic.union(pl)
        hdr_pins = pn if hdr_pins is None else hdr_pins.union(pn)
j3 = board(-35.0, -25.0, 17.2, 24.0, -2.5, 0.9)
j3_plug = board(-33.0, -27.0, 24.0, 30.0, -2.2, 0.6)
u1 = board(-31.0, -21.0, 3.05, 6.95, -2.5, -0.75)
caps = board(-31.3, -19.2, 10.3, 11.7, -2.5, -1.6).union(board(-19.2, -17.8, 3.6, 6.4, -2.5, -1.6))
sw1 = board(-46.9, -35.5, 0.1, 12.5, -2.5, -0.5)
DB9_BX = -27.9                  # r12 board: 4.0 closer to the VoiceS3R (r10: -31.9)
db9_body = board(DB9_BX - 15.0, DB9_BX + 15.0, BY0 + 0.5, BY0 + 10.5, -2.5, 10.0)
db9_flange = board(DB9_BX - 15.4, DB9_BX + 15.4, BY0 - 1.0, BY0, -2.5, 10.0)
db9_shell = board(DB9_BX - 8.5, DB9_BX + 8.5, BY0 - 7.0, BY0 - 1.0, -0.5, 8.0)
tails = board(DB9_BX - 6.5, DB9_BX + 6.5, BY0 + 3.0, BY0 + 8.5, -7.1, -4.1)
DB9_XC, DB9_ZC = VXP - DB9_BX, Z_ATOM + 3.75
db9_posts = (cyl_y(DB9_XC - 12.5, VYP + BY0 - 5.0, VYP + BY0 - 1.0, DB9_ZC, 2.5)
             .union(cyl_y(DB9_XC + 12.5, VYP + BY0 - 5.0, VYP + BY0 - 1.0, DB9_ZC, 2.5)))

# ---- modules (official outlines; see build_station.py) ----------------------------------------------------
VOICE = (VXP - 12, VXP + 12, VYP - 12, VYP + 12)                  # back face y -38.7, 0.1 off the panel's top lip
NFC = (-40.9, -16.9, -14.2, 33.8)                                  # 0.2 right of the left PCB bosses, Grove at the back
VEIN = (-15.2, 43.8, -5.2, 20.8)                                   # 0.3 behind the right front PCB boss
atom = rbox(*VOICE, Z_ATOM, Z_ATOM + 16.8, 3.0)
nfc = rbox(*NFC, ZBT + SP_NFC, ZBT + SP_NFC + 8.0, 1.5)
TAPE = 1.0                                                         # VHB double-sided tape on the four spacer tops
VEIN_Z0 = ZBT + SP_VEIN + TAPE                                     # 25.1: top 40.1, 4.1 proud of the top plate
vein = rbox(*VEIN, VEIN_Z0, VEIN_Z0 + 15.0, 2.0)
NX = (NFC[0] + NFC[1]) / 2

# spacers: M3 male-female, hex 5.5 across flats modelled as r 3.2 cylinders, male thread r 1.5, nut r 3.2 × 2.4,
# male end down through the board with the nut under it; TPS-M2.3-7: hex 5 (r 2.9) on the boss, M2.3 pan head r 2 × 1.6
spacers = None
for i, (bx, by) in enumerate(HOLES, 1):
    x, y = at(bx, by)
    top = ZBT + SP_NFC if i in NFC_H else VEIN_Z0 - TAPE
    for p in (cyl_z(x, y, 3.2, ZBT, top), cyl_z(x, y, 1.5, ZBT - MALE, ZBT), cyl_z(x, y, 3.2, ZB - NUT, ZB)):
        spacers = p if spacers is None else spacers.union(p)
for bx, by in BOSSES:
    x, y = at(bx, by)
    for p in (cyl_z(x, y, 2.9, BOSS_TOP, ZB), cyl_z(x, y, 2.0, ZBT, ZBT + 1.6)):
        spacers = spacers.union(p)
# the TPS must stand on the bosses the case model has (±43.5, ±23.5)
for bx, by in BOSSES:
    x, y = at(bx, by)
    assert abs(abs(x) - 43.5) < 0.01 and abs(abs(y) - 23.5) < 0.01, (bx, by, x, y)

# a spacer or nut on one side of the board and a spacer, nut or male end of the next hole must not meet: hex 5.5 across
# flats is 6.35 across corners, so the holes stay >= 6.4 apart
ALL = HOLES + BOSSES
for i, (p0, q0) in enumerate(ALL, 1):
    for j, (p1, q1) in enumerate(ALL[i:], i + 1):
        if ((p0 - p1) ** 2 + (q0 - q1) ** 2) ** 0.5 < 6.4:
            raise SystemExit(f'holes {i} and {j} (H1..H8, then B1..B4) are closer than 6.4')

# plugs at the open back (the PORT.A <-> NFC Grove cable loops outside, as in build_station.py)
YB = VOICE[2]
usb_plug = box(VXP - 6, VXP + 6, YB - 24.2, YB - 6.5, Z_ATOM + 4.0, Z_ATOM + 11.0).union(
    box(VXP - 4.2, VXP + 4.2, YB - 6.5, YB, Z_ATOM + 6.0, Z_ATOM + 9.0))
porta_plug = box(VXP - 4.9, VXP + 4.9, YB - 10.2, YB, Z_ATOM + 0.0, Z_ATOM + 4.0)
NFC_TOP = ZBT + SP_NFC + 8.0
nfc_plug = box(NX - 4.0, NX + 4.0, NFC[2] - 8.2, NFC[2], NFC_TOP - 5.2, NFC_TOP - 0.4)   # inside the case
DB9_X0, DB9_X1 = DB9_XC - 15.4, DB9_XC + 15.4
DB9_Z0, DB9_Z1 = Z_ATOM - 3.5, Z_ATOM + 11.0
# the plug stops 0.8 short of the flange, outside the panel guides (it still takes 5.2 of the 6 mm D shell)
db9_plug = box(DB9_X0 + 0.25, DB9_X1 - 0.25, -80, -PANEL_IN - 0.1, DB9_Z0 + 0.25, DB9_Z1 - 0.25)

# ---- machining (what Takachi cuts) -------------------------------------------------------------------------
# top plate: vein window of its outline + 0.2 (it stands through), VoiceS3R window with a 1.2 lip; no NFC window
VEIN_WIN = (VEIN[0] - 0.2, VEIN[1] + 0.2, VEIN[2] - 0.2, VEIN[3] + 0.2, 2.2)   # the module passes through
VOICE_WIN = (VOICE[0] + 1.2, VOICE[1] - 1.2, VOICE[2] + 1.2, VOICE[3] - 1.2, 1.8)
cover = cover.cut(rbox(*VEIN_WIN[:4], CEIL - 1, TOP + 1, VEIN_WIN[4]))
cover = cover.cut(rbox(*VOICE_WIN[:4], CEIL - 1, TOP + 1, VOICE_WIN[4]))

# ---- interference ----------------------------------------------------------------------------------------
case = cover.union(base).union(front_panel)
checks = [('VoiceS3R', atom), ('指静脈', vein), ('NFC', nfc), ('board', pcb), ('header plastic', hdr_plastic),
          ('header pins', hdr_pins), ('J3', j3), ('J3 plug', j3_plug), ('MAX3232', u1), ('caps', caps), ('DIP', sw1),
          ('DB9 body', db9_body), ('DB9 flange', db9_flange), ('DB9 shell', db9_shell), ('DB9 posts', db9_posts),
          ('DB9 tails', tails), ('spacers', spacers), ('USB plug', usb_plug), ('PORT.A Grove', porta_plug),
          ('NFC Grove', nfc_plug), ('DB9 plug', db9_plug)]
bad = []
for name, obj in checks:
    v = case.intersect(obj).val().Volume()
    print(f'interference case x {name:14s} = {v:.3f} mm3')
    if v > 0.01:
        bad.append(f'case/{name}')
# the parts among themselves: the modules, the board's tall parts, the spacers and the plugs (a plug and the
# connector it goes into, and the board and what is soldered to it, are meant to touch)
mutual = [('VoiceS3R', atom), ('指静脈', vein), ('NFC', nfc), ('spacers', spacers), ('J3 plug', j3_plug), ('DIP', sw1),
          ('DB9 body', db9_body), ('USB plug', usb_plug), ('NFC Grove', nfc_plug), ('DB9 plug', db9_plug)]
for i, (na, a) in enumerate(mutual):
    for nb, b in mutual[i + 1:]:
        v = a.intersect(b).val().Volume()
        if v > 0.01:
            print(f'interference {na} x {nb} = {v:.3f} mm3')
            bad.append(f'{na}/{nb}')
print('parts among themselves: ' + ('ok' if not any('/' in b and not b.startswith('case/') for b in bad) else 'NG'))

# ---- hole drawings for Takachi (DXF, mm, one sheet per face) -----------------------------------------------
out = os.path.join(ROOT, 'station')


def rrect(msp, x0, x1, y0, y1, r, layer):
    """Rounded rectangle as one closed polyline (bulge 0.4142 = 90° arc)."""
    b = 0.41421356
    pts = [(x0 + r, y0, 0), (x1 - r, y0, b), (x1, y0 + r, 0), (x1, y1 - r, b), (x1 - r, y1, 0), (x0 + r, y1, b),
           (x0, y1 - r, 0), (x0, y0 + r, b)] if r else [(x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0)]
    msp.add_lwpolyline(pts, format='xyb', close=True, dxfattribs={'layer': layer})


def sheet(name, title, notes, draw, x0, y0):
    doc = ezdxf.new('R2010')
    for ly, col in (('OUTLINE', 8), ('CUT', 1), ('COUNTERBORE', 5), ('CSK', 3), ('NOTE', 7)):
        doc.layers.add(ly, color=col)
    msp = doc.modelspace()
    draw(msp)
    y = y0
    for t in [title] + notes:
        msp.add_text(t, height=2.0, dxfattribs={'layer': 'NOTE'}).set_placement((x0, y))
        y -= 3.5
    path = os.path.join(out, f'vein_station_{REV}_{name}.dxf')
    doc.saveas(path)
    print('wrote', path)
    return path


TOP_OUTLINE = (-62.5, 62.5, -42.5, 42.5, 17.0)   # the cover seen from above
TOP_WINS = [('vein', VEIN_WIN), ('VoiceS3R', VOICE_WIN)]


def draw_top(msp):
    # seen from above, origin = case centre (x across 125, y across 85, back panel at the bottom)
    rrect(msp, *TOP_OUTLINE, 'OUTLINE')
    for _, w in TOP_WINS:
        rrect(msp, *w, 'CUT')


def rrect_xy(x0, x1, y0, y1, r, n=16):
    """The same rounded rectangle as rrect(), as a closed point list for the PDF."""
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        a = np.radians(np.linspace(a0, a0 + 90, n + 1))
        pts += list(zip(cx + r * np.cos(a), cy + r * np.sin(a)))
    return np.array(pts + pts[:1])


def top_template(name):
    """A4 portrait, 1 mm on paper = 1 mm: the cover's outline and the two windows seen from above, to lay face up
    on the cover and cut the windows by hand. Same geometry as the DXF (draw_top)."""
    W, H = 210.0, 297.0
    fig = plt.figure(figsize=(W / 25.4, H / 25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(-W / 2, W / 2)
    ax.set_ylim(-190, H - 190)   # the case centre sits 107 below the top of the sheet
    ax.set_aspect('equal')
    ax.axis('off')
    x0c, x1c, y0c, y1c, _ = TOP_OUTLINE
    txt = lambda x, y, s, **k: ax.text(x, y, s, fontsize=k.pop('fs', 7), family=k.pop('family', 'DejaVu Sans'), **k)
    ax.plot(*rrect_xy(*TOP_OUTLINE).T, color='0.35', lw=0.6)
    ax.plot([x0c + 4, x1c - 4], [0, 0], color='0.6', lw=0.3, ls='-.')
    ax.plot([0, 0], [y0c + 4, y1c - 4], color='0.6', lw=0.3, ls='-.')
    txt(0, y1c + 2.5, 'FRONT', ha='center', fs=8, weight='bold')
    txt(0, y0c - 5.5, 'BACK  (back panel side, -y: USB-C / PORT.A / DB9 cables come out here)', ha='center', fs=8,
        weight='bold')
    rows = []
    for label, (x0, x1, y0, y1, r) in TOP_WINS:
        ax.plot(*rrect_xy(x0, x1, y0, y1, r).T, color='#d0021b', lw=0.5)
        for cx, cy in ((x0 + r, y0 + r), (x1 - r, y0 + r), (x1 - r, y1 - r), (x0 + r, y1 - r)):   # corner drills
            ax.plot([cx - 1.2, cx + 1.2], [cy, cy], color='#d0021b', lw=0.25)
            ax.plot([cx, cx], [cy - 1.2, cy + 1.2], color='#d0021b', lw=0.25)
        txt((x0 + x1) / 2, (y0 + y1) / 2 + 1.5, label, ha='center', va='center', fs=7, weight='bold', color='#d0021b')
        txt((x0 + x1) / 2, (y0 + y1) / 2 - 2.5, f'{x1 - x0:.1f} x {y1 - y0:.1f}  R{r:g}', ha='center', va='center',
            fs=6, color='#d0021b')
        rows.append(f'{label:9s} {x1 - x0:5.1f} x {y1 - y0:4.1f}  R{r:<4g} left {x0 - x0c:5.1f}  right {x1c - x1:5.1f}'
                    f'  back {y0 - y0c:5.1f}  front {y1c - y1:5.1f}   drill at the + marks, dia {2 * r:.1f} or less')
    # 50 mm check ruler
    ry = -72
    ax.plot([-25, 25], [ry, ry], color='k', lw=0.6)
    for i in range(6):
        ax.plot([-25 + 10 * i] * 2, [ry, ry + (3 if i in (0, 5) else 1.8)], color='k', lw=0.4)
    txt(0, ry - 4.5, '50 mm: measure this line. If it is not 50 mm, reprint.', ha='center', fs=7)
    notes = [f'Vein Station {REV} - PF13-4-9 cover (top plate) cutting template, 1:1, seen from above',
             'PRINT AT 100% / ACTUAL SIZE (no "fit to page", no scaling).',
             'Lay the sheet face up on the cover, BACK toward the open back (the back panel is not used),',
             'and line up the grey outline (125 x 85, R17) with the cover edges. Centre lines = case centre.',
             'Red = cut through (windows); + = corner drill centres. Unit mm. Distances from the outline:',
             ''] + rows + ['', 'No window for the NFC unit (it reads through the 3 mm plate).',
                           'Same geometry as ' + f'vein_station_{REV}_top.dxf (for Takachi machining).']
    y = -86
    for i, t in enumerate(notes):
        txt(-95, y, t, fs=6.2 if t in rows else 7, family='DejaVu Sans Mono' if t in rows else 'DejaVu Sans',
            weight='bold' if i < 2 else 'normal')
        y -= 5
    path = os.path.join(out, f'vein_station_{REV}_{name}.pdf')
    fig.savefig(path, metadata={'CreationDate': None})
    plt.close(fig)
    print('wrote', path)
    return path


downloads = [
    ('穴加工図(DXF、タカチの穴加工用)', sheet('top', 'PF13-4-9 cover (top plate) - seen from above, origin = case centre, back panel side = -y',
          ['CUT: through (2 windows: vein, VoiceS3R; corner R as drawn)', 'no window for the NFC unit',
           'the back panel is not used (no machining)', 'unit mm'], draw_top,
          -62.5, -50)),
    ('天板の型紙(PDF、A4 原寸 — 拡大縮小なしで印刷)', top_template('top_template_1to1')),
]

# ---- 3D preview ------------------------------------------------------------------------------------------
parts = [
    ('shell', 'カバー+前後パネル(タカチ PF13-4-9、実測からの簡略形状)', '#3d6fb6', 0.45, 'shell',
     cover.union(front_panel)),
    ('nfc', 'NFC Unit(公式 CAD、天板の裏に両面テープ、窓なし)', '#f2f2ee', 1, 'mods',
     stl_at('nfc', NX, (NFC[2] + NFC[3]) / 2, ZBT + SP_NFC + 2.8, TOP)),   # CAD z -2.8..5.2
] + vein_parts(VEIN, VEIN_Z0) + [
    ('atom', 'VoiceS3R(公式 CAD)', '#1fa49a', 1, 'mods', stl_at('voice', VXP, VYP, Z_ATOM, TOP)),   # CAD z 0..16.8
    ('pcb', 'Station 基板 r12(92 × 71)', '#1f7a4d', 1, 'mods', pcb),
    ('hdrpl', 'ピンヘッダー樹脂', '#2b2f33', 1, 'mods', hdr_plastic),
    ('hdrpin', 'ピン', '#d8b25a', 1, 'mods', hdr_pins),
    ('j3', 'J3 MX1.25 4P(指静脈)', '#f1efe8', 1, 'mods', j3),
    ('j3plug', 'J3 プラグ(指静脈ケーブル)', '#e7e1cf', 1, 'mods', j3_plug),
    ('u1', 'U1 MAX3232', '#202326', 1, 'mods', u1),
    ('caps', 'C1〜C5 0.1µF', '#b8a27a', 1, 'mods', caps),
    ('sw1', 'SW1 ストレート/クロス DIP', '#c0392b', 1, 'mods', sw1),
    ('db9', 'J4 DB9 オス', '#8a8f96', 1, 'mods', db9_body.union(db9_flange).union(db9_shell).union(db9_posts)),
    ('spacers', 'タカチ TPS-M2.3-7(ボスの上)+ M3 オスメス+ナット(NFC 12 / 指静脈 12)', '#c9a227', 1, 'mods', spacers),
    ('db9plug', 'DB9 プラグ(FC-1200 へ)', '#5c6166', 1, 'mods', db9_plug),
    ('usbplug', 'USB-C プラグ(Windows PC へ)', '#24292d', 1, 'mods', usb_plug),
    ('portaplug', 'PORT.A Grove プラグ(外で NFC へ折り返し)', '#c47f0e', 1, 'mods', porta_plug),
    ('nfcplug', 'NFC 側 Grove プラグ(箱の中、ケーブルは背面パネルから外へ)', '#c47f0e', 1, 'mods', nfc_plug),
    ('lid', 'ベース(床、加工なし)', '#8fa09c', 0.9, 'lid', base),
]
SUB = ('既製ケース タカチ PF13-4-9 に、基板 r12 と市販の M3 スペーサーで VoiceS3R・指静脈・NFC・DB9 を収める版'
       '(印刷部品なし、天板の窓 2 つだけ加工: 試作は型紙で手加工、量産はタカチの穴加工)。ドラッグで回転、ホイール/ピンチで拡大。')
DIMS = [('ケース', 'タカチ PF13-4-9(125 × 40 × 85、ABS)'), ('内側', '117 × 79 × 34.5、天板 3.0、パネル 2.0'),
        ('基板', 'r12 92 × 71、ケースの基板用ボスに TPS-M2.3-7 と M2.3 ねじ'),
        ('モジュール', 'NFC 12 / 指静脈 12(上面に VHB テープ)の M3 オスメスの上(基板の下でナット止め)'), ('天板の穴', '指静脈(外形 + 0.2、4.1 突き出して横を押さえる)・VoiceS3R(返し 1.2)'),
        ('背面', 'パネルを付けない(USB-C / PORT.A ・ DB9 ・ NFC の Grove ケーブルをそのまま出す)'), ('NFC', '手前左、天板の裏に付ける(窓なし、3 mm 越しに読む)')]
NOTE = ('ケースはタカチ公式 STP を実測した数値からの簡略形状です(STP は再配布しない)。VoiceS3R と NFC Unit の形は '
        'M5Stack 公式 STL(m5stack/M5_Hardware、Copyright (c) 2021 M5Stack、MIT License)をそのまま表示、'
        '干渉チェックはその外形の箱で行う。指静脈の外形は公式値(CAD が無いので、細部は製品写真を見て描いたイメージ)、'
        'DB9 と基板上の部品は KiCad のフットプリント寸法からの簡略形状、指静脈のコネクタ位置は未確定。単位 mm。')
write_page('station-pf', 'PF ' + REV, parts, SUB, DIMS, NOTE, TOP, downloads,
           '<p>試作は型紙を天板に貼って手で開ける(角をドリル → 糸のこ/カッター → やすり)。'
           'まとめて作るときはタカチの穴加工(カスタム品 見積依頼)に DXF を添えて出す。</p>')

if bad:
    raise SystemExit('interference: ' + ', '.join(bad))
