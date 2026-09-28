"""Vein Station SW75 (smallest): the vein module and the DB9 in a Takachi SW-75B (50 × 30 × 75, ABS, snap-in cover,
¥200), and the Atom VoiceS3R outside the case in line with it: the station board (pcb/station_board,
`build_board.py sw75`) fills the case and runs out through the +y end wall as a 26 wide tongue, and the VoiceS3R stands
on the tongue on its Ext.Pin (J1 / J2, stock pin headers), its USB-C / PORT.A edge outwards (+y), its top level with
the cover. The Unit NFC goes on the VoiceS3R's PORT.A. The board is one-sided (all parts on top, Economic PCBA).
Run from the repository root:  python3 station/build_station_sw75.py
Writes the 3D preview site/station-sw75/index.html, the dimensioned hole drawings of the three machined faces
(station/vein_station_<REV>_{cover,side,end}.dxf / .pdf: the cover, the +x side, the +y end, each seen from outside) and
a 1:1 A4 paper template of the same three faces for cutting them by hand (station/vein_station_<REV>_template_1to1.pdf),
and fails if the case collides with a module, plug, spacer or the board, or two of those collide with each other.

Case coordinates = the board's: x across the 50 side, y along the 75 side, origin = case centre, z = 0 at the inside
of the floor. DB9 on the +x side, the board's tongue and the VoiceS3R on the +y end.
The case is written from Takachi's drawing (SW-75□, 2024/07/16, DXF/PDF on takachi-el.co.jp): outside 50 × 75 R2 × 30,
floor 2, cover 2 thick with a 5 deep skirt, no floor ribs; inside 44.8 × 69.8 at the floor leaning in to the effective
42.8 × 67.8 at 23 (the skirt's lower edge), modelled as that loft; everything from 23 up to the cover's top face at 28 is
taken as solid (so the model is on the safe side).
Stack (z): Takachi ASR-7 stick-on tapped bosses on the floor (□20 tape base) under H1 / H4 | board 7.2..8.8 |
vein module on M3 × 6 spacers (male-female into the ASR-7 at H1 / H4, female-female with a screw from below at H2 / H3)
+ 1.0 VHB tape, 15.8..30.8: 2.8 proud of the cover through a window of its outline + 0.2; MAX3232 and J3 under it |
VoiceS3R 11.3..28.1 on the tongue's pin headers (plastic 2.5), 0.5 clear of the +y end wall | under the tongue a foot
at H5 down to the desk (M3 × 8 female-female spacer + a 1.2 rubber bumper, a pan head screw on top under the VoiceS3R).
The DB9 and the tongue pass through notches open to the top of the body, so the board drops in from above.
"""
import os
import cadquery as cq
from shapes import ROOT, box, rbox, cyl_z, stl_at, vein_parts, write_page
from template import cut_template, edge_row
from drawing import face, sheet

REV = 'sw75f'

# ---- case (Takachi SW-75B, from the drawing) --------------------------------------------------------------
OUT = (-25.0, 25.0, -37.5, 37.5)
FLOOR, CEIL, TOP = -2.0, 23.0, 28.0
inside = (cq.Workplane('XY').rect(44.8, 69.8).workplane(offset=CEIL).rect(42.8, 67.8).loft())
body = rbox(*OUT, FLOOR, TOP, 2.0).cut(inside)

# ---- board (pcb/station_board, build_board.py sw75) and what stands on it: keep these lists together with it ------
BX0, BX1, BY0, BY1 = -20.4, 20.4, -33.8, 34.3
AX, AY = 0.0, 50.0                          # VoiceS3R centre, USB-C / PORT.A edge to +y
TX, TY = 13.0, 62.0                         # the tongue: |x| <= TX, out to y = TY
HOLES = [(-6.3, -15.0), (1.2, -19.5), (-10.9, 20.5), (1.3, 20.5), (0.0, 55.0)]   # H1..H4 vein spacers, H5 the foot
ASR = (1, 4)                                # the vein spacers on ASR-7 bosses
FOOT = 5                                    # H5
DB9_BY = 0.0                                # DB9 on the +x edge
J3 = (-8.35, -22.5)                         # opening -y, under the vein socket
U1 = (-12.5, 2.0)                           # MAX3232, SOIC-16 along y
SW1 = (13.0, 25.5)                          # DIP, above the DB9 (reached with the cover off)
J1X, J2X = AX - 7.62, AX + 7.62             # Ext.Pin rows (J1 5 pins from AY - 2.54, J2 4 pins from AY, both to +y)

