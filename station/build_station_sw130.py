"""Vein Station SW130 (slim): everything inside a Takachi SW-130B (40 × 25 × 130, ABS, snap-in cover, ¥360) in a row
along it: the DB9 on the -y end, the vein module, the DIP and the MAX3232, and the Atom VoiceS3R at the +y end. The
station board (pcb/station_board, `build_board.py sw130`, one-sided, Economic PCBA) fills the case floor; the VoiceS3R
stands on it on its Ext.Pin (J1 / J2, stock pin headers), centred, its USB-C / PORT.A edge to +y (both through
one hole in the +y end wall), its top 1.4 proud of the cover through a window. The Unit NFC plugs into the board's Grove J6 on the -x
side by the DB9 (G38 / G39 as I2C), so NFC and USB leave on different faces; the VoiceS3R's PORT.A is spare, reachable through the USB hole. Its
reset button (a U-shaped flap on the face left of the ports) faces the +x side, where a 6 × 8 hole takes a screwdriver.
Run from the repository root:  python3 station/build_station_sw130.py
Writes the 3D preview site/station-sw130/index.html, the dimensioned hole drawings of the four machined faces
(station/vein_station_<REV>_{cover,side,side_nfc,end_db9,end_usb}.dxf / .pdf, each seen from outside) and a 1:1 A4 paper template
of the same faces (station/vein_station_<REV>_template_1to1.pdf), and fails if the case collides with a module, plug,
spacer or the board, or two of those collide with each other.

Case coordinates = the board's: x across the 40 side, y along the 130 side, origin = case centre, z = 0 at the inside
of the floor. The case is written from Takachi's drawing (SW-130□, 2024/07/16, DXF/PDF on takachi-el.co.jp): outside
40 × 130 R3 × 25, floor 2.5 and cover 2.5 thick, no bosses or ribs; inside 35.5 × 125.5 up to 17, where the cover's
skirt (3 deep, the cover 5.5 in all) narrows it to 32.8 × 122.8 up to the cover's underside at 20; top face 22.5.
Stack (z): M3 × 3 spacers stuck to the floor (VHB) | board 3.0..4.6 (THT tails down to the floor: cut them to 3) |
vein module on M3 × 5 spacers over H1..H4 + 0.7 VHB, 10.3..25.3: 2.8 proud of the cover through a window of its outline
+ 0.2 | VoiceS3R 7.1..23.9 on the pin headers (plastic 2.5), through a window of its outline + 0.2 | DB9 up to 17.1,
0.1 into the skirt's height: the skirt's lower edge is filed back 0.8 over the DB9 (the only cut in the cover's skirt).
The DB9 notch in the -y end wall is open to the top of the body, so the board drops in from above; the USB-C / PORT.A
notch in the +y end is open to the top as well (a closed hole would leave a 0.3 bridge under the body's top edge).
"""
import os
import cadquery as cq
from shapes import ROOT, box, rbox, cyl_z, cyl_y, stl_at, vein_parts, write_page
from template import cut_template, edge_row
from drawing import face, sheet

REV = 'sw130d'

# ---- case (Takachi SW-130B, from the drawing) ------------------------------------------------------------
OUT = (-20.0, 20.0, -65.0, 65.0)
FLOOR, SKIRT, CEIL, TOP = -2.5, 17.0, 20.0, 22.5
IN = (-17.75, 17.75, -62.75, 62.75)          # inside up to the skirt
SK = (-16.4, 16.4, -61.4, 61.4)              # inside the cover's skirt
body = rbox(*OUT, FLOOR, TOP, 3.0).cut(rbox(*IN, 0, SKIRT, 1.0)).cut(rbox(*SK, SKIRT - 0.01, CEIL, 1.0))

