"""Vein Unit P: the finger vein module (Waveshare Finger Vein Scanner Module (A)) alone in the smallest printed box
(MJF PA12) with one Grove cable to the VoiceS3R's PORT.A. The board u4 (pcb/vein_unit_board/build_board.py p) lies on
the floor's ribs under the module and carries J1 (MX1.25 4P vertical, the module's cable) in the -x end just past the
module's 9P plug, U1 (5 V -> 3.3 V) with C1 / C2 beside the Grove J2 in the +x end, J2 opening through the +x wall.
  - The module stands on the board and is held down by the lid: its top 2.0 is a 57 × 25 step, which goes through the
    lid's window (57.5 × 25.5); the 59 × 26 body under it bears on a 0.7 deep recess in the lid's underside
    (59.4 × 26.4), so the module's top is 0.5 proud of the lid. The board is pinned between the module and the ribs,
    the walls locate it sideways (no screws, no bosses).
  - The module's cable (the kit's MX1.25 9P -> 4P, ~10 cm, the 9P end re-pinned to 3..6): the 9P plug with its wires
    bent round the -x end stands 2.0 out of the end face (measured 2026-10-07); the rest is folded along the long
    sides (a bundle 2.0 thick on each, as measured on -y) and may cross in the groove under the module (18..28 from
    the 9P end, 2 deep); the user winds it on the real module, so only the room is kept, not a route. It comes round
    the -x/+y corner and into J1 from above (the mated plug 5.7 high and room for the wires' bend over it).
  - The lid: M2 x 5 countersunk tapping screws from the top into ledges on the walls (station/shapes.py).
Writes site/vein-unit-print/ and station/vein_station_print_unit_{body,lid}.stl, fails on any interference.
Run from the repository root:  python3 station/build_vein_unit_print.py
Coordinates = the board's: x along the module (the 9P end and J1 at -x, the Grove at +x), y across, z = 0 on
the floor's inside face."""
import os
import cadquery as cq
from shapes import (ROOT, box, rbox, union, vein_parts, vein_step_box, write_page, shell_and_lid, check, T_WALL,
                    T_FLOOR, T_TOP, LEDGE_D, LEDGE_W, LEDGE_H, RIB_W, RIB_PITCH, RIB_FLOOR, RIB_LID, VEIN_GROOVE, ledge_notches,
                    way_in)

REV = 'vp3'
# ---- shared with pcb/vein_unit_board/build_board.py p (u4): the outline, J1 and J2. Keep the two together ------------
VEIN = (-29.5, 29.5, -13.0, 13.0)        # the module, the 9P end at -x
BRD = (-37.3, 39.8, -15.0, 15.0)         # the board u4 (x0, x1, y0, y1), less NOTCHES
# the board goes in from above past the lid screws' ledges (shapes.ledges, from the lid down to LEDGE_H): notched
# 0.3 round each, through to the board's edge where less than 2.0 would be left (checked against the ledges below)
NOTCHES = [(-37.3, -33.4, -15.0, -7.8), (35.9, 39.8, -15.0, -7.8), (-37.3, -30.1, 11.1, 15.0), (35.9, 39.8, 7.6, 15.0)]
J1 = (-33.7, 0.0)                        # MX1.25 4P vertical (53398-0471), footprint origin, turned 270 (pads to +x)
J2 = (34.4, 0.0)                         # Grove (JST S4B-PH-SM4-TB), footprint origin, turned 90 (opening +x)
U1 = (32.6, 10.5)                        # LDO (SOT-23) beside J2, clear of the +x/+y notch, C2 / C1 at y 7.8 / 13.3
# ----------------------------------------------------------------------------------------------------------------------
GAP = 0.3                                # the board / the module / the cable to the walls
# the module's cable out of its outline (measured 2026-10-07): the 9P plug with the wires bent round the -x end
# CABLE_END out of the end face; the cable folded along each long side CABLE_SIDE thick ("a little under 2 mm" on -y)
CABLE_END = 2.0
CABLE_SIDE = 2.0
J1_ROOM = 1.8                            # over J1's mated plug (5.7) for the wires' bend, under the lid ledges' bottoms
# J1 past the 9P plug: its pads (+x, 1.9 from the origin) 0.3 off the plug, its fitting nails' pads (-x, 3.0 from the
# origin) 0.6 inside the board's edge; the long sides CABLE_SIDE out of the module
assert abs(J1[0] - (VEIN[0] - CABLE_END - 0.3 - 1.9)) < 1e-9 and abs(BRD[0] - (J1[0] - 3.0 - 0.6)) < 1e-9, 'BRD / J1 against the plug'
assert abs(BRD[2] - (VEIN[2] - CABLE_SIDE)) < 1e-9 and abs(BRD[3] - (VEIN[3] + CABLE_SIDE)) < 1e-9, 'BRD against the cable'
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

