"""Vein Station PF: the station in an off-the-shelf Takachi PF13-4-9 (125 × 40 × 85, ABS, front/back panels, ¥710)
instead of a printed enclosure. Nothing is printed: the station board r12 (pcb/station_board, `build_board.py pf`)
stands on stock M3 hex spacers, and the modules stand on spacers on the board.
Run from the repository root:  python3 station/build_station_pf.py
Writes the hole drawings for Takachi's machining service (station/vein_station_pf<N>_{top,floor}.dxf) and the
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

Stack (z): floor -1.5 | M3 spacer 12 (female-female, M3 flat-head screw from below through a countersunk floor hole)
| board 10.5..12.1 | VoiceS3R 14.6..31.4 on the Ext.Pin (0.6 under the panel-groove ledge; its button is not used)
| vein module on 6 mm spacers, pressed 0.1 against the top plate lip | Unit NFC on 12 mm spacers, 24.1..32.1, stuck to the
top plate's underside with foam tape (gap 0.2..0.9), no window: it reads through the 3 mm ABS. Flush in a window
would not work: its Grove plug would then sit in the top plate.
Every vein corner and the NFC's left corners have a floor spacer right under the module spacer (male-female through
the board hole), so pressing a finger on the module goes straight down to the floor and does not bend the board.
Layout: back row VoiceS3R + DB9 on the board (the DB9 posts are 0.1 from the panel guides, the row cannot move right);
the NFC at the front left (its Grove plug inside, the cable leaves through the open back to PORT.A outside), right of
the left PCB bosses; the vein module on the right, behind the right front PCB boss (both bosses stay).
The back panel is left off: every connection is on that side, so there is nothing to machine there (no D-sub cutout,
no counterbore). The DB9 plug's push goes into the board and its floor spacers instead of the panel.
"""
import base64, json, os
import numpy as np
import cadquery as cq
import ezdxf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REV = 'pf2'

# ---- helpers ---------------------------------------------------------------------------------------------
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
ZB = FLOOR + 12.0              # board bottom on 12 mm spacers
ZBT = ZB + 1.6
Z_ATOM = ZBT + 2.5             # VoiceS3R bottom (header plastic 2.5)
BX0, BX1, BY0, BY1 = -48.0, 38.0, -11.0, 60.0     # pf outline (build_board.py pf)
# H1..H9 in board coords, the same list as build_board.py (keep them together)
HOLES = [(30.9, 17.5), (14.9, 17.5), (30.9, 55.5), (14.9, 55.5), (5.2, 27.5), (-43.8, 27.5), (5.2, 42.5),
         (-43.8, 42.5), (-44.5, 16.5)]
FLOOR_H, NFC_H, VEIN_H = (1, 3, 5, 6, 7, 8, 9), (1, 2, 3, 4), (5, 6, 7, 8)
SP_FLOOR, SP_NFC, SP_VEIN = 12.0, 12.0, 6.0


def at(bx, by):
    return VXP - bx, VYP + by


def board(bx0, bx1, by0, by1, z0, z1):
    """Box in board coords (z from the VoiceS3R bottom face) -> case coords."""
    return box(VXP - bx1, VXP - bx0, VYP + by0, VYP + by1, Z_ATOM + z0, Z_ATOM + z1)


pcb = board(BX0, BX1, BY0, BY1, -4.1, -2.5)
for bx, by in HOLES:
    x, y = at(bx, by)
    pcb = pcb.cut(cyl_z(x, y, 1.6, ZB - 1, ZBT + 1))
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
vein = rbox(*VEIN, CEIL - 15.0, CEIL, 2.0)                         # 6 mm spacers push it 0.1 against the lip
NX = (NFC[0] + NFC[1]) / 2

