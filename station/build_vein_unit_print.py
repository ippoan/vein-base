"""Vein Unit P: the finger vein module (Waveshare Finger Vein Scanner Module (A)) alone in the smallest printed box
(MJF PA12) with one Grove cable to the VoiceS3R's PORT.A. The board u4 (pcb/vein_unit_board/build_board.py p) lies on
the floor's ribs under the module and carries J1 (MX1.25 4P vertical, the module's cable), U1 (5 V -> 3.3 V) with C1 /
C2, and the Grove J2 in the +x end, opening through the +x wall.
  - The module stands on the board and is held down by the lid: its top 2.0 is a 57 × 25 step, which goes through the
    lid's window (57.5 × 25.5); the 59 × 26 body under it bears on a 0.7 deep recess in the lid's underside
    (59.4 × 26.4), so the module's top is 0.5 proud of the lid. The board is pinned between the module and the ribs,
    the walls locate it sideways (no screws, no bosses).
  - The module's cable (the kit's MX1.25 9P -> 4P, ~10 cm, the 9P end re-pinned to 3..6), as the user wound it on the
    module (photos and measures, 2026-10-07): out of the 9P plug in the -x end face and bent round the -x end (2.0
    out of the end face, plug and wires), along the -y side face (2.0 out of it) to the groove across the module's
    bottom (18..28 from the 9P end, 2 deep), across in the groove (the module's bottom still sits flat), out of the +y
    side: 27 of wire from there to the 4P plug's root (31 to its tip), up, looped over J1 and down into it.
  - The lid: M2 x 5 countersunk tapping screws from the top into ledges on the walls (station/shapes.py).
Writes site/vein-unit-print/ and station/vein_station_print_unit_{body,lid}.stl, fails on any interference.
Run from the repository root:  python3 station/build_vein_unit_print.py
Coordinates = the board's: x along the module (the 9P end at -x, the Grove at +x), y across (J1 on +y), z = 0 on
the floor's inside face."""
import os
import cadquery as cq
from shapes import (ROOT, box, rbox, union, vein_parts, vein_step_box, write_page, shell_and_lid, check, T_WALL,
                    T_FLOOR, T_TOP, LEDGE_D, LEDGE_W, LEDGE_H, RIB_W, RIB_PITCH, RIB_FLOOR, RIB_LID, VEIN_GROOVE)

REV = 'vp1'
# ---- shared with pcb/vein_unit_board/build_board.py p (u4): the outline, J1 and J2. Keep the two together ------------
VEIN = (-29.5, 29.5, -13.0, 13.0)        # the module, the 9P end at -x
BRD = (-31.5, 39.8, -15.0, 19.6)         # the board u4 (x0, x1, y0, y1), corners R1.0
J1 = (-6.5, 16.0)                        # MX1.25 4P vertical (53398-0471), footprint origin, turned 180 (pads to -y)
J2 = (34.4, 0.0)                         # Grove (JST S4B-PH-SM4-TB), footprint origin, turned 90 (opening +x)
U1 = (8.0, 16.4)                         # LDO (SOT-23), C1 / C2 3.0 either side on x
# ----------------------------------------------------------------------------------------------------------------------
GAP = 0.3                                # the board / the module / the cable to the walls
# the module's cable out of its outline (measured 2026-10-07): the 9P plug with the wires bent round the -x end
# CABLE_END out of the end face, the wires along the -y side face CABLE_SIDE ("a little under 2 mm"), and from the +y
# side 27 of wire to the 4P plug's root (31 to its tip)
CABLE_END = 2.0
CABLE_SIDE = 2.0
CABLE_TO_J1 = 27.0
# END_EXTRA: the -x end longer than the cable needs, for lid screw ledges in the -x corners (a countersink stays 1.0 off
# the lid's recess, so that takes 2.9): 0 = the smallest box, three ledges
END_EXTRA = 0.0
assert abs(BRD[0] - (VEIN[0] - CABLE_END - END_EXTRA)) < 1e-9 and abs(BRD[2] - (VEIN[2] - CABLE_SIDE)) < 1e-9, 'BRD against the cable'
xi0, xi1, yi0, yi1 = BRD[0] - GAP, BRD[1] + GAP, BRD[2] - GAP, BRD[3] + GAP
ZB = RIB_FLOOR                           # the board on the floor's ribs
ZBT = ZB + 1.6
VZ0 = ZBT                                # the module straight on the board
RECESS = 0.7                             # the lid's recess for the module's body
Z_IN = VZ0 + 15.0 - 2.0 - RECESS         # the module's step face bears on the recess's floor
Z_TOP = Z_IN + T_TOP                     # the module's top 0.5 over it
x0 = VEIN[0]
g0, g1 = x0 + VEIN_GROOVE[0], x0 + VEIN_GROOVE[1]
assert J2[0] - 4.6 >= VEIN[1] + 0.3 - 1e-9, 'J2 against the module'
assert g0 < J1[0] - 3.375 and J1[0] + 3.375 < g1, 'J1 beside the groove'