ZB = 7.2                                    # ASR-7
ZBT = ZB + 1.6
SP_VEIN, TAPE = 6.0, 1.0
VEIN = (-21.2, 4.8, -26.5, 32.5)            # 26 across, 59 along y, the socket end at -y, 8 from the end wall
                                            # (the cable's C loop down to J3)
VEIN_Z0 = ZBT + SP_VEIN + TAPE              # 15.8, top 30.8
Z_ATOM = ZBT + 2.5                          # VoiceS3R bottom (header plastic 2.5), top 28.1

NOTCH = (-12.0, -6.0, 2.5)                  # cut into the -y edge under the vein socket, for the cable
pcb = (box(BX0, BX1, BY0, BY1, ZB, ZBT).union(box(-TX, TX, BY1 - 1.0, TY, ZB, ZBT))
       .cut(box(NOTCH[0], NOTCH[1], BY0 - 1, BY0 + NOTCH[2], ZB - 1, ZBT + 1)))
for x, y in HOLES:
    pcb = pcb.cut(cyl_z(x, y, 1.6, ZB - 1, ZBT + 1))


def on(x0, x1, y0, y1, z0, z1):
    """Box on the board, z from the board's top face."""
    return box(x0, x1, y0, y1, ZBT + z0, ZBT + z1)


def cyl_x(x0, x1, y, z, r):
    return cq.Workplane('YZ').workplane(offset=x0).center(y, z).circle(r).extrude(x1 - x0)


# DB9 male RA turned to +x (as build_station_pf.py, from the KiCad footprint)
BX = BX1
db9_body = on(BX - 10.5, BX - 0.5, DB9_BY - 15.0, DB9_BY + 15.0, 0, 12.5)
db9_flange = on(BX, BX + 1.0, DB9_BY - 15.4, DB9_BY + 15.4, 0, 12.5)
db9_shell = on(BX + 1.0, BX + 7.0, DB9_BY - 8.5, DB9_BY + 8.5, 2.0, 10.5)
db9_tails = on(BX - 8.5, BX - 3.0, DB9_BY - 6.5, DB9_BY + 6.5, -4.6, -1.6)
DB9_ZC = ZBT + 6.25
db9_posts = cyl_x(BX + 1.0, BX + 5.0, DB9_BY - 12.5, DB9_ZC, 2.5).union(cyl_x(BX + 1.0, BX + 5.0, DB9_BY + 12.5, DB9_ZC, 2.5))
DB9_Y0, DB9_Y1 = DB9_BY - 15.4, DB9_BY + 15.4
db9_plug = box(BX + 1.8, 80, DB9_Y0 + 0.25, DB9_Y1 - 0.25, ZBT - 0.75, ZBT + 13.25)   # stops 0.8 short of the flange

j3 = on(J3[0] - 5.0, J3[0] + 5.0, J3[1] - 3.1, J3[1] + 3.7, 0, 3.4)
j3_plug = on(J3[0] - 3.0, J3[0] + 3.0, J3[1] - 9.1, J3[1] - 3.1, 0.3, 3.1)
# the vein cable (MX1.25 9P -> 4P, approx a 3 × 1 bundle): level out of the module's socket at the -y end, down through
# the board's notch, the spare length folded under the board (7.2 to the floor), back up through the notch into J3's plug
VCX = (J3[0] - 1.5, J3[0] + 1.5)
YS, YP = VEIN[2], J3[1] - 9.1                              # socket face, plug's back
YN = (BY0 + 0.5, BY0 + 1.5)                                # the run down / up, inside the notch
ZS, ZP = VEIN_Z0 + 3.2, ZBT + 1.7                          # socket and plug centre heights
vein_cable = (box(*VCX, YN[0], YS, ZS - 0.5, ZS + 0.5)                       # socket -> over the notch
              .union(box(*VCX, *YN, 2.0, ZS + 0.5))                          # down / up through the notch
              .union(box(*VCX, YN[0], YP, ZP - 0.5, ZP + 0.5))               # plug's back -> the notch
              .union(box(J3[0] - 3.5, J3[0] + 3.0, YN[0], BY0 + 7.0, 2.0, 5.5)))   # spare length under the board