# spacers: hex 5.5 across flats, modelled as r 3.2 cylinders
spacers = None
for i, (bx, by) in enumerate(HOLES, 1):
    x, y = at(bx, by)
    parts = []
    if i in FLOOR_H:
        parts.append(cyl_z(x, y, 3.2, FLOOR, ZB))
    if i in NFC_H:
        parts.append(cyl_z(x, y, 3.2, ZBT, ZBT + SP_NFC))
    if i in VEIN_H:
        parts.append(cyl_z(x, y, 3.2, ZBT, CEIL - 15.0))
    for p in parts:
        spacers = p if spacers is None else spacers.union(p)

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
# top plate: vein window with a 1.0 lip, VoiceS3R window with a 1.2 lip; no NFC window
VEIN_WIN = (VEIN[0] + 1, VEIN[1] - 1, VEIN[2] + 1, VEIN[3] - 1, 1.5)
VOICE_WIN = (VOICE[0] + 1.2, VOICE[1] - 1.2, VOICE[2] + 1.2, VOICE[3] - 1.2, 1.8)
FLOOR_HOLES = [at(*HOLES[i - 1]) for i in FLOOR_H]               # M3 countersunk (flat head from below)
cover = cover.cut(rbox(*VEIN_WIN[:4], CEIL - 1, TOP + 1, VEIN_WIN[4]))
cover = cover.cut(rbox(*VOICE_WIN[:4], CEIL - 1, TOP + 1, VOICE_WIN[4]))
for x, y in FLOOR_HOLES:
    base = base.cut(cyl_z(x, y, 1.7, -5, 0)).cut(cq.Workplane('XY').workplane(offset=-4.0).center(x, y)
                                                 .circle(3.15).workplane(offset=1.5).circle(1.65).loft())

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
mutual = [('VoiceS3R', atom), ('指静脈', vein), ('NFC', nfc), ('spacers', spacers), ('J3 plug', j3_plug),
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


def draw_top(msp):
    # seen from above, origin = case centre (x across 125, y across 85, back panel at the bottom)
    rrect(msp, -62.5, 62.5, -42.5, 42.5, 17.0, 'OUTLINE')
    rrect(msp, *VEIN_WIN, 'CUT')
    rrect(msp, *VOICE_WIN, 'CUT')


def draw_floor(msp):
    # seen from BELOW (the machining side), origin = case centre: x is mirrored
    rrect(msp, -62.5, 62.5, -42.5, 42.5, 17.0, 'OUTLINE')
    for x, y in FLOOR_HOLES:
        msp.add_circle((-x, y), 1.7, dxfattribs={'layer': 'CUT'})
        msp.add_circle((-x, y), 3.15, dxfattribs={'layer': 'CSK'})


dxfs = [
    sheet('top', 'PF13-4-9 cover (top plate) - seen from above, origin = case centre, back panel side = -y',
          ['CUT: through (2 windows: vein, VoiceS3R; corner R as drawn)', 'no window for the NFC unit',
           'the back panel is not used (no machining)', 'unit mm'], draw_top,
          -62.5, -50),
    sheet('floor', 'PF13-4-9 base (floor) - seen from BELOW, origin = case centre',
          [f'CUT: dia 3.4 through x {len(FLOOR_HOLES)}', 'CSK: 90 deg countersink dia 6.3 for M3 flat head, from below', 'unit mm'],
          draw_floor, -62.5, -50),
]

# ---- 3D preview ------------------------------------------------------------------------------------------
def tri(shape):
    vs, ts = shape.val().tessellate(0.03, 0.15)
    v = np.array([(p.x, p.y, p.z - TOP) for p in vs], dtype=np.float32)
    return v[np.array(ts)].reshape(-1).astype(np.float32)


parts = [
    ('shell', 'カバー+前後パネル(タカチ PF13-4-9、実測からの簡略形状)', '#3d6fb6', 0.45, 'shell',
     cover.union(front_panel)),
    ('nfc', 'NFC Unit 48×24×8(天板の裏に両面テープ、窓なし)', '#f2f2ee', 1, 'mods', nfc),
    ('vein', '指静脈モジュール(外形は公式値、コネクタ位置は未確定)', '#2e3538', 1, 'mods', vein),
    ('atom', 'VoiceS3R', '#1fa49a', 1, 'mods', atom),
    ('pcb', 'Station 基板 r12(86 × 71)', '#1f7a4d', 1, 'mods', pcb),
    ('hdrpl', 'ピンヘッダー樹脂', '#2b2f33', 1, 'mods', hdr_plastic),
    ('hdrpin', 'ピン', '#d8b25a', 1, 'mods', hdr_pins),
    ('j3', 'J3 MX1.25 4P(指静脈)', '#f1efe8', 1, 'mods', j3),
    ('j3plug', 'J3 プラグ(指静脈ケーブル)', '#e7e1cf', 1, 'mods', j3_plug),
    ('u1', 'U1 MAX3232', '#202326', 1, 'mods', u1),
    ('caps', 'C1〜C5 0.1µF', '#b8a27a', 1, 'mods', caps),
    ('sw1', 'SW1 ストレート/クロス DIP', '#c0392b', 1, 'mods', sw1),
    ('db9', 'J4 DB9 オス', '#8a8f96', 1, 'mods', db9_body.union(db9_flange).union(db9_shell).union(db9_posts)),
    ('spacers', 'M3 六角スペーサー(床 12 / NFC 12 / 指静脈 6)', '#c9a227', 1, 'mods', spacers),
    ('db9plug', 'DB9 プラグ(FC-1200 へ)', '#5c6166', 1, 'mods', db9_plug),
    ('usbplug', 'USB-C プラグ(Windows PC へ)', '#24292d', 1, 'mods', usb_plug),
    ('portaplug', 'PORT.A Grove プラグ(外で NFC へ折り返し)', '#c47f0e', 1, 'mods', porta_plug),
    ('nfcplug', 'NFC 側 Grove プラグ(箱の中、ケーブルは背面パネルから外へ)', '#c47f0e', 1, 'mods', nfc_plug),
    ('lid', 'ベース(床、M3 皿穴 7)', '#8fa09c', 0.9, 'lid', base),
]
model = [dict(key=k, label=l, color=c, opacity=o, group=g, data=base64.b64encode(tri(s).tobytes()).decode())
         for k, l, c, o, g, s in parts]
SUB = ('既製ケース タカチ PF13-4-9 に、基板 r12 と市販の M3 スペーサーで VoiceS3R・指静脈・NFC・DB9 を収める版'
       '(印刷部品なし、穴はタカチの穴加工)。ドラッグで回転、ホイール/ピンチで拡大。')
DIMS = [('ケース', 'タカチ PF13-4-9(125 × 40 × 85、ABS)'), ('内側', '117 × 79 × 34.5、天板 3.0、パネル 2.0'),
        ('基板', 'r12 86 × 71、床から M3 スペーサー 12(皿ネジ × 7)'),
        ('モジュール', 'NFC 12 / 指静脈 6 の M3 スペーサーの上(指静脈の四隅は床まで重ねる)'), ('天板の穴', '指静脈(返し 1.0)・VoiceS3R(返し 1.2)'),
        ('背面', 'パネルを付けない(USB-C / PORT.A ・ DB9 ・ NFC の Grove ケーブルをそのまま出す)'), ('NFC', '手前左、天板の裏に付ける(窓なし、3 mm 越しに読む)')]
NOTE = ('ケースはタカチ公式 STP を実測した数値からの簡略形状です(STP は再配布しない)。モジュールの外形は公式値、'
        'DB9 と基板上の部品は KiCad のフットプリント寸法からの簡略形状、指静脈のコネクタ位置は未確定。単位 mm。')
dims = ''.join(f'        <tr><td>{k}</td><td>{v}</td></tr>\n' for k, v in DIMS)
site = os.path.join(ROOT, 'site/station-pf')
os.makedirs(site, exist_ok=True)
rows = []
for p in dxfs:
    import shutil
    shutil.copyfile(p, os.path.join(site, os.path.basename(p)))
    rows.append(f'<a href="{os.path.basename(p)}" download>穴加工図<span>{os.path.basename(p)}</span></a>')
rows.append('<p>タカチの穴加工(カスタム品 見積依頼)に DXF を添えて出す。</p>')
tpl = open(os.path.join(ROOT, 'tools/station_template.html'), encoding='utf-8').read()
page = os.path.join(site, 'index.html')
open(page, 'w', encoding='utf-8').write(
    tpl.replace('__MODEL__', json.dumps(model)).replace('__REV__', 'PF ' + REV).replace('__SUB__', SUB)
    .replace('__DIMS__', dims).replace('__NOTE__', NOTE).replace('__TZ__', '-18').replace('__DOWNLOADS__', ''.join(rows)))
print('wrote', page, os.path.getsize(page), 'bytes')

if bad:
    raise SystemExit('interference: ' + ', '.join(bad))