# ---- board (pcb/station_board, build_board.py sw130) and what stands on it: keep these numbers together with it ----
BX0, BX1, BY0, BY1 = -17.4, 17.4, -61.7, 61.0
AX, AY = 0.0, 49.2                           # VoiceS3R centre, USB-C / PORT.A edge to +y
HOLES = [(-9.0, -26.0), (9.0, -26.0), (-9.0, 9.0), (9.0, 9.0), (0.0, 54.2), (-13.8, -18.0), (13.5, -47.5)]
VEIN_H = (1, 2, 3, 4)                        # the vein module's spacers; the others hold the board only
J3 = (-0.15, -34.5)                          # opening -y, under the vein socket
J6 = (BX0 + 4.45 + 2.3, -45.0)               # Grove (NFC), opening -x: its footprint's front 2.3 inside the edge
U1 = (-8.0, 26.0)                            # MAX3232, turned (along x)
SW1 = (8.0, 26.0)                            # DIP, turned (along x), reached with the cover off
J1X, J2X = AX - 7.62, AX + 7.62              # Ext.Pin rows (J1 5 pins from AY - 2.54, J2 4 pins from AY, both to +y)

ZB = 3.0                                     # M3 × 3 spacers on the floor
ZBT = ZB + 1.6
SP_VEIN, TAPE = 5.0, 0.7
VEIN = (-13.0, 13.0, -38.0, 21.0)            # 26 across, 59 along y, the socket end at -y (the cable loops before the DB9)
VEIN_Z0 = ZBT + SP_VEIN + TAPE               # 10.3, top 25.3
Z_ATOM = ZBT + 2.5                           # VoiceS3R bottom (header plastic 2.5), top 23.9

pcb = box(BX0, BX1, BY0, BY1, ZB, ZBT)
for x, y in HOLES:
    pcb = pcb.cut(cyl_z(x, y, 1.6, ZB - 1, ZBT + 1))


def on(x0, x1, y0, y1, z0, z1):
    """Box on the board, z from the board's top face."""
    return box(x0, x1, y0, y1, ZBT + z0, ZBT + z1)


def cyl_x(x0, x1, y, z, r):
    return cq.Workplane('YZ').workplane(offset=x0).center(y, z).circle(r).extrude(x1 - x0)


# DB9 male RA on the -y edge, mating face -y, centred (as build_station_pf.py, from the KiCad footprint)
db9_body = on(-15.0, 15.0, BY0 + 0.5, BY0 + 10.5, 0, 12.5)
db9_flange = on(-15.4, 15.4, BY0 - 1.0, BY0, 0, 12.5)
db9_shell = on(-8.5, 8.5, BY0 - 7.0, BY0 - 1.0, 2.0, 10.5)
db9_tails = on(-6.5, 6.5, BY0 + 3.0, BY0 + 8.5, -4.6, -1.6)
DB9_ZC = ZBT + 6.25
db9_posts = cyl_y(-12.5, BY0 - 5.0, BY0 - 1.0, DB9_ZC, 2.5).union(cyl_y(12.5, BY0 - 5.0, BY0 - 1.0, DB9_ZC, 2.5))
db9_plug = box(-15.15, 15.15, -100, BY0 - 1.8, ZBT - 0.75, ZBT + 13.25)   # stops 0.8 short of the flange

j3 = on(J3[0] - 5.0, J3[0] + 5.0, J3[1] - 3.1, J3[1] + 3.7, 0, 3.4)
j3_plug = on(J3[0] - 3.0, J3[0] + 3.0, J3[1] - 9.1, J3[1] - 3.1, 0.3, 3.1)
# the vein cable (MX1.25 9P -> 4P, approx a 3 × 1 bundle): level out of the module's socket at the -y end, a loop down
# in front of it (between the vein module and the DB9), back into J3's plug from -y
VCX = (J3[0] - 1.5, J3[0] + 1.5)
YS, YP, YL = VEIN[2], J3[1] - 9.1, J3[1] - 11.0              # socket face, plug's back, the loop's far side
ZS, ZP = VEIN_Z0 + 3.2, ZBT + 1.7
vein_cable = (box(*VCX, YL, YS, ZS - 0.5, ZS + 0.5).union(box(*VCX, YL - 1.0, YL, ZP - 0.5, ZS + 0.5))
              .union(box(*VCX, YL - 1.0, YP, ZP - 0.5, ZP + 0.5)))