vein = vein_step_box(VEIN, VZ0)
board = box(*BRD, ZB, ZBT)
for n in NOTCHES:
    board = board.cut(box(*n, ZB - 1, ZBT + 1))
# J1 with its 4P plug in it: the housing ±3.375 and the fitting nails ±5.075 across (KiCad's footprint, Fab), -1.1..2.6
# deep turned to x (the pads on the module's side), up to the mated height 5.7 (Molex PicoBlade 53398)
j1 = box(J1[0] - 2.6, J1[0] + 1.1, J1[1] - 5.075, J1[1] + 5.075, ZBT, ZBT + 5.7)
# the Grove: JST PH S4B-PH-SM4-TB (Fab -3.2..4.4 front, ±5.95 across, 6 high), the plug through the +x wall
grove = box(J2[0] - 3.2, J2[0] + 4.4, J2[1] - 6.0, J2[1] + 6.0, ZBT, ZBT + 6.0)
grove_plug = box(J2[0] + 4.4, xi1 + T_WALL + 8.0, J2[1] - 4.5, J2[1] + 4.5, ZBT + 0.6, ZBT + 5.4)
ldo = box(U1[0] - 2.0, U1[0] + 2.0, U1[1] - 3.3, U1[1] + 3.4, ZBT, ZBT + 1.2)        # U1 + C1 / C2
# the module's 9P plug (14.4 wide as station/build_vein_unit.py, low in the end face) with the wires bent round the
# -x end (one envelope, CABLE_END out); the cable folded along both long sides and across in the groove, round the
# -x/+y corner (past the 9P plug) and over J1 into its plug
Z_P = VZ0 + 1.5
YC = (VEIN[2] + VEIN[3]) / 2
ys0, ys1 = VEIN[2] - CABLE_SIDE, VEIN[3] + CABLE_SIDE
plug9 = rbox(x0 - CABLE_END, x0, ys0, YC + 7.2, ZBT, Z_P + 3.5, 0.6)       # rounded round the corner
xj1 = J1[0] + 1.1 + 0.3                                  # past J1's housing
cable_runs = (box(x0, VEIN[1], ys0, VEIN[2], ZBT, Z_IN - 0.3),          # folded along the sides, up to the lid
              box(x0, VEIN[1], VEIN[3], ys1, ZBT, Z_IN - 0.3),
              box(g0 + 0.2, g1 - 0.2, ys0, ys1, ZBT, ZBT + VEIN_GROOVE[2] - 0.1),
              rbox(xj1, x0, YC + 7.4, ys1, ZBT, ZBT + 5.7 + J1_ROOM, 0.6),  # round the -x/+y corner
              box(J1[0] - 2.6, xj1 + 0.01, J1[1] - 3.375, ys1, ZBT + 5.7, ZBT + 5.7 + J1_ROOM))   # over J1
cable = union(*cable_runs)

wall_cuts = [box(xi1 - 1, xi1 + 5, J2[1] - 6.3, J2[1] + 6.3, ZBT - 0.3, ZBT + 6.4)]       # Grove (as GROVE_CUT, sw130)
win = (VEIN[0] + 0.75, VEIN[1] - 0.75, VEIN[2] + 0.25, VEIN[3] - 0.25)                   # 57.5 × 25.5
rec = (VEIN[0] - 0.2, VEIN[1] + 0.2, VEIN[2] - 0.2, VEIN[3] + 0.2)                       # 59.4 × 26.4
lid_cuts = [rbox(*win, Z_IN - 3, Z_TOP + 1, 1.75), rbox(*rec, Z_IN - 3, Z_IN + RECESS, 2.2)]
parts = [('vein', vein), ('board', board), ('J1 + 4P plug', j1), ('Grove J2', grove), ('Grove plug', grove_plug),
         ('LDO', ldo), ('9P plug + wires', plug9), ('cable', cable)]
tray, lid, size, screws = shell_and_lid(xi0, xi1, yi0, yi1, wall_cuts, lid_cuts, Z_IN, 
                                        keep_clear=[o for n, o in parts if n != 'cable'] + list(cable_runs))
