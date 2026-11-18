"""FP001S USB box: the Grow FP001S face / palm vein module and its USB board t2 (pcb/fp001s_test_board, 42 x 32) in
one printed box (MJF PA12), one USB-C cable to the PC like a USB camera.
  - The board lies on four floor bosses (M2 x 4 pan tapping screws from the top through H1..H4), J1 (USB-C) out
    through the back (-y) wall, J3 (SH 1.0 6P, opening +y) at the front edge.
  - The module stands in the front (+y) wall looking out, its axis along y, the round lens UP and the square window
    under it (manual 1.1: upside down it sees nothing, found 2026-11-18). Its front (dia 18.9, 1.8) fills the wall,
    the flange (dia 20.9, 1.0) bears on the wall's inside face, the rear (dia 18.8, 3.4) sits in a plate behind it.
    Wall and plate are U-shaped, open to the top: the module drops in from above with the lid off, and the lid
    carries the other halves (a tongue that fills the wall's slot over the module and the plate's top half), so
    closing the lid locks the module.
  - The SH cable (both ends SH, 1 -> 1; the module's own cable has loose wires) leaves J3 forwards under nothing and
    rises in the gap between the board's edge and the module's back to the module's socket.
  - The lid: M2 x 5 countersunk tapping screws from the top into ledges on the walls (station/shapes.py).
Writes site/fp001s-print/ and station/vein_station_print_fp001s_v<VERSION>_{body,lid}.stl, fails on any interference.
Run from the repository root:  python3 station/build_fp001s_print.py
Coordinates = the board's (pcb/fp001s_test_board/build_board.py: origin = the board's centre, J1 on the -y edge),
z = 0 on the floor's inside face."""
import os
import cadquery as cq
from shapes import (ROOT, VER, box, rbox, cyl_z, union, write_page, shell_and_lid, check, T_WALL, T_FLOOR, T_TOP,
                    LEDGE_D, LEDGE_W, LEDGE_H, RIB_W, RIB_PITCH, RIB_LID)

REV = 'fp1'
# ---- shared with pcb/fp001s_test_board/build_board.py (t2): outline, holes, part places. Keep the two together -------
BRD = (-21.0, 21.0, -16.0, 16.0)
HOLES = [(sx * 18.5, sy * 13.5) for sx in (-1, 1) for sy in (-1, 1)]
J1 = (-10.0, -12.95)                     # USB-C (HRO TYPE-C-31-M-12), footprint origin
J3 = (0.0, 12.6)                         # SH 1.0 6P horizontal (SM06B-SRSS-TB), turned 180, opening +y
U4 = (6.0, 3.5)                          # CH340C SOIC-16, turned 90 (long side along x)
U3, Y1 = (-8.0, 1.0), (-3.5, 1.0)        # CH334F QFN-24 4x4, 12 MHz 3225
U1, L1, C9 = (12.0, -3.5), (17.0, -3.0), (15.5, 6.0)   # SY8089 SOT-23-5, SWPA4020 4x4, 220 uF 3528
# ----------------------------------------------------------------------------------------------------------------------
GAP = 0.3
BOSS_D, BOSS_H, PILOT = 5.0, 2.5, 1.6    # M2 x 4 tapping: 1.6 board + 2.4 into the boss (2.5); the pilot from z -0.4, 1.2 of floor left
ZB = BOSS_H
ZBT = ZB + 1.6
# the module (Grow FP001S-White, manual 1.3.1): front dia 18.9 x 1.8, flange dia 20.9 x 1.0, rear dia 18.8 x 3.4
FP_FRONT, FP_FLANGE, FP_REAR = (18.9, 1.8), (20.9, 1.0), (18.8, 3.4)
FIT = 0.2                                # the holes / U's over the module's diameters (radius + FIT)
# J1's receptacle overhangs the board's -y edge (courtyard to -17.1): the back wall's inside 0.3 past its front
J1_FRONT = -16.85
USB_PLUG = (13.0, 7.4)                   # the plug's overmould through the back wall (w x h, rounded), from J1's face
# J3's mated plug and wires: out of the receptacle's front (+y) at the board's edge, the wires bend up at PLUG_END and
# rise to the module's socket in the gap before the module's back (CABLE_RISE deep)
PLUG_END, CABLE_RISE = 20.5, 1.8
xi0, xi1, yi0 = BRD[0] - GAP, BRD[1] + GAP, J1_FRONT - GAP
FP_BACK = PLUG_END + CABLE_RISE + 0.3    # the module's rear face
yi1 = FP_BACK + FP_REAR[1] + FP_FLANGE[1]        # the front wall's inside face = the flange's front
assert abs(FP_FRONT[1] - T_WALL) < 1e-9, "the module's front fills the wall"
ZC = round(FP_REAR[0] / 2 + FIT + 1.0, 2)       # the module's axis: 1.0 of the plate under its rear body
Z_IN = ZC + FP_FLANGE[0] / 2 + 0.8              # the lid's underside 0.8 over the flange
Z_TOP = Z_IN + T_TOP
PLATE = (FP_BACK + 1.0, yi1 - FP_FLANGE[1] - 0.05)   # the holder plate's y span (over the rear body, 0.05 off the flange)