u1 = on(U1[0] - 1.95, U1[0] + 1.95, U1[1] - 4.95, U1[1] + 4.95, 0, 1.75)
caps = on(-8.8, -7.2, -5.5, 8.0, 0, 0.9).union(on(-18.0, -15.0, 7.8, 9.2, 0, 0.9))
sw1 = on(SW1[0] - 5.86, SW1[0] + 5.86, SW1[1] - 3.35, SW1[1] + 3.35, 0, 3.0)

# Ext.Pin headers on the tongue (plastic 2.54 × 2.5, pins up 6 into the VoiceS3R, tails 3 under the board)
hdr_plastic = on(J1X - 1.27, J1X + 1.27, AY - 3.81, AY + 8.89, 0, 2.5).union(
    on(J2X - 1.27, J2X + 1.27, AY - 1.27, AY + 8.89, 0, 2.5))
hdr_pins = on(J1X - 0.32, J1X + 0.32, AY - 2.86, AY + 7.94, -4.6, 8.5).union(
    on(J2X - 0.32, J2X + 0.32, AY - 0.32, AY + 7.94, -4.6, 8.5))
atom = rbox(AX - 12, AX + 12, AY - 12, AY + 12, Z_ATOM, Z_ATOM + 16.8, 3.0)
YF = AY + 12                                               # the USB-C / PORT.A face
usb_plug = box(AX - 6, AX + 6, YF + 6.5, YF + 24.2, Z_ATOM + 4.0, Z_ATOM + 11.0).union(
    box(AX - 4.2, AX + 4.2, YF, YF + 6.5, Z_ATOM + 6.0, Z_ATOM + 9.0))
porta_plug = box(AX - 4.9, AX + 4.9, YF, YF + 10.2, Z_ATOM + 0.0, Z_ATOM + 4.0)

# spacers: M3 × 6 (hex 5.5 as r 3.2) on the board; under it the male end into an ASR-7 (φ7 boss on a □20 tape
# base) at H1 / H4, a pan head screw (r 2.8 × 2) elsewhere. The foot at H5: M3 × 8 female-female + 1.2 rubber bumper
# down to the desk (z = FLOOR), a pan head screw on top (under the VoiceS3R, 0.5 clear)
spacers = asr = foot = None
for i, (x, y) in enumerate(HOLES, 1):
    if i == FOOT:
        foot = cyl_z(x, y, 3.2, FLOOR, ZB).union(cyl_z(x, y, 2.8, ZBT, ZBT + 2.0))
        continue
    parts = [cyl_z(x, y, 3.2, ZBT, ZBT + SP_VEIN)]
    if i in ASR:
        a = box(x - 10.0, x + 10.0, y - 10.0, y + 10.0, 0, 1.0).union(cyl_z(x, y, 3.5, 1.0, ZB))
        asr = a if asr is None else asr.union(a)
    else:
        parts.append(cyl_z(x, y, 2.8, ZB - 2.0, ZB))
    for s in parts:
        spacers = s if spacers is None else spacers.union(s)

vein = rbox(*VEIN, VEIN_Z0, VEIN_Z0 + 15.0, 2.0)

# ---- machining ---------------------------------------------------------------------------------------------
VEIN_WIN = (VEIN[0] - 0.2, VEIN[1] + 0.2, VEIN[2] - 0.2, VEIN[3] + 0.2, 2.2)
cover_cut = rbox(*VEIN_WIN[:4], CEIL - 1, TOP + 1, VEIN_WIN[4])
# wall cut-outs as (along the wall 0, 1, z0, z1, R) in case coords: y on the +x side, x on the +y end. Both are open to
# the body's top edge (23, under the cover's skirt), so the board drops in from above with the DB9 and the tongue in them
DB9_CUT = (DB9_Y0 - 0.25, DB9_Y1 + 0.25, ZBT - 1.5, CEIL, 0)                              # DB9 hood (+x)
TONGUE_CUT = (-TX - 0.5, TX + 0.5, ZB - 0.4, CEIL, 0)                                     # the board's tongue (+y)
SIDE = (BX1 + 0.5, OUT[1] + 1)             # the +x wall
END = (BY1 - 0.5, OUT[3] + 1)              # the +y wall
wall_cut = box(*SIDE, *DB9_CUT[:4]).union(box(*TONGUE_CUT[:2], *END, *TONGUE_CUT[2:4]))
case = body.cut(cover_cut).cut(wall_cut)

