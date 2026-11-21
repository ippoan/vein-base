"""FP001S USB box: the Grow FP001S face / palm vein module and its USB board t5 (pcb/fp001s_test_board, 54 x 34) in
one printed box (MJF PA12), one USB-C cable to the PC like a USB camera.
  - The board lies on four floor bosses (M2 x 4 pan tapping screws from the top through H1..H4), J1 (USB-C, the PC)
    and J2 (USB-C, a device: the VoiceS3R, fp4) out through the back (-y) wall, J3 (SH 1.0 6P, opening +y) at the
    front edge.
  - The module lies in the lid looking straight up (its face parallel to the desk, the user's choice 2026-11-18:
    the face is looked down at, the palm held over it), in front of the board (+y). Its front (dia 18.9, 1.8) fills
    a hole in the lid flush with the top, the flange (dia 20.9, 1.0) sits in a recess in the lid's underside, the
    rear (dia 18.8, 3.4) hangs into the box and rests on three posts on the floor: closing the lid clamps it. The
    round lens towards the back (-y), the square window towards the user (+y): the manual's "Up" (the lens side)
    away from the user who leans over it, so the face comes out upright (upside down it sees nothing, 2026-11-18).
  - The SH cable (10 cm, both ends SH, 1 -> 1; the module's own cable has loose wires) leaves J3 forwards and runs
    on under the module to its socket on the module's back; the ~7 cm left over is folded into a pocket beside the
    module (one each side, as the socket's place on the module is not known yet). All of it is in the check.
  - The lid: M2 x 5 countersunk tapping screws from the top into ledges on the walls (station/shapes.py).
Writes site/fp001s-print/ and station/vein_station_print_fp001s_v<VERSION>_{body,lid}.stl, fails on any interference.
Run from the repository root:  python3 station/build_fp001s_print.py
Coordinates = the board's (pcb/fp001s_test_board/build_board.py: origin = the board's centre, J1 on the -y edge),
z = 0 on the floor's inside face."""
import os
import cadquery as cq
from shapes import (ROOT, VER, box, rbox, cyl_z, union, write_page, shell_and_lid, check, T_WALL, T_FLOOR, T_TOP,
                    LEDGE_D, LEDGE_W, LEDGE_H, RIB_W, RIB_PITCH, RIB_LID)

REV = 'fp4'
# ---- shared with pcb/fp001s_test_board/build_board.py (t5): outline, holes, part places. Keep the two together -------
BRD = (-27.0, 27.0, -17.0, 17.0)
HOLES = [(sx * 24.5, sy * 14.5) for sx in (-1, 1) for sy in (-1, 1)]
J1 = (-16.5, -13.95)                     # USB-C (HRO TYPE-C-31-M-12), footprint origin
J3 = (-16.0, 13.6)                       # SH 1.0 6P horizontal (SM06B-SRSS-TB), turned 180, opening +y
U6, Y106 = (2.0, 3.0), (2.0, -9.4)       # RP2354A QFN-60 7x7 (RP) and its 12 MHz 3225 (the minimal design's X1)
U3, Y1 = (-15.0, 0.0), (-10.5, 0.0)      # CH334F QFN-24 4x4, 12 MHz 3225
U1, L1, C9 = (18.5, -0.5), (23.5, 0.0), (22.0, 8.6)    # SY8089 SOT-23-5 (U5), SWPA4020 4x4 (L2), 220 uF 3528
J2 = (16.5, -13.95)                      # t5: the second USB-C (a device: the VoiceS3R), same edge as J1
# ----------------------------------------------------------------------------------------------------------------------
GAP = 0.3
BOSS_D, BOSS_H, PILOT = 5.0, 2.5, 1.6    # M2 x 4 tapping: 1.6 board + 2.4 into the boss (2.5); the pilot from z -0.4, 1.2 of floor left
ZB = BOSS_H
ZBT = ZB + 1.6
# the module (Grow FP001S-White, manual 1.3.1): front dia 18.9 x 1.8, flange dia 20.9 x 1.0, rear dia 18.8 x 3.4
FP_FRONT, FP_FLANGE, FP_REAR = (18.9, 1.8), (20.9, 1.0), (18.8, 3.4)
FIT = 0.2                                # the holes / U's over the module's diameters (radius + FIT)
# J1's receptacle overhangs the board's -y edge (courtyard to -17.1): the back wall's inside 0.3 past its front
J1_FRONT = J1[1] - 3.9                   # the receptacle's front (t2: -16.85 at J1 y -12.95)
USB_PLUG = (13.0, 7.4)                   # the plug's overmould through the back wall (w x h, rounded), from J1's face
# J3's mated plug and wires: out of the receptacle's front (+y) at the board's edge to PLUG_END, then on under the
# module to its socket on its back (the module's underside; the cable is laid by hand, only the room is kept)
PLUG_END = BRD[3] + 4.5                  # the mated plug and the wires' first bend past the board's edge
CABLE_ROOM = 2.0                         # over the plug for the wires' bend, under the module
xi0, xi1, yi0 = BRD[0] - GAP, BRD[1] + GAP, J1_FRONT - GAP
# the module lies in the lid looking straight up (parallel to the desk, the user's choice 2026-11-18), in front of the
# board: its front flush with the lid's top, the flange in a recess on the lid's underside, the rear body hanging
# into the box over the SH plug, held up from below by three posts on the floor (so closing the lid clamps it)
FP_C = (0.0, BRD[3] + GAP + FP_FLANGE[0] / 2 + 0.3)     # the module's axis (x, y)
yi1 = FP_C[1] + FP_FLANGE[0] / 2 + GAP
Z_REAR = ZBT + 2.9 + CABLE_ROOM          # the module's back (rear face) over the plug and the wires' bend
Z_TOP = Z_REAR + FP_REAR[1] + FP_FLANGE[1] + FP_FRONT[1]    # the front flush with the lid's top
Z_IN = Z_TOP - T_TOP
FLANGE_UP = (Z_TOP - FP_FRONT[1]) - Z_IN                    # the flange's top over the lid's underside: the recess
assert 0 < FLANGE_UP < T_TOP - 1.0 + 1e-9, 'the lid keeps 1.0 over the flange recess'
POSTS = [(FP_C[0] + sx * 6.3, FP_C[1] - 2.5) for sx in (-1, 1)] + [(FP_C[0], FP_C[1] + 6.5)]   # under the rear body
POST_D = 4.0