u1 = on(U1[0] - 4.95, U1[0] + 4.95, U1[1] - 1.95, U1[1] + 1.95, 0, 1.75)
caps = on(-14.0, -2.0, 19.6, 21.0, 0, 0.9).union(on(-9.5, -6.5, 31.1, 32.5, 0, 0.9))
sw1 = on(SW1[0] - 5.86, SW1[0] + 5.86, SW1[1] - 3.35, SW1[1] + 3.35, 0, 3.0)

# Ext.Pin headers (plastic 2.54 × 2.5, pins up 6 into the VoiceS3R, tails 3 under the board)
hdr_plastic = on(J1X - 1.27, J1X + 1.27, AY - 3.81, AY + 8.89, 0, 2.5).union(
    on(J2X - 1.27, J2X + 1.27, AY - 1.27, AY + 8.89, 0, 2.5))
hdr_pins = on(J1X - 0.32, J1X + 0.32, AY - 2.86, AY + 7.94, -4.6, 8.5).union(
    on(J2X - 0.32, J2X + 0.32, AY - 0.32, AY + 7.94, -4.6, 8.5))
atom = rbox(AX - 12, AX + 12, AY - 12, AY + 12, Z_ATOM, Z_ATOM + 16.8, 3.0)
YF = AY + 12                                                # the USB-C / PORT.A face
usb_plug = box(AX - 6, AX + 6, YF + 6.5, YF + 24.2, Z_ATOM + 4.0, Z_ATOM + 11.0).union(
    box(AX - 4.2, AX + 4.2, YF, YF + 6.5, Z_ATOM + 6.0, Z_ATOM + 9.0))
porta_plug = box(AX - 4.9, AX + 4.9, YF, YF + 10.2, Z_ATOM + 0.0, Z_ATOM + 4.0)   # PORT.A (spare) under the USB-C
# J6: JLC's HY2.0 body runs ~2.1 further out than the footprint's (the vein unit board's measurement); JLC's assembly
# preview shows its front ~0.5 past the board edge, so take 0.6 (into the wall; the Grove cut takes the whole body)
GF = BX0 - 0.6                                              # its front, 0.6 outside the board edge
grove = on(GF, J6[0] + 3.25, J6[1] - 6.0, J6[1] + 6.0, 0, 6.0)
grove_plug = on(GF - 8.1, GF, J6[1] - 4.5, J6[1] + 4.5, 0.6, 5.4)

# spacers: M3 × 3 (hex 5.5 as r 3.2) on the floor under every hole; over H1..H4 an M3 × 5 for the vein module (its
# top taped to the module), over the others a pan head screw (r 2.8 × 2; H5's is under the VoiceS3R, 0.5 clear)
spacers = None
for i, (x, y) in enumerate(HOLES, 1):
    parts = [cyl_z(x, y, 3.2, 0, ZB)]
    parts.append(cyl_z(x, y, 3.2, ZBT, ZBT + SP_VEIN) if i in VEIN_H else cyl_z(x, y, 2.8, ZBT, ZBT + 2.0))
    for s in parts:
        spacers = s if spacers is None else spacers.union(s)

vein = rbox(*VEIN, VEIN_Z0, VEIN_Z0 + 15.0, 2.0)