vein = vein_step_box(VEIN, VZ0)
board = rbox(*BRD, ZB, ZBT, 1.0)
# J1 with its 4P plug in it: the housing ±3.375 and the fitting nails ±5.075 (KiCad's footprint, Fab), y -1.1..2.6
# turned (the pads on the module's side), up to the mated height 5.7 (Molex PicoBlade 53398)
j1 = box(J1[0] - 5.075, J1[0] + 5.075, J1[1] - 1.1, J1[1] + 2.6, ZBT, ZBT + 5.7)
# the Grove: JST PH S4B-PH-SM4-TB (Fab -3.2..4.4 front, ±5.95 across, 6 high), the plug through the +x wall
grove = box(J2[0] - 3.2, J2[0] + 4.4, J2[1] - 6.0, J2[1] + 6.0, ZBT, ZBT + 6.0)
grove_plug = box(J2[0] + 4.4, xi1 + T_WALL + 8.0, J2[1] - 4.5, J2[1] + 4.5, ZBT + 0.6, ZBT + 5.4)
ldo = box(U1[0] - 4.0, U1[0] + 4.0, U1[1] - 2.0, U1[1] + 2.0, ZBT, ZBT + 1.2)        # U1 + C1 / C2
# the module's 9P plug (14.4 wide as station/build_vein_unit.py, low in the end face) with the wires bent round the
# -x end (one envelope, CABLE_END out) and the 4-wire cable (a ribbon 4.2 high on edge along the -y side): along the -y
# side face to the groove, across in it, out of the +y side, up, a loop over J1 (CABLE_TO_J1 of wire: up to ARCH, over,
# down into the plug's top 5.7) and down into it
Z_P = VZ0 + 1.5
YC = (VEIN[2] + VEIN[3]) / 2
ys0 = VEIN[2] - CABLE_SIDE                               # the run along the -y side face
yc0, yc1 = VEIN[3] + 0.2, VEIN[3] + 1.6                # the riser on the +y side
ARCH = ZBT + 10.6
LOOP_X = 6.5                                            # the loop over J1, ± from its centre
# up from the groove (1.0) to ARCH, across to the plug's middle, down to its top, the rest looped over J1 sideways
loop = CABLE_TO_J1 - ((ARCH - ZBT - 1.0) + (J1[1] + 0.75 - VEIN[3]) + (ARCH - ZBT - 5.7))
assert 0 < loop < 2 * 2 * (LOOP_X - 3.375) + 2 * (BRD[3] - J1[1] - 0.75), 'the cable to J1 does not fit the loop'
plug9 = rbox(x0 - CABLE_END, x0, ys0, YC + 7.2, ZBT, Z_P + 3.5, 0.6)       # rounded round the corner
assert yc1 + 0.3 <= J1[1] - 1.1, 'the cable against J1'
cable_runs = (box(x0, g1 - 0.2, ys0, VEIN[2], ZBT, ZBT + 4.2),
              box(g0 + 0.2, g1 - 0.2, ys0, yc1, ZBT, ZBT + VEIN_GROOVE[2] - 0.1),
              box(J1[0] - 3.375, J1[0] + 3.375, yc0, yc1, ZBT, ARCH),
              box(J1[0] - LOOP_X, J1[0] + LOOP_X, yc0, BRD[3], ZBT + 5.7, ARCH))