def cyl_y(y0, y1, z, r, x=0.0):
    return cq.Workplane('XZ').workplane(offset=-y1).center(x, z).circle(r).extrude(y1 - y0)


# ---- the parts -------------------------------------------------------------------------------------------------------
board = box(*BRD, ZB, ZBT)
for x, y in HOLES:
    board = board.cut(cyl_z(x, y, 1.1, ZB - 1, ZBT + 1))
fx, fy = FP_C
z1 = Z_REAR + FP_REAR[1]
fp = union(cyl_z(fx, fy, FP_REAR[0] / 2, Z_REAR, z1), cyl_z(fx, fy, FP_FLANGE[0] / 2, z1, z1 + FP_FLANGE[1]),
           cyl_z(fx, fy, FP_FRONT[0] / 2, z1 + FP_FLANGE[1], Z_TOP))
# the round lens towards the back (-y, the board's side) and the square window towards the user (+y): looked down on
# from the front, the image comes out with the face upright (the manual's "Up" = the lens side)
lens = cyl_z(fx, fy - 4.0, 1.2, Z_TOP - 0.01, Z_TOP + 0.05)
win = box(fx - 1.5, fx + 1.5, fy + 4.0, fy + 7.0, Z_TOP - 0.01, Z_TOP + 0.05)
assert J2[1] == J1[1], 'J2 on the same line as J1 (one back wall, one J1_FRONT)'
uz = ZBT + 1.63
usb = union(*[box(j[0] - 4.47, j[0] + 4.47, J1_FRONT, J1_FRONT + 7.3, ZBT, ZBT + 3.26) for j in (J1, J2)])
usb_plug = union(*[box(j[0] - USB_PLUG[0] / 2 + 0.3, j[0] + USB_PLUG[0] / 2 - 0.3, J1_FRONT - 30.0, J1_FRONT,
                       uz - USB_PLUG[1] / 2 + 0.3, uz + USB_PLUG[1] / 2 - 0.3).edges('|Y').fillet(0.7) for j in (J1, J2)])
j3 = box(J3[0] - 4.0, J3[0] + 4.0, J3[1] - 1.2, BRD[3] - 0.1, ZBT, ZBT + 2.95)
plug = box(J3[0] - 3.6, J3[0] + 3.6, BRD[3] - 0.1, PLUG_END, ZBT, ZBT + 2.9)
# the SH cable: 10 cm, both ends SH (1 -> 1). J3 to the module's socket is 2..3 cm, ~7 cm left over. Where the
# socket sits on the module's back (the cable leaves it sideways along the back) is not known yet, so the room is
# kept for any side: a low run on under the module, a band over the plug out to both sides, and a pocket either side
# of the module where the rest is folded (each ~7 wide, 13 deep, 10 high: a 6-wire ribbon on edge, two turns;
# clear of the lid's locating rim along the walls)
run = box(J3[0] - 4.0, J3[0] + 4.0, PLUG_END, FP_C[1] + 3.0, ZBT, ZBT + 2.0)
band = box(J3[0] - 4.0, 11.0, BRD[3] + 1.0, BRD[3] + 6.0, ZBT + 2.9, Z_REAR)      # J3 (at -x) over to both sides
POCKET = (11.0, xi1 - 3.0, BRD[3] + 1.0, BRD[3] + 14.0, ZB + 0.1, Z_IN - 0.5)   # x0, x1 (mirrored), y0, y1, z0, z1
# t3: J3 sits at -x, under the left pocket: that one starts over the plug and the run (the ribbon laid flat there)
pockets = union(box(POCKET[0], POCKET[1], *POCKET[2:]),
                box(-POCKET[1], -POCKET[0], POCKET[2], POCKET[3], ZBT + 2.9, POCKET[5]))