# ---- machining ---------------------------------------------------------------------------------------------
VEIN_WIN = (VEIN[0] - 0.2, VEIN[1] + 0.2, VEIN[2] - 0.2, VEIN[3] + 0.2, 2.2)
ATOM_WIN = (AX - 12.2, AX + 12.2, AY - 12.2, AY + 12.2, 3.2)
cover_cut = rbox(*VEIN_WIN[:4], CEIL - 1, TOP + 1, VEIN_WIN[4]).union(rbox(*ATOM_WIN[:4], SKIRT, TOP + 1, ATOM_WIN[4]))
SKIRT_FILE = box(-16.0, 16.0, IN[2] - 0.5, SK[2] + 0.2, SKIRT - 0.1, SKIRT + 0.8)   # the skirt filed back over the DB9
# wall cut-outs as (along the wall 0, 1, z0, z1, R) in case coords: x on the ends, y on the +x side
DB9_CUT = (-15.65, 15.65, ZBT - 1.5, CEIL, 0)                                            # DB9 hood (-y), open to the top
USB_CUT = (AX - 5.3, AX + 5.3, Z_ATOM - 0.4, SKIRT, 0)                                    # USB-C over PORT.A (+y), open to the top
GROVE_CUT = (J6[1] - 6.3, J6[1] + 6.3, ZBT - 0.3, ZBT + 6.4, 0.5)                          # Grove body 12 × 6 (-x)
# the reset: a U-shaped flap on the face left of the ports (official STL: 1.5..6.5 from the centre away from the
# ports, 1.4..8.4 up), on the +x face here (the VoiceS3R turned half a turn); the hole takes a screwdriver
RESET_CUT = (AY - 7.0, AY - 1.0, Z_ATOM + 1.0, Z_ATOM + 9.0, 1.0)                        # the reset (+x)
wall_cut = (box(*DB9_CUT[:2], OUT[2] - 1, BY0 - 0.5, *DB9_CUT[2:4])
            .union(box(*USB_CUT[:2], YF + 0.5, OUT[3] + 1, *USB_CUT[2:4])))
wall_cut = wall_cut.union(rbox(AX + 12.5, OUT[1] + 1, *RESET_CUT)).union(rbox(OUT[0] - 1, IN[0] + 0.2, *GROVE_CUT))
case = body.cut(cover_cut).cut(SKIRT_FILE).cut(wall_cut)

# ---- interference ------------------------------------------------------------------------------------------
checks = [('指静脈', vein), ('vein cable', vein_cable), ('board', pcb), ('J3', j3), ('J3 plug', j3_plug), ('MAX3232', u1),
          ('caps', caps), ('SW1', sw1), ('DB9 body', db9_body), ('DB9 flange', db9_flange), ('DB9 shell', db9_shell),
          ('DB9 posts', db9_posts), ('DB9 tails', db9_tails), ('spacers', spacers), ('DB9 plug', db9_plug),
          ('headers', hdr_plastic.union(hdr_pins)), ('VoiceS3R', atom), ('USB plug', usb_plug), ('Grove', grove),
          ('Grove plug', grove_plug), ('PORT.A plug', porta_plug)]
bad = []
for name, obj in checks:
    v = case.intersect(obj).val().Volume()
    print(f'interference case x {name:14s} = {v:.3f} mm3')
    if v > 0.01:
        bad.append(f'case/{name}')
mutual = [('指静脈', vein), ('vein cable', vein_cable), ('spacers', spacers), ('J3 plug', j3_plug), ('MAX3232', u1),
          ('caps', caps), ('SW1', sw1), ('DB9 body', db9_body), ('DB9 tails', db9_tails), ('DB9 plug', db9_plug),
          ('header plastic', hdr_plastic), ('VoiceS3R', atom), ('USB plug', usb_plug), ('Grove', grove),
          ('Grove plug', grove_plug), ('PORT.A plug', porta_plug)]
for i, (na, a) in enumerate(mutual):
    for nb, b in mutual[i + 1:]:
        v = a.intersect(b).val().Volume()
        if v > 0.01:
            print(f'interference {na} x {nb} = {v:.3f} mm3')
            bad.append(f'{na}/{nb}')
print('parts among themselves: ' + ('ok' if not any(not b.startswith('case/') for b in bad) else 'NG'))