# ---- interference ------------------------------------------------------------------------------------------
checks = [('指静脈', vein), ('vein cable', vein_cable), ('board', pcb), ('J3', j3), ('J3 plug', j3_plug), ('MAX3232', u1),
          ('caps', caps), ('SW1', sw1), ('DB9 body', db9_body), ('DB9 flange', db9_flange), ('DB9 shell', db9_shell),
          ('DB9 posts', db9_posts), ('DB9 tails', db9_tails), ('spacers', spacers), ('ASR-7', asr), ('foot', foot),
          ('DB9 plug', db9_plug), ('headers', hdr_plastic.union(hdr_pins)), ('VoiceS3R', atom), ('USB plug', usb_plug),
          ('PORT.A plug', porta_plug)]
bad = []
for name, obj in checks:
    v = case.intersect(obj).val().Volume()
    print(f'interference case x {name:14s} = {v:.3f} mm3')
    if v > 0.01:
        bad.append(f'case/{name}')
mutual = [('指静脈', vein), ('vein cable', vein_cable), ('spacers', spacers), ('ASR-7', asr), ('J3 plug', j3_plug),
          ('MAX3232', u1), ('caps', caps), ('SW1', sw1), ('DB9 body', db9_body), ('DB9 tails', db9_tails),
          ('DB9 plug', db9_plug), ('header plastic', hdr_plastic), ('VoiceS3R', atom), ('foot', foot),
          ('USB plug', usb_plug), ('PORT.A plug', porta_plug)]
for i, (na, a) in enumerate(mutual):
    for nb, b in mutual[i + 1:]:
        v = a.intersect(b).val().Volume()
        if v > 0.01:
            print(f'interference {na} x {nb} = {v:.3f} mm3')
            bad.append(f'{na}/{nb}')
v = vein_cable.intersect(pcb).val().Volume()                  # the cable passes the board only through the notch
if v > 0.01:
    print(f'interference vein cable x board = {v:.3f} mm3')
    bad.append('vein cable/board')
print('parts among themselves: ' + ('ok' if not any(not b.startswith('case/') for b in bad) else 'NG'))

# ---- hole drawings and the 1:1 template (the cover, the +x side, the +y end, each seen from outside) ---------
# Faces in their own 2D coords: the cover as the case's x, y (seen from above); the walls with the height h = z - FLOOR
# (0 = the floor's outside face, 30 = the cover's top face) and along the wall as seen from outside: y on the +x side
# (+y to the right), -x on the +y end (+x, the DB9 side, to the left). The side and end holes are dimensioned from the
# bottom-left corner (what a ruler starts from), the cover's from the case centre (as Takachi machine).
H = TOP - FLOOR
COVER = (*OUT, 2.0)
SIDE_FACE = (OUT[2], OUT[3], 0, H, 0)
END_FACE = (-OUT[1], -OUT[0], 0, H, 0)
cover_cuts = [('vein', ('rect', *VEIN_WIN))]
side_cuts = [('DB9', ('rect', *DB9_CUT[:2], DB9_CUT[2] - FLOOR, DB9_CUT[3] - FLOOR, DB9_CUT[4]))]
end_cuts = [('board', ('rect', -TONGUE_CUT[1], -TONGUE_CUT[0], TONGUE_CUT[2] - FLOOR, TONGUE_CUT[3] - FLOOR,
                       TONGUE_CUT[4]))]
SIDE_NAMES, END_NAMES = ('-y end', '+y end', 'bottom', 'top'), ('+x side', '-x side', 'bottom', 'top')
out = os.path.join(ROOT, 'station')


def size(c):
    if c[0] == 'circle':
        return f'dia {2 * c[3]:.1f}'
    return f'{c[2] - c[1]:.1f} x {c[4] - c[3]:.1f}' + (f', 4-R{c[5]:g}' if c[5] else ', square corners')


def draw_cover(msp):
    face(msp, COVER, [dict(cut=cover_cuts[0][1], at=(VEIN_WIN[0] + 1.5, 22), hdim=VEIN_WIN[0] + 4,
                           text=('vein window, through', size(cover_cuts[0][1])))],
         titles=[('+y END (the VoiceS3R outside)', (0, OUT[3] + 16)), ('-y END', (0, OUT[2] - 22))])