assert ZBT + 5.7 + J1_ROOM < Z_IN - LEDGE_H, 'the cable over J1 reaches the lid ledges'


# the way in from above: the board with its parts, then the module with its 9P plug, past the ledges (in xy). The
# notches are the ledges + 0.3, out to the board's edge where less than 2.0 would be left; the cable is laid by hand
want = ledge_notches(screws, (xi0, xi1, yi0, yi1), BRD, GAP)
assert want == sorted(NOTCHES), f'NOTCHES (here and in build_board.py p) should be {want}'
way_in(screws, (xi0, xi1, yi0, yi1), [('J1', j1), ('Grove J2', grove), ('LDO', ldo), ('vein', vein), ('9P plug', plug9)],
       board=board)
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
    ('j1', 'J1 MX1.25 4P 縦型(53398-0471)と 4P プラグ(−x 端、9P プラグの外側、上から挿す)。1:3V3 2:GND 3:RXD 4:TXD。ロックの窓(シルクの △ LOCK)は足の側(+x、指静脈の側)。プラグのロックの爪をそちらに向けて上から挿す', '#f1efe8', 1, 'mods', j1),
    ('plug9', f'指静脈の MX1.25 9P プラグと −x 端を回る線(端面から {CABLE_END:g}、付属ケーブル④、3〜6 に差し替え)', '#e7e1cf', 1, 'mods', plug9),
    ('cable', f'4 線のケーブルの置き場(両側面に厚さ {CABLE_SIDE:g} で折り返し、底の溝、−x/+y の角を回って J1 の上へ。巻き方は実物で合わせる)', '#d9775c', 1, 'mods', cable),
    ('ldo', 'U1 LDO 5V → 3.3V と C1 / C2(+x 端、J2 の横)', '#202326', 1, 'mods', ldo),
    ('grove', 'J2 Grove(JST S4B-PH-SM4-TB、+x の端面)とプラグ(VoiceS3R の PORT.A へ)', '#c47f0e', 1, 'mods',
     grove.union(grove_plug)),
    ('lid', '本体(床・壁・リブ・ふたのねじの受け、MJF PA12 で造形)', '#8fa09c', 0.9, 'lid', tray)]
dims = [('外形', '%.1f × %.1f × %.1f(長さ × 幅 × 高さ、ふた込み)' % size), ('体積', '%.1f cm³(本体 + ふた)' % vol),
        ('肉厚', f'壁 {T_WALL}、床 {T_FLOOR}、天板 {T_TOP}(MJF PA12)'),
        ('リブ', f'反り止め。幅 {RIB_W:g} を約 {RIB_PITCH:g} おきの格子に、床(高さ {RIB_FLOOR:g}、基板が載る)とふたの裏(深さ {RIB_LID:g}、部品と窓を避ける)'),
        ('指静脈', f'基板にじかに載せ、ふたで押さえる。上の段(57 × 25、高さ 2.0)がふたの窓 {win[1] - win[0]:.1f} × {win[3] - win[2]:.1f} を通り、'
                 f'下の胴(59 × 26)がふたの裏の座ぐり(深さ {RECESS:g}、{rec[1] - rec[0]:.1f} × {rec[3] - rec[2]:.1f})に当たる。上面はふたから {VZ0 + 15.0 - Z_TOP:.1f} 出る'),
        ('基板', f'u4 {BRD[1] - BRD[0]:.1f} × {BRD[3] - BRD[2]:.1f}(R1.0)、床のリブ(高さ {RIB_FLOOR:g})の上で指静脈に押さえられ、横は壁で決まる。ねじなし。部品は上面だけ'),
        ('ケーブル', '付属ケーブル④(MX1.25 9P → 4P、約 10 cm、9P 側を 3〜6 に差し替え)。−x 端は 9P プラグと曲げた線で '
                   f'{CABLE_END:g}。余りは指静脈の両側面に厚さ {CABLE_SIDE:g} で折り返し(底の溝 {VEIN_GROOVE[0]:g}〜{VEIN_GROOVE[1]:g}・深さ {VEIN_GROOVE[2]:g} も使える)、'
                   f'−x/+y の角を回って −x 端の縦型 J1 に上から挿す(挿したプラグ 5.7 の上に線の曲がり {J1_ROOM:g})。巻き方は実物で合わせる'),
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