# ---- hole drawings and the 1:1 template (each face seen from outside) --------------------------------------------
# Faces in their own 2D coords: the cover as the case's x, y (seen from above); the walls with the height h = z - FLOOR
# (0 = the floor's outside face, 25 = the cover's top face) and along the wall as seen from outside: y on the +x side
# (+y to the right), x on the -y end (+x to the right), -x on the +y end (+x to the left). The wall holes are
# dimensioned from the bottom-left corner (what a ruler starts from), the cover's from the case centre.
H = TOP - FLOOR
COVER = (*OUT, 3.0)
SIDE_FACE = (OUT[2], OUT[3], 0, H, 0)
END_FACE = (OUT[0], OUT[1], 0, H, 0)
cover_cuts = [('vein', ('rect', *VEIN_WIN)), ('VoiceS3R', ('rect', *ATOM_WIN))]
side_cuts = [('reset', ('rect', *RESET_CUT[:2], RESET_CUT[2] - FLOOR, RESET_CUT[3] - FLOOR, RESET_CUT[4]))]
nfc_cuts = [('NFC', ('rect', -GROVE_CUT[1], -GROVE_CUT[0], GROVE_CUT[2] - FLOOR, GROVE_CUT[3] - FLOOR, GROVE_CUT[4]))]
end_db9_cuts = [('DB9', ('rect', *DB9_CUT[:2], DB9_CUT[2] - FLOOR, DB9_CUT[3] - FLOOR, DB9_CUT[4]))]
end_usb_cuts = [('USB / PORT.A', ('rect', -USB_CUT[1], -USB_CUT[0], USB_CUT[2] - FLOOR, USB_CUT[3] - FLOOR, USB_CUT[4]))]
SIDE_NAMES, END_NAMES = ('-y end', '+y end', 'bottom', 'top'), ('left', 'right', 'bottom', 'top')
BOTTOM = ('bottom edge = the floor\'s outside face (z -2.5), top edge = the cover\'s top (z 22.5)', (0, -29))
out = os.path.join(ROOT, 'station')


def size(c):
    return f'{c[2] - c[1]:.1f} x {c[4] - c[3]:.1f}' + (f', 4-R{c[5]:g}' if c[5] else ', square corners')


def draw_cover(msp):
    face(msp, COVER, [dict(cut=cover_cuts[0][1], at=(VEIN_WIN[0] + 1.5, 10), hdim=VEIN_WIN[0] - 4,
                           text=('vein window, through', size(cover_cuts[0][1]))),
                      dict(cut=cover_cuts[1][1], at=(ATOM_WIN[0] + 1.5, AY + 4), hdim=ATOM_WIN[0] - 4,
                           text=('VoiceS3R window, through', size(cover_cuts[1][1])))],
         titles=[('+y END (VoiceS3R, USB-C / PORT.A)', (0, OUT[3] + 16)), ('-y END (DB9)', (0, OUT[2] - 36))])


def wall_sheet(outline, cuts, title):
    def draw(msp):
        face(msp, outline, [dict(cut=c, at=(c[1] + 1.0, c[4] - 3.5), wdim=H + 3, text=(f'{n}, through', size(c)))
                            for n, c in cuts], titles=[(title, (0, -24)), BOTTOM], datum=(outline[0], 0))
    return draw


def wall_view(outline, cuts, at, label, left, right):
    x0, x1, _, h, _ = outline
    g = dict(color='0.6', lw=0.3)
    small = [(n, c) for n, c in cuts if c[2] - c[1] <= 12]      # labelled under the hole, big ones inside
    return dict(outline=outline, at=at, holes=[c if (n, c) in small else (*c, n) for n, c in cuts],
                lines=[([x, x], [0, h], dict(g, ls='--')) for x in (x0 + COVER[4], x1 - COVER[4])] +
                      [([(x0 + x1) / 2] * 2, [-2, h + 2], dict(g, ls='-.'))],
                text=[(x0, h + 3, label, dict(fs=7, weight='bold')),
                      (x0 - 1.5, h / 2, left, dict(ha='right', va='center', fs=6, color='0.4')),
                      (x1 + 1.5, h / 2, right, dict(ha='left', va='center', fs=6, color='0.4')),
                      ((x0 + x1) / 2, -3.5, 'BOTTOM (desk side)', dict(ha='center', fs=6, weight='bold'))] +
                     [((c[1] + c[2]) / 2, c[3] - 2.8, n, dict(ha='center', fs=5.5, color='#d0021b')) for n, c in small])