def draw_side(msp):
    face(msp, SIDE_FACE, [dict(cut=side_cuts[0][1], at=(-14, 21), wdim=H + 3, hdim=side_cuts[0][1][1] - 4,
                               text=('DB9 hood, open to the top', size(side_cuts[0][1])))],
         titles=[('+x SIDE seen from outside: -y end left, +y (VoiceS3R) end right', (0, -24)),
                 ('bottom edge = the floor\'s outside face (z -2), top edge = the cover\'s top (z 28)', (0, -29))],
         datum=(SIDE_FACE[0], 0))


def draw_end(msp):
    c = end_cuts[0][1]
    face(msp, END_FACE, [dict(cut=c, at=(c[1] + 1.5, c[4] - 4), wdim=H + 3,
                              text=('board tongue, open to the top', size(c)))],
         titles=[('+y END seen from outside: +x (DB9 side) left, -x right', (0, -24)),
                 ('bottom edge = the floor\'s outside face (z -2), top edge = the cover\'s top (z 28)', (0, -29))],
         datum=(END_FACE[0], 0))


def wall_view(outline, cuts, at, label, left, right):
    x0, x1, _, h, _ = outline
    g = dict(color='0.6', lw=0.3)
    small = [(n, c) for n, c in cuts if c[0] == 'circle' or c[2] - c[1] <= 12]   # labelled under the hole, big ones inside
    return dict(outline=outline, at=at, holes=[c if (n, c) in small else (*c, n) for n, c in cuts],
                lines=[([x, x], [0, h], dict(g, ls='--')) for x in (x0 + COVER[4], x1 - COVER[4])] +
                      [([(x0 + x1) / 2] * 2, [-2, h + 2], dict(g, ls='-.'))],
                text=[(x0, h + 3, label, dict(fs=7, weight='bold')),
                      (x0 - 1.5, h / 2, left, dict(ha='right', va='center', fs=6, color='0.4')),
                      (x1 + 1.5, h / 2, right, dict(ha='left', va='center', fs=6, color='0.4')),
                      ((x0 + x1) / 2, -3.5, 'BOTTOM (desk side)', dict(ha='center', fs=6, weight='bold'))] +
                     [(c[1], c[2] - c[3] - 2.8, n, dict(ha='center', fs=5.5, color='#d0021b')) if c[0] == 'circle' else
                      ((c[1] + c[2]) / 2, c[3] - 2.8, n, dict(ha='center', fs=5.5, color='#d0021b')) for n, c in small])


def template():
    x0, x1, y0, y1, _ = COVER
    g = dict(color='0.6', lw=0.3, ls='-.')
    b = dict(ha='center', fs=7, weight='bold')
    cover = dict(outline=COVER, at=(-62, 2), holes=[('rect', *VEIN_WIN, 'vein')],
                 lines=[([x0 + 4, x1 - 4], [0, 0], g), ([0, 0], [y0 + 4, y1 - 4], g)],
                 text=[(x0, y1 + 9, 'COVER, seen from above', dict(fs=8, weight='bold')),
                       (0, y1 + 2.5, '+y END (VoiceS3R)', b), (0, y0 - 5.5, '-y END', b),
                       (x1 + 2, 0, '+x SIDE\n(DB9)', dict(ha='left', va='center', fs=6.5, weight='bold'))])
    side = wall_view(SIDE_FACE, side_cuts, (50, 8), '+x SIDE, seen from outside', '-y', '+y')
    end = wall_view(END_FACE, end_cuts, (50, -38), '+y END, seen from outside', '+x', '-x')
    rows = ([edge_row(n, c, COVER, ('-x', '+x', '-y', '+y')) for n, c in cover_cuts] + [''] +
            [edge_row(n, c, SIDE_FACE, SIDE_NAMES) for n, c in side_cuts] + [''] +
            [edge_row(n, c, END_FACE, END_NAMES) for n, c in end_cuts])
    notes = [f'Vein Station {REV} - Takachi SW-75B cutting template, 1:1 (cover, +x side, +y end, all seen from outside)',
             'PRINT AT 100% / ACTUAL SIZE (no "fit to page", no scaling).',
             'Cut the three views apart. Cover: face up on the cover, grey outline (50 x 75, R2) on the cover edges.',
             'Side / end: the grey line is the whole case (cover on, 30 high): its BOTTOM edge on the desk side of the body,',
             'its ends on the case ends; dashed = where the corner radius starts. All wall cuts are in the body.',
             'The DB9 and board cuts are open to the top of the body (so the board drops in): cut up to the body\'s edge.',
             'Red = cut through; + = corner drill centres. Unit mm.',
             'Distances: cover from the outline edges; side / end from the ends, the bottom (floor outside) and the top',
             '(the cover\'s top face, 30 above the bottom).', ''] + rows
    return cut_template(os.path.join(out, f'vein_station_{REV}_template_1to1.pdf'), 60, [cover, side, end], -62, -76,
                        notes, rows)