cable = union(*cable_runs)

wall_cuts = [box(xi1 - 1, xi1 + 5, J2[1] - 6.3, J2[1] + 6.3, ZBT - 0.3, ZBT + 6.4)]       # Grove (as GROVE_CUT, sw130)
win = (VEIN[0] + 0.75, VEIN[1] - 0.75, VEIN[2] + 0.25, VEIN[3] - 0.25)                   # 57.5 × 25.5
rec = (VEIN[0] - 0.2, VEIN[1] + 0.2, VEIN[2] - 0.2, VEIN[3] + 0.2)                       # 59.4 × 26.4
lid_cuts = [rbox(*win, Z_IN - 3, Z_TOP + 1, 1.75), rbox(*rec, Z_IN - 3, Z_IN + RECESS, 2.2)]
parts = [('vein', vein), ('board', board), ('J1 + 4P plug', j1), ('Grove J2', grove), ('Grove plug', grove_plug),
         ('LDO', ldo), ('9P plug + wires', plug9), ('cable', cable)]
tray, lid, size, screws = shell_and_lid(xi0, xi1, yi0, yi1, wall_cuts, lid_cuts, Z_IN, 
                                        keep_clear=[o for n, o in parts if n != 'cable'] + list(cable_runs))
bad = check((tray, lid), parts)
vol = (tray.val().Volume() + lid.val().Volume()) / 1000
print(REV, 'outer %.1f x %.1f x %.1f' % size, 'volume %.1f cm3' % vol, 'screws',
      [(round(float(x), 1), round(float(y), 1)) for x, y in screws], 'interference:', bad or 'none')
failed = [f'only {len(screws)} places for the lid screws'] if len(screws) < 3 else []
failed += bad

out = os.path.join(ROOT, 'station')
stls = []
for n, s, label in (('body', tray, '本体'), ('lid', lid, 'ふた')):
    p = os.path.join(out, f'vein_station_print_unit_{n}.stl')
    cq.exporters.export(s, p, tolerance=0.02, angularTolerance=0.1)
    stls.append((f'{label}の STL(MJF PA12 で造形)', p))
view = [('shell', f'ふた(窓 {win[1] - win[0]:.1f} × {win[3] - win[2]:.1f}、裏に深さ {RECESS:g} の座ぐり、M2 皿ねじで本体の受けに締める)',
         '#2b2f33', 0.45, 'shell', lid)] + vein_parts(VEIN, VZ0, step=True) + [
    ('board', '基板 u4(床のリブの上、指静脈で押さえる。build_board.py p)', '#1f7a4d', 1, 'mods', board),
    ('j1', 'J1 MX1.25 4P 縦型(53398-0471)と 4P プラグ。1:3V3 2:GND 3:RXD 4:TXD', '#f1efe8', 1, 'mods', j1),
    ('plug9', f'指静脈の MX1.25 9P プラグと −x 端を回る線(端面から {CABLE_END:g}、付属ケーブル④、3〜6 に差し替え)', '#e7e1cf', 1, 'mods', plug9),
    ('cable', '4 線のケーブル(−y の側面に沿い、底の溝を横切って +y から出て、J1 の上で輪にして上から挿す)', '#d9775c', 1, 'mods', cable),
    ('ldo', 'U1 LDO 5V → 3.3V と C1 / C2', '#202326', 1, 'mods', ldo),
    ('grove', 'J2 Grove(JST S4B-PH-SM4-TB、+x の端面)とプラグ(VoiceS3R の PORT.A へ)', '#c47f0e', 1, 'mods',
     grove.union(grove_plug)),
    ('lid', '本体(床・壁・リブ・ふたのねじの受け、MJF PA12 で造形)', '#8fa09c', 0.9, 'lid', tray)]