def template():
    x0, x1, y0, y1, _ = COVER
    g = dict(color='0.6', lw=0.3, ls='-.')
    b = dict(ha='center', fs=7, weight='bold')
    cover = dict(outline=COVER, at=(-75, -12), holes=[('rect', *VEIN_WIN, 'vein'), ('rect', *ATOM_WIN, 'VoiceS3R')],
                 lines=[([x0 + 4, x1 - 4], [0, 0], g), ([0, 0], [y0 + 4, y1 - 4], g)],
                 text=[(x0, y1 + 3, 'COVER, from above', dict(fs=8, weight='bold')),
                       (0, y0 - 5.5, '-y END (DB9)', b), (x1 + 2, AY, '+x SIDE\n(reset)', dict(ha='left', va='center', fs=6.5))])
    side = wall_view(SIDE_FACE, side_cuts, (22, 27), '+x SIDE (reset), seen from outside', '-y', '+y')
    side_nfc = wall_view(SIDE_FACE, nfc_cuts, (22, -9), '-x SIDE (NFC), seen from outside', '+y', '-y')
    end_db9 = wall_view(END_FACE, end_db9_cuts, (-5, -45), '-y END (DB9), from outside', '-x', '+x')
    end_usb = wall_view(END_FACE, end_usb_cuts, (55, -45), '+y END (USB-C / PORT.A), from outside', '+x', '-x')
    rows = ([edge_row(n, c, COVER, ('-x', '+x', '-y', '+y')) for n, c in cover_cuts] + [''] +
            [edge_row(n, c, SIDE_FACE, SIDE_NAMES) for n, c in side_cuts] +
            [edge_row(n, c, SIDE_FACE, ('+y end', '-y end', 'bottom', 'top')) for n, c in nfc_cuts] +
            [edge_row(n, c, END_FACE, ('-x side', '+x side', 'bottom', 'top')) for n, c in end_db9_cuts] +
            [edge_row(n, c, END_FACE, ('+x side', '-x side', 'bottom', 'top')) for n, c in end_usb_cuts])
    notes = [f'Vein Station {REV} - Takachi SW-130B cutting template, 1:1 (cover, both sides, both ends, from outside)',
             'PRINT AT 100% / ACTUAL SIZE (no "fit to page", no scaling).',
             'Cut the views apart. Cover: face up on the cover, grey outline (40 x 130, R3) on the cover edges.',
             'Side / ends: the grey line is the whole case (cover on, 25 high): its BOTTOM edge on the desk side of the body,',
             'its ends on the case ends. All wall cuts are in the body; the DB9 and USB cuts are open to the body\'s top edge.',
             'Also file the cover\'s skirt back 0.8 over the DB9 (32 wide, at the -y end).',
             'Red = cut through; + = corner drill centres. Unit mm.',
             'Distances: cover from the outline edges; side / ends from the ends, the bottom (floor outside) and the top.',
             ''] + rows
    return cut_template(os.path.join(out, f'vein_station_{REV}_template_1to1.pdf'), 60,
                        [cover, side, side_nfc, end_db9, end_usb], -64, -92, notes, rows)