dxf = {}
for name, title, notes, draw, x0, y0 in (
        ('cover', 'SW-75B cover - seen from OUTSIDE (above), origin = case centre, +y = the VoiceS3R end',
         ['CUT: vein window (corner R as dimensioned), through', 'dimensions: centre from the case centre, size',
          'unit mm'], draw_cover, OUT[0], OUT[2] - 30),
        ('side', 'SW-75B body, +x side - seen from OUTSIDE, datum = bottom left (-y end, floor outside)',
         ['CUT: DB9 hood (square corners), open to the top of the body', 'heights from the bottom (the floor\'s outside face)',
          'unit mm'], draw_side, SIDE_FACE[0], -36),
        ('end', 'SW-75B body, +y end - seen from OUTSIDE, datum = bottom left (+x side, floor outside)',
         ['CUT: the board\'s tongue (square corners), open to the top of the body',
          'heights from the bottom (the floor\'s outside face)', 'unit mm'], draw_end, END_FACE[0], -36)):
    dxf[name] = sheet(os.path.join(out, f'vein_station_{REV}_{name}.dxf'), title, notes, draw, x0, y0)
downloads = [('型紙(PDF、A4 原寸 — 拡大縮小なしで印刷。カバー・+x 側面・+y 端面)', template())]
for name, label in (('cover', 'カバー'), ('side', '+x 側面(DB9)'), ('end', '+y 端面(基板の出っ張り)')):
    downloads += [(f'加工図 {label}(DXF、寸法入り)', dxf[name][0]), (f'加工図 {label}(PDF、DXF と同じ図)', dxf[name][1])]

# ---- 3D preview ------------------------------------------------------------------------------------------
cover = case.intersect(box(-26, 26, -39, 39, CEIL, TOP + 1))
shell = case.intersect(box(-26, 26, -39, 39, FLOOR - 1, CEIL))
NFC_X, NFC_Y = AX + 40.0, YF + 10.0        # the Unit NFC on the desk beside the VoiceS3R, its Grove towards PORT.A
parts = [
    ('shell', 'カバー(タカチ SW-75B、指静脈の窓)', '#2b2f33', 0.45, 'shell', cover),
    ('atom', 'VoiceS3R(公式 CAD、ケースの外で基板の出っ張りに立つ。USB-C / PORT.A は +y)', '#1fa49a', 1, 'mods',
     stl_at('voice', AX, AY, Z_ATOM, TOP, turn=True)),                     # CAD z 0..16.8
    ('nfc', 'NFC Unit(公式 CAD、机の上。Grove ケーブルで VoiceS3R の PORT.A へ)', '#f2f2ee', 1, 'mods',
     stl_at('nfc', NFC_X, NFC_Y, FLOOR + 2.8, TOP)),   # CAD z -2.8..5.2
] + vein_parts(VEIN, VEIN_Z0, along_y=True) + [
    ('pcb', 'station 基板 sw75(ケースいっぱい + +y へ出る幅 26 の舌、片面実装)', '#1f7a4d', 1, 'mods', pcb),
    ('hdr', 'J1 / J2 ピンヘッダー(VoiceS3R の Ext.Pin)', '#2b2f33', 1, 'mods', hdr_plastic.union(hdr_pins)),
    ('j3', 'J3 MX1.25 4P(指静脈)', '#f1efe8', 1, 'mods', j3),
    ('j3plug', 'J3 プラグ(指静脈ケーブル)', '#e7e1cf', 1, 'mods', j3_plug),
    ('veincable', '指静脈のケーブル(基板の切り欠きから下へ、余りは基板の下、おおよその通り道)', '#b04a2f', 1, 'mods', vein_cable),
    ('u1', 'U1 MAX3232 と C1〜C5(指静脈の下)', '#202326', 1, 'mods', u1.union(caps)),
    ('sw1', 'SW1 ストレート / クロス DIP(DB9 の上、カバーを外して切り替え)', '#c0392b', 1, 'mods', sw1),
    ('db9', 'J4 DB9 オス(右の側面)', '#8a8f96', 1, 'mods', db9_body.union(db9_flange).union(db9_shell).union(db9_posts)),
    ('spacers', 'M3 × 6(指静脈、上面に VHB テープ)', '#c9a227', 1, 'mods', spacers),
    ('asr', 'タカチ ASR-7(床に貼るボス、H1 / H4 のスペーサーを受ける)', '#e8e4d8', 1, 'mods', asr),
    ('foot', '舌の足(M3 × 8 メスメス + ゴム足 1.2、上はなべねじ)', '#c9a227', 1, 'mods', foot),
    ('db9plug', 'DB9 プラグ(FC-1200 へ)', '#5c6166', 1, 'mods', db9_plug),
    ('usbplug', 'USB-C プラグ(Windows PC へ)', '#24292d', 1, 'mods', usb_plug),
    ('portaplug', 'PORT.A Grove プラグ(NFC へ)', '#c47f0e', 1, 'mods', porta_plug),
    ('lid', 'ボディ(タカチ SW-75B、側面に DB9、端面に基板を通す切り欠き)', '#8fa09c', 0.9, 'lid', shell),
]
SUB = ('最小案: 指静脈と DB9 をタカチ SW-75B(50 × 30 × 75)に入れ、VoiceS3R はケースの外で、端面から出した基板の舌に'
       '立てる版(片面実装、NFC は VoiceS3R の PORT.A)。ドラッグで回転、ホイール/ピンチで拡大。')