rise = union(run, band, pockets)
ics = union(box(U6[0] - 3.5, U6[0] + 3.5, U6[1] - 3.5, U6[1] + 3.5, ZBT, ZBT + 0.9),         # RP2354A QFN-60
            box(Y106[0] - 1.6, Y106[0] + 1.6, Y106[1] - 1.25, Y106[1] + 1.25, ZBT, ZBT + 0.8),
            box(U3[0] - 2.0, U3[0] + 2.0, U3[1] - 2.0, U3[1] + 2.0, ZBT, ZBT + 0.9),
            box(Y1[0] - 1.25, Y1[0] + 1.25, Y1[1] - 1.6, Y1[1] + 1.6, ZBT, ZBT + 0.8),
            box(U1[0] - 1.5, U1[0] + 1.5, U1[1] - 1.4, U1[1] + 1.4, ZBT, ZBT + 1.1))
power = union(box(L1[0] - 2.0, L1[0] + 2.0, L1[1] - 2.4, L1[1] + 2.4, ZBT, ZBT + 2.0),
              box(C9[0] - 2.6, C9[0] + 2.6, C9[1] - 1.4, C9[1] + 1.4, ZBT, ZBT + 2.1))
heads = union(*[cyl_z(x, y, 1.9, ZBT, ZBT + 1.4) for x, y in HOLES])                         # M2 pan heads
parts = [('FP001S', fp), ('board', board), ('USB-C J1 / J2', usb), ('USB-C plug', usb_plug), ('SH J3', j3),
         ('SH plug', plug), ('SH cable room', rise), ('ICs', ics), ('L1 / C9', power), ('screw heads', heads)]

# ---- the case --------------------------------------------------------------------------------------------------------
r_hole = FP_FRONT[0] / 2 + FIT
lid_hole = union(cyl_z(fx, fy, r_hole, Z_IN - 1, Z_TOP + 1),
                 cyl_z(fx, fy, FP_FLANGE[0] / 2 + FIT, Z_IN - 1, Z_IN + FLANGE_UP))        # the flange's recess
usb_holes = [box(j[0] - USB_PLUG[0] / 2, j[0] + USB_PLUG[0] / 2, yi0 - T_WALL - 1, yi0 + 0.1,
                 uz - USB_PLUG[1] / 2, uz + USB_PLUG[1] / 2).edges('|Y').fillet(1.0) for j in (J1, J2)]   # rounded in the wall's face
bosses = union(*[cyl_z(x, y, BOSS_D / 2, -0.01, ZB) for x, y in HOLES])
posts = union(*[cyl_z(x, y, POST_D / 2, -0.01, Z_REAR) for x, y in POSTS])
tray, lid, size, screws = shell_and_lid(xi0, xi1, yi0, yi1, usb_holes, [lid_hole], Z_IN,
                                        keep_clear=[o for _, o in parts], tht=[usb], floor=[bosses, posts],
                                        rib_floor=ZB, walls=('x-', 'x+'))
for x, y in HOLES:
    tray = tray.union(cyl_z(x, y, BOSS_D / 2, -0.01, ZB)).cut(cyl_z(x, y, PILOT / 2, -0.4, ZB + 0.1))