def cyl_y(y0, y1, z, r, x=0.0):
    return cq.Workplane('XZ').workplane(offset=-y1).center(x, z).circle(r).extrude(y1 - y0)


# ---- the parts -------------------------------------------------------------------------------------------------------
board = box(*BRD, ZB, ZBT)
for x, y in HOLES:
    board = board.cut(cyl_z(x, y, 1.1, ZB - 1, ZBT + 1))
fp = union(cyl_y(yi1, yi1 + FP_FRONT[1], ZC, FP_FRONT[0] / 2), cyl_y(yi1 - FP_FLANGE[1], yi1, ZC, FP_FLANGE[0] / 2),
           cyl_y(FP_BACK, yi1 - FP_FLANGE[1], ZC, FP_REAR[0] / 2))
lens = cyl_y(yi1 + FP_FRONT[1] - 0.01, yi1 + FP_FRONT[1] + 0.05, ZC + 4.0, 1.2)   # the round lens above the axis
win = box(-1.5, 1.5, yi1 + FP_FRONT[1] - 0.01, yi1 + FP_FRONT[1] + 0.05, ZC - 7.0, ZC - 4.0)   # the square window
usb = box(J1[0] - 4.47, J1[0] + 4.47, J1_FRONT, J1_FRONT + 7.3, ZBT, ZBT + 3.26)
uz = ZBT + 1.63
usb_plug = box(J1[0] - USB_PLUG[0] / 2 + 0.3, J1[0] + USB_PLUG[0] / 2 - 0.3, J1_FRONT - 30.0, J1_FRONT,
               uz - USB_PLUG[1] / 2 + 0.3, uz + USB_PLUG[1] / 2 - 0.3).edges('|Y').fillet(0.7)
j3 = box(J3[0] - 4.0, J3[0] + 4.0, J3[1] - 1.2, BRD[3] - 0.1, ZBT, ZBT + 2.95)
plug = box(J3[0] - 3.6, J3[0] + 3.6, BRD[3] - 0.1, PLUG_END, ZBT, ZBT + 2.9)
rise = box(J3[0] - 4.0, J3[0] + 4.0, PLUG_END, PLUG_END + CABLE_RISE, ZBT, ZC + 8.0)
ics = union(box(U4[0] - 4.95, U4[0] + 4.95, U4[1] - 3.0, U4[1] + 3.0, ZBT, ZBT + 1.75),       # SOIC-16 with its leads
            box(U3[0] - 2.0, U3[0] + 2.0, U3[1] - 2.0, U3[1] + 2.0, ZBT, ZBT + 0.9),
            box(Y1[0] - 1.25, Y1[0] + 1.25, Y1[1] - 1.6, Y1[1] + 1.6, ZBT, ZBT + 0.8),
            box(U1[0] - 1.5, U1[0] + 1.5, U1[1] - 1.4, U1[1] + 1.4, ZBT, ZBT + 1.1))
power = union(box(L1[0] - 2.0, L1[0] + 2.0, L1[1] - 2.4, L1[1] + 2.4, ZBT, ZBT + 2.0),
              box(C9[0] - 2.6, C9[0] + 2.6, C9[1] - 1.4, C9[1] + 1.4, ZBT, ZBT + 2.1))