DIMS = [('ケース', 'タカチ SW-75B(50 × 30 × 75、ABS、はめ込み式)。VoiceS3R を入れて全長 約 100'),
        ('内側', '床 44.8 × 69.8 → 縁の下 42.8 × 67.8、高さ 23(図面の有効寸法)'),
        ('基板', 'station 基板 sw75(40.8 × 68.1 + 幅 26 の舌が端面から 27.7 出る)、部品は全部上面。床に貼る ASR-7 × 2 にスペーサーのオス側でねじ込む(7.2)'),
        ('VoiceS3R', '舌の上に Ext.Pin(J1 / J2、普通のピンヘッダー)で立てる。上面はカバーと同じ高さ(28.1)、USB-C / PORT.A は外(+y)'),
        ('指静脈', 'M3 × 6 の上に VHB テープ、カバーから 2.8 突き出す。MAX3232 と J3 はその下。ケーブルは基板の -y 端の切り欠きから下へ逃がして J3 へ'),
        ('NFC', '箱の外、VoiceS3R の PORT.A へ'),
        ('加工', 'カバーに指静脈の窓、+x の側面に DB9 の切り欠き、+y の端面に基板の舌を通す切り欠き(どちらも上まで開いていて、基板を上から落とし込む)'),
        ('舌の足', 'H5 に M3 × 8 メスメス + ゴム足 1.2 で机に当てる(VoiceS3R のボタンを押したときのたわみ止め)')]
NOTE = ('ケースはタカチの外形図(SW-75□)からの簡略形状です(縁の下 23 から上は全部ふさがっているとして安全側に見ている)。'
        'VoiceS3R と NFC Unit の形は M5Stack 公式 STL(m5stack/M5_Hardware、Copyright (c) 2021 M5Stack、MIT License)、'
        '干渉チェックは VoiceS3R の外形の箱で行う。指静脈の外形は公式値(細部は写真からのイメージ)、基板上の部品は KiCad の'
        'フットプリント寸法からの簡略形状、指静脈のコネクタ位置は未確定。単位 mm。')
write_page('station-sw75', 'SW75 ' + REV, parts, SUB, DIMS, NOTE, TOP, downloads,
           '<p>試作は型紙を切り分けてカバー・ボディに貼り、手で開ける(角をドリル → 糸のこ/ピラニアソー → やすり)。'
           '側面・端面の高さはボディの底(床の外面)から測る。</p>')

if bad:
    raise SystemExit('interference: ' + ', '.join(bad))