dxf = {}
for name, title, notes, draw, x0, y0 in (
        ('cover', 'SW-130B cover - seen from OUTSIDE (above), origin = case centre, +y = the VoiceS3R end',
         ['CUT: vein window and VoiceS3R window (corner R as dimensioned), through',
          'dimensions: centres from the case centre, sizes', 'file the skirt back 0.8 over the DB9 (-y end, 32 wide)',
          'unit mm'], draw_cover, OUT[0], OUT[2] - 44),
        ('side', 'SW-130B body, +x side - seen from OUTSIDE, datum = bottom left (-y end, floor outside)',
         ['CUT: the reset hole (a screwdriver to the VoiceS3R\'s reset), through',
          'heights from the bottom (the floor\'s outside face)', 'unit mm'],
         wall_sheet(SIDE_FACE, side_cuts, '+x SIDE seen from outside: -y (DB9) end left, +y end right'),
         SIDE_FACE[0], -36),
        ('side_nfc', 'SW-130B body, -x side - seen from OUTSIDE, datum = bottom left (+y end, floor outside)',
         [f'CUT: the Grove (NFC) socket body and plug, R{GROVE_CUT[4]:g}, through', 'heights from the bottom (the floor\'s outside face)', 'unit mm'],
         wall_sheet(SIDE_FACE, nfc_cuts, '-x SIDE seen from outside: +y (USB) end left, -y (DB9) end right'),
         SIDE_FACE[0], -36),
        ('end_db9', 'SW-130B body, -y end - seen from OUTSIDE, datum = bottom left (-x side, floor outside)',
         ['CUT: DB9 hood (square corners), open to the top of the body', 'heights from the bottom', 'unit mm'],
         wall_sheet(END_FACE, end_db9_cuts, '-y END seen from outside: -x left, +x right'), END_FACE[0], -36),
        ('end_usb', 'SW-130B body, +y end - seen from OUTSIDE, datum = bottom left (+x side, floor outside)',
         ['CUT: USB-C over PORT.A (square corners), open to the top of the body', 'heights from the bottom', 'unit mm'],
         wall_sheet(END_FACE, end_usb_cuts, '+y END seen from outside: +x left, -x right'), END_FACE[0], -36)):
    dxf[name] = sheet(os.path.join(out, f'vein_station_{REV}_{name}.dxf'), title, notes, draw, x0, y0)
downloads = [('型紙(PDF、A4 原寸 — 拡大縮小なしで印刷。カバー・両側面・両端面)', template())]
for name, label in (('cover', 'カバー'), ('side', '+x 側面(リセット)'), ('side_nfc', '−x 側面(NFC の Grove)'),
                    ('end_db9', '−y 端面(DB9)'), ('end_usb', '+y 端面(USB-C / PORT.A)')):
    downloads += [(f'加工図 {label}(DXF、寸法入り)', dxf[name][0]), (f'加工図 {label}(PDF、DXF と同じ図)', dxf[name][1])]

# ---- 3D preview ------------------------------------------------------------------------------------------
cover = case.intersect(box(-21, 21, -66, 66, SKIRT, TOP + 1))
shell = case.intersect(box(-21, 21, -66, 66, FLOOR - 1, SKIRT))
NFC_X, NFC_Y = BX0 - 38.0, J6[1]              # the Unit NFC on the desk beside the -x side, by J6
parts = [
    ('shell', 'カバー(タカチ SW-130B、指静脈・VoiceS3R の窓)', '#2b2f33', 0.45, 'shell', cover),
    ('atom', 'VoiceS3R(公式 CAD、ケースの中で基板に立つ。USB-C / PORT.A は +y、リセットは +x)', '#1fa49a', 1, 'mods',
     stl_at('voice', AX, AY, Z_ATOM, TOP, turn=True)),                     # CAD z 0..16.8
    ('nfc', 'NFC Unit(公式 CAD、机の上。Grove ケーブルで −x 側面の J6 へ)', '#f2f2ee', 1, 'mods',
     stl_at('nfc', NFC_X, NFC_Y, FLOOR + 2.8, TOP)),   # CAD z -2.8..5.2
] + vein_parts(VEIN, VEIN_Z0, along_y=True) + [
    ('pcb', 'station 基板 sw130(34.8 × 122.7、片面実装)', '#1f7a4d', 1, 'mods', pcb),
    ('hdr', 'J1 / J2 ピンヘッダー(VoiceS3R の Ext.Pin)', '#2b2f33', 1, 'mods', hdr_plastic.union(hdr_pins)),
    ('j3', 'J3 MX1.25 4P(指静脈)', '#f1efe8', 1, 'mods', j3),
    ('j3plug', 'J3 プラグ(指静脈ケーブル)', '#e7e1cf', 1, 'mods', j3_plug),
    ('veincable', '指静脈のケーブル(DB9 との間で折り返す、おおよその通り道)', '#b04a2f', 1, 'mods', vein_cable),
    ('u1', 'U1 MAX3232 と C1〜C5', '#202326', 1, 'mods', u1.union(caps)),
    ('sw1', 'SW1 ストレート / クロス DIP(カバーを外して切り替え)', '#c0392b', 1, 'mods', sw1),
    ('db9', 'J4 DB9 オス(−y の端面)', '#8a8f96', 1, 'mods', db9_body.union(db9_flange).union(db9_shell).union(db9_posts)),
    ('spacers', 'M3 × 3(床に VHB)と M3 × 5(指静脈、上面に VHB)', '#c9a227', 1, 'mods', spacers),
    ('db9plug', 'DB9 プラグ(FC-1200 へ)', '#5c6166', 1, 'mods', db9_plug),
    ('usbplug', 'USB-C プラグ(Windows PC へ)', '#24292d', 1, 'mods', usb_plug),
    ('portaplug', 'PORT.A Grove プラグ(予備、USB-C の下)', '#c47f0e', 1, 'mods', porta_plug),
    ('grove', 'J6 Grove(NFC、G38 / G39、−x の側面)', '#f1efe8', 1, 'mods', grove),
    ('groveplug', 'Grove プラグ(NFC へ)', '#c47f0e', 1, 'mods', grove_plug),
    ('lid', 'ボディ(タカチ SW-130B、端面に DB9 と USB-C / PORT.A、−x の側面に NFC、+x の側面にリセットの穴)', '#8fa09c', 0.9, 'lid', shell),
]
SUB = ('細い案: タカチ SW-130B(40 × 25 × 130)に、DB9・指静脈・VoiceS3R を一列に全部入れる版(片面実装、NFC は '
       '−x 側面の Grove、USB-C と PORT.A は +y の端面)。ドラッグで回転、ホイール/ピンチで拡大。')