dims = [('外形', '%.1f × %.1f × %.1f(長さ × 幅 × 高さ、ふた込み)' % size), ('体積', '%.1f cm³(本体 + ふた)' % vol),
        ('肉厚', f'壁 {T_WALL}、床 {T_FLOOR}、天板 {T_TOP}(MJF PA12)'),
        ('リブ', f'反り止め。幅 {RIB_W:g} を約 {RIB_PITCH:g} おきの格子に、床(高さ {RIB_FLOOR:g}、基板が載る)とふたの裏(深さ {RIB_LID:g}、部品と窓を避ける)'),
        ('指静脈', f'基板にじかに載せ、ふたで押さえる。上の段(57 × 25、高さ 2.0)がふたの窓 {win[1] - win[0]:.1f} × {win[3] - win[2]:.1f} を通り、'
                 f'下の胴(59 × 26)がふたの裏の座ぐり(深さ {RECESS:g}、{rec[1] - rec[0]:.1f} × {rec[3] - rec[2]:.1f})に当たる。上面はふたから {VZ0 + 15.0 - Z_TOP:.1f} 出る'),
        ('基板', f'u4 {BRD[1] - BRD[0]:.1f} × {BRD[3] - BRD[2]:.1f}(R1.0)、床のリブ(高さ {RIB_FLOOR:g})の上で指静脈に押さえられ、横は壁で決まる。ねじなし。部品は上面だけ'),
        ('ケーブル', '付属ケーブル④(MX1.25 9P → 4P、約 10 cm、9P 側を 3〜6 に差し替え)。9P から −x 端を回り、'
                   f'指静脈の −y の側面に沿って(はみ出し {CABLE_SIDE:g})底の溝(9P の端から {VEIN_GROOVE[0]:g}〜{VEIN_GROOVE[1]:g}、深さ {VEIN_GROOVE[2]:g})を横切り、'
                   f'+y の溝の横から出て縦型 J1 に上から挿す(+y の辺から 4P の根元まで {CABLE_TO_J1:g}、余りは J1 の上で輪にする)。−x 端は 9P プラグと曲げた線で {CABLE_END:g}'),
        ('Grove', 'J2(+x の端面、穴 12.6 × 6.7)から VoiceS3R の PORT.A へ 1 本。1 白 = G2(← TXD)、2 黄 = G1(→ RXD)、3 = 5V、4 = GND'),
        ('ふた', f'M2 皿タッピングねじ × {len(screws)} 本(M2 × 5)で、上から壁の内側の受け({LEDGE_D:g} × {LEDGE_W:g}、高さ {LEDGE_H:g})に締める: '
                 + ', '.join(f'({x:.1f}, {y:.1f})' for x, y in screws)),
        ('干渉', 'なし' if not bad else ', '.join(bad))]
write_page('vein-unit-print', f'指静脈 Unit P {REV}', view,
           '指静脈モジュールだけを 3D 印刷(MJF PA12)の最小の箱に入れ、Grove 1 本で VoiceS3R の PORT.A に直接挿す案。'
           'ドラッグで回転、ホイール/ピンチで拡大。', dims,
           '指静脈の外形は公式値、上の段と底の溝は実測、細部は製品写真からのイメージ。部品は KiCad のフットプリント寸法と'
           'データシートからの簡略形状。単位 mm。', Z_TOP, stls, tz='-10')
if failed:
    raise SystemExit('interference: ' + ', '.join(failed))