heads = union(*[cyl_z(x, y, 1.9, ZBT, ZBT + 1.4) for x, y in HOLES])                         # M2 pan heads
parts = [('FP001S', fp), ('board', board), ('USB-C J1', usb), ('USB-C plug', usb_plug), ('SH J3', j3),
         ('SH plug', plug), ('SH cable rise', rise), ('ICs', ics), ('L1 / C9', power), ('screw heads', heads)]

# ---- the case --------------------------------------------------------------------------------------------------------
r_hole = FP_FRONT[0] / 2 + FIT
r_rear = FP_REAR[0] / 2 + FIT
slot = union(cyl_y(yi1 - 0.1, yi1 + T_WALL + 0.1, ZC, r_hole),
             box(-r_hole, r_hole, yi1 - 0.1, yi1 + T_WALL + 0.1, ZC, Z_IN + 1))
usb_hole = box(J1[0] - USB_PLUG[0] / 2, J1[0] + USB_PLUG[0] / 2, yi0 - T_WALL - 1, yi0 + 0.1,
               uz - USB_PLUG[1] / 2, uz + USB_PLUG[1] / 2).edges('|Y').fillet(1.0)      # rounded in the wall's face
bosses = union(*[cyl_z(x, y, BOSS_D / 2, -0.01, ZB) for x, y in HOLES])
tray, lid, size, screws = shell_and_lid(xi0, xi1, yi0, yi1, [slot, usb_hole], [], Z_IN,
                                        keep_clear=[o for _, o in parts], tht=[usb], floor=[bosses, fp],
                                        rib_floor=ZB, walls=('x-', 'x+'))
for x, y in HOLES:
    tray = tray.union(cyl_z(x, y, BOSS_D / 2, -0.01, ZB)).cut(cyl_z(x, y, PILOT / 2, -0.4, ZB + 0.1))
# the holder plate behind the flange: the lower half (a U) on the floor, the upper half with the wall's tongue on the lid
plate_lo = box(-r_rear - 3.0, r_rear + 3.0, *PLATE, -0.01, ZC).cut(cyl_y(PLATE[0] - 1, PLATE[1] + 1, ZC, r_rear))
plate_hi = box(-r_rear - 3.0, r_rear + 3.0, *PLATE, ZC, Z_IN + 0.01).cut(cyl_y(PLATE[0] - 1, PLATE[1] + 1, ZC, r_rear))
# the tongue's bottom flat TONGUE_Z over the axis: following the circle down to the axis would end in knife edges
# (1.0 of PA12 at its corners from here; a crescent gap of up to ~1.4 is left beside the module's front either side)
TONGUE_Z = 5.0
tongue = box(-r_hole + 0.1, r_hole - 0.1, yi1 + 0.05, yi1 + T_WALL, ZC + TONGUE_Z, Z_IN + 0.01).cut(
    cyl_y(yi1 - 1, yi1 + T_WALL + 1, ZC, r_hole))
tray = tray.union(plate_lo)
lid = lid.union(plate_hi).union(tongue)
assert PLATE[0] > PLUG_END + CABLE_RISE, 'the plate stands in the cable rise'

bad = check((tray, lid), parts)
vol = (tray.val().Volume() + lid.val().Volume()) / 1000
print(REV, 'outer %.1f x %.1f x %.1f' % size, 'volume %.1f cm3' % vol, 'lid screws',
      [(round(float(x), 1), round(float(y), 1)) for x, y in screws], 'interference:', bad or 'none')
failed = [f'only {len(screws)} places for the lid screws'] if len(screws) < 3 else []
failed += bad

out = os.path.join(ROOT, 'station')
stls = []
for n, s, label in (('body', tray, '本体'), ('lid', lid, 'ふた')):
    p = os.path.join(out, f'vein_station_print_fp001s_v{VER}_{n}.stl')
    cq.exporters.export(s, p, tolerance=0.02, angularTolerance=0.1)
    stls.append((f'{label}の STL(MJF PA12 で造形)', p))