DIMS = [('ケース', 'タカチ SW-130B(40 × 25 × 130、ABS、はめ込み式、¥360)'),
        ('内側', '35.5 × 125.5、高さ 17(その上 20 まではカバーの縁で 32.8 × 122.8)。ボス・リブなし'),
        ('基板', 'station 基板 sw130(34.8 × 122.7)、部品は全部上面。床に VHB で貼った M3 × 3 の上(3.0)'),
        ('VoiceS3R', '基板に Ext.Pin(J1 / J2、普通のピンヘッダー)で立てる。カバーの窓から 1.4 出る。USB-C とその下の PORT.A(予備)は +y の端面の 1 つの穴から、リセットは +x の側面の穴からドライバーで'),
        ('NFC', '基板の Grove J6(−x の側面、DB9 の近く)。G38 = SDA / G39 = SCL(4.7k プルアップ)、ファームで I2C をこのピンで開く'),
        ('指静脈', 'M3 × 5 の上に VHB 0.7、カバーから 2.8 突き出す。J3 はその下、ケーブルは DB9 との間で折り返す'),
        ('DB9', '−y の端面(切り欠きはボディの上縁まで開いていて、基板を上から落とし込む)。カバーの縁をその上だけ 0.8 削る'),
        ('加工', 'カバーに窓 2 つ、−y 端面に DB9、+y 端面に USB-C / PORT.A(1 つの穴)、−x 側面に NFC の Grove、+x 側面にリセットの穴 6 × 8')]
NOTE = ('ケースはタカチの外形図(SW-130□)からの簡略形状です。VoiceS3R と NFC Unit の形は M5Stack 公式 STL'
        '(m5stack/M5_Hardware、Copyright (c) 2021 M5Stack、MIT License)、干渉チェックは VoiceS3R の外形の箱で行う。'
        'リセットボタンの位置は公式 STL から読んだ値。指静脈の外形は公式値(細部は写真からのイメージ)、基板上の部品は '
        'KiCad のフットプリント寸法からの簡略形状、指静脈のコネクタ位置は未確定。単位 mm。')
write_page('station-sw130', 'SW130 ' + REV, parts, SUB, DIMS, NOTE, TOP, downloads,
           '<p>試作は型紙を切り分けてカバー・ボディに貼り、手で開ける(角をドリル → 糸のこ/ピラニアソー → やすり)。'
           '側面・端面の高さはボディの底(床の外面)から測る。</p>')

if bad:
    raise SystemExit('interference: ' + ', '.join(bad))