tray = tray.union(posts)
for x, y in POSTS:
    assert (x - fx) ** 2 + (y - fy) ** 2 < (FP_REAR[0] / 2 - POST_D / 2 - 0.3) ** 2, 'a post off the rear body'

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
    ('shell', 'ふた(M2 皿ねじで本体の受けに締める。FP001S の穴と、裏につばの座ぐり)', '#2b2f33', 0.45, 'shell', lid),
    ('fp', 'FP001S-White(前 ⌀18.9・つば ⌀20.9・後ろ ⌀18.8、厚さ 6.2)。真上を向き、前の面はふたの上面とそろう', '#e9e9e4', 1, 'mods', fp),
    ('lens', 'レンズ(丸、奥 = USB-C の側)と四角い窓(手前 = 使う人の側)', '#202326', 1, 'mods', lens.union(win)),
    ('board', 'USB 基板 t5(54 × 34、床のボスに M2 × 4 なべタッピング 4 本。pcb/fp001s_test_board)', '#1f7a4d', 1, 'mods', board),
    ('usb', 'J1(PC へ)・J2(VoiceS3R へ)の USB-C と挿したプラグ(どちらも奥の壁から)', '#b8bcc2', 1, 'mods', usb.union(usb_plug)),
    ('j3', 'J3 SH 1.0 6P と挿したプラグ(手前の縁、口は +y)', '#f1efe8', 1, 'mods', j3.union(plug)),
    ('rise', 'SH ケーブル(10 cm)の置き場: J3 から FP001S の下へ、プラグの上の帯で左右へ、余り約 7 cm は FP001S の左右のポケットに折り返す', '#d9775c', 0.6, 'mods', rise),
    ('ics', 'RP2354A・CH334F・水晶 2 つ・SY8089', '#202326', 1, 'mods', ics),
    ('power', 'L1 2.2 µH・C9 220 µF', '#6b5b3e', 1, 'mods', power),
    ('lid', '本体(床・壁・ボス・リブ・FP001S を下から受ける柱 3 本、MJF PA12 で造形)', '#8fa09c', 0.9, 'lid', tray)]
dims = [('外形', '%.1f × %.1f × %.1f(幅 × 奥行き × 高さ、ふた込み)' % size), ('体積', '%.1f cm³(本体 + ふた)' % vol),
        ('肉厚', f'壁 {T_WALL}、床 {T_FLOOR}、天板 {T_TOP}(MJF PA12)'),
        ('FP001S', f'ふたの手前側に、**真上を向けて**(机に平行)入れる。前(⌀18.9 × 1.8)がふたの穴を埋めて上面とそろい、つば(⌀20.9)がふたの裏の座ぐり(深さ {FLANGE_UP:.1f})に当たり、'
                   f'後ろ(⌀18.8)を床の柱 3 本(⌀{POST_D:g})が下から受ける。ふたを閉めると挟まる。**丸いレンズは奥(USB-C の側)、四角い窓は手前(使う人の側)**: 上からのぞき込んだ顔が正立して写る向き'),
        ('基板', f't5(54 × 34)を床のボス(⌀{BOSS_D:g}、高さ {BOSS_H:g})に M2 × 4 なべタッピング 4 本で留める'),
        ('USB-C', f'奥の壁の穴 {USB_PLUG[0]:g} × {USB_PLUG[1]:g}(R1)× 2: 左の J1 から PC へ 1 本(カメラ(UVC)と COM ポートが同時に出る)、右の J2 に VoiceS3R(ハブのポート 3)'),
        ('ケーブル', f'J3 → FP001S は両端 SH 1.0 6P の 1 → 1、10 cm(付属のケーブルは片側がバラ線で使えない)。J3 から手前へ出し、FP001S の下を通して裏のソケットへ(2〜3 cm)。'
                     f'余り約 7 cm は FP001S の左右のポケット({POCKET[1] - POCKET[0]:.1f} × {POCKET[3] - POCKET[2]:.0f} × 高さ {POCKET[5] - POCKET[4]:.1f})のうちソケットに近い側に折り返す。'
                     'ソケットの位置(レンズに対してどの縁か)は実物で確かめる'),
        ('リブ', f'反り止め。幅 {RIB_W:g} を約 {RIB_PITCH:g} おきに、床(高さ {ZB:g}、基板の下)とふたの裏(深さ {RIB_LID:g})'),
        ('ふた', f'M2 皿タッピングねじ × {len(screws)} 本(M2 × 5)で、上から壁の内側の受け({LEDGE_D:g} × {LEDGE_W:g}、高さ {LEDGE_H:g})に締める: '
                 + ', '.join(f'({x:.1f}, {y:.1f})' for x, y in screws)),
        ('干渉', 'なし' if not bad else ', '.join(bad))]
write_page('fp001s-print', f'FP001S USB ボックス {REV}', view,
           'Grow FP001S(顔・手のひら静脈)と USB 基板 t5 を 3D 印刷(MJF PA12)の箱に入れ、USB-C 1 本で PC につなぐ案。FP001S は真上を向く。'
           'ドラッグで回転、ホイール/ピンチで拡大。', dims,
           'FP001S の外形はマニュアル 1.3.1 の値、レンズと窓の位置は写真からのイメージ。基板の部品は KiCad のフットプリント寸法と'
           'データシートからの簡略形状。単位 mm。', Z_TOP, stls, tz='-12')
if failed:
    raise SystemExit('interference: ' + ', '.join(failed))