view = [
    ('shell', 'ふた(M2 皿ねじで本体の受けに締める。裏に FP001S の押さえ: 前の壁の切り欠きを埋める舌と、後ろの板の上半分)', '#2b2f33', 0.45, 'shell', lid),
    ('fp', 'FP001S-White(前 ⌀18.9・つば ⌀20.9・後ろ ⌀18.8、奥行き 6.2)。丸いレンズが上', '#e9e9e4', 1, 'mods', fp),
    ('lens', 'レンズ(丸、上)と四角い窓(下)', '#202326', 1, 'mods', lens.union(win)),
    ('board', 'USB 基板 t2(42 × 32、床のボスに M2 × 4 なべタッピング 4 本。pcb/fp001s_test_board)', '#1f7a4d', 1, 'mods', board),
    ('usb', 'J1 USB-C と挿したプラグ(奥の壁から、PC へ 1 本)', '#b8bcc2', 1, 'mods', usb.union(usb_plug)),
    ('j3', 'J3 SH 1.0 6P と挿したプラグ(手前の縁、口は +y)', '#f1efe8', 1, 'mods', j3.union(plug)),
    ('rise', 'SH ケーブルの立ち上がり(基板の縁と FP001S の後ろの間を上へ、モジュールのソケットへ)', '#d9775c', 0.8, 'mods', rise),
    ('ics', 'CH340C・CH334F・水晶・SY8089', '#202326', 1, 'mods', ics),
    ('power', 'L1 2.2 µH・C9 220 µF', '#6b5b3e', 1, 'mods', power),
    ('lid', '本体(床・壁・ボス・リブ・FP001S の受け、MJF PA12 で造形)', '#8fa09c', 0.9, 'lid', tray)]
dims = [('外形', '%.1f × %.1f × %.1f(幅 × 奥行き × 高さ、ふた込み)' % size), ('体積', '%.1f cm³(本体 + ふた)' % vol),
        ('肉厚', f'壁 {T_WALL}、床 {T_FLOOR}、天板 {T_TOP}(MJF PA12)'),
        ('FP001S', f'手前の壁に、軸を水平(+y)にして立てる。**丸いレンズが上**。前(⌀18.9 × 1.8)が壁を埋め、つば(⌀20.9)が壁の内面に当たり、'
                   f'後ろ(⌀18.8)を板で受ける。壁と板は上が開いた U で、ふたを外して上から落とし込み、ふたの舌と板の上半分で押さえる。レンズの高さは床の外面から {ZC + T_FLOOR:.1f}'),
        ('基板', f't2(42 × 32)を床のボス(⌀{BOSS_D:g}、高さ {BOSS_H:g})に M2 × 4 なべタッピング 4 本で留める'),
        ('USB-C', f'奥の壁の穴 {USB_PLUG[0]:g} × {USB_PLUG[1]:g}(R1)から PC へ 1 本。カメラ(UVC)と COM ポートが同時に出る'),
        ('ケーブル', 'J3 → FP001S は両端 SH 1.0 6P の 1 → 1(付属のケーブルは片側がバラ線で使えない)。J3 から手前へ出し、FP001S の後ろで上へ曲げる'),
        ('リブ', f'反り止め。幅 {RIB_W:g} を約 {RIB_PITCH:g} おきに、床(高さ {ZB:g}、基板の下)とふたの裏(深さ {RIB_LID:g})'),
        ('ふた', f'M2 皿タッピングねじ × {len(screws)} 本(M2 × 5)で、上から壁の内側の受け({LEDGE_D:g} × {LEDGE_W:g}、高さ {LEDGE_H:g})に締める: '
                 + ', '.join(f'({x:.1f}, {y:.1f})' for x, y in screws)),
        ('干渉', 'なし' if not bad else ', '.join(bad))]
write_page('fp001s-print', f'FP001S USB ボックス {REV}', view,
           'Grow FP001S(顔・手のひら静脈)と USB 基板 t2 を 3D 印刷(MJF PA12)の箱に入れ、USB-C 1 本で PC につなぐ案。'
           'ドラッグで回転、ホイール/ピンチで拡大。', dims,
           'FP001S の外形はマニュアル 1.3.1 の値、レンズと窓の位置は写真からのイメージ。基板の部品は KiCad のフットプリント寸法と'
           'データシートからの簡略形状。単位 mm。', Z_TOP, stls, tz='-12')
if failed:
    raise SystemExit('interference: ' + ', '.join(failed))
