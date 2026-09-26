"""Vein Unit: the finger vein module alone in a Takachi SW-75 (50 × 75 × 30, ABS, snap-in cover, ¥200), like an M5Stack
Unit: one Grove socket in an end wall, so the only cable that leaves is a Grove cable (to a PortABC PORT.C, 5 V).
The module's own MX1.25 cable stays inside, a few cm long, and never moves.
Run from the repository root:  python3 station/build_vein_unit.py
Writes the 3D preview site/vein-unit/index.html and fails if the case collides with the module, the board or its parts.

Coordinates: x along 75 (the Grove end at -x), y along 50, z = 0 on the desk; origin = centre of the case.
SW-75 from Takachi's drawing (SW-75B.pdf, 2024-07-16): body 50 × 75 × 28 with 2.0 walls and floor, cover 2.0 on
top (z 28..30) with a 1.6 lip 5 deep inside the body; usable inside 42.8 × 67.8 (the walls draw in towards the top,
44.8 × 69.8 at the floor), which the model uses all the way up (conservative).
Stack (z): floor 2 | M3 × 4 pan heads under the board (the feet, 2..4) | adapter board 1.6 (4..5.6): Grove socket
(right angle, at the -x edge, behind a hole in the end wall), 5 V -> 3.3 V LDO, MX1.25 for the module's cable |
M3 female-female spacers 10 (5.6..15.6) | VHB tape 1.0 | vein module 16.6..31.6: 1.6 proud of the cover, through a
window of its outline + 0.2 cut in the cover, so the cover holds its top sideways and the tape its bottom.
Machining: the cover window and the Grove hole (9.2 × 6.6) in the -x end wall; nothing else.
"""
import os
from shapes import box, rbox, cyl_z, union, vein_parts, write_page

REV = 'vu1'
L, W, H = 75.0, 50.0, 30.0        # SW-75 outside
T, TC, LIP = 2.0, 2.0, 5.0        # wall / floor, cover, cover lip depth
IX, IY = 67.8 / 2, 42.8 / 2       # usable inside (half)
ZC = H - TC                       # cover underside 28

# ---- vein module and what holds it ------------------------------------------------------------------------
VEIN = (-29.5, 29.5, -13.0, 13.0)                 # 59 × 26, centred
SP, TAPE = 10.0, 1.0
Z_BRD = T + 2.0                                   # board bottom on the M3 pan heads
Z_BT = Z_BRD + 1.6
VEIN_Z0 = Z_BT + SP + TAPE                        # 16.6: top 31.6, 1.6 proud of the cover
VEIN_WIN = (VEIN[0] - 0.2, VEIN[1] + 0.2, VEIN[2] - 0.2, VEIN[3] + 0.2, 2.2)
vein = rbox(*VEIN, VEIN_Z0, VEIN_Z0 + 15.0, 2.0)
SPACERS = [(sx * 25.5, sy * 9.5) for sx in (1, -1) for sy in (1, -1)]      # under the module's corners
spacers = union(*[cyl_z(x, y, 3.2, Z_BT, Z_BT + SP) for x, y in SPACERS])
screws = union(*[cyl_z(x, y, 2.75, T, Z_BRD) for x, y in SPACERS])

# ---- adapter board (Grove 5 V in -> LDO -> MX1.25 to the module) --------------------------------------------
BRD = (-IX + 0.5, IX - 2.4, -IY + 2.4, IY - 2.4)
board = box(*BRD, Z_BRD, Z_BT)
for x, y in SPACERS:
    board = board.cut(cyl_z(x, y, 1.6, Z_BRD - 1, Z_BT + 1))
GROVE_Y, GROVE_Z = 0.0, Z_BT                      # right-angle HY2.0 4P, opening to -x, flush with the board edge
grove = box(BRD[0], BRD[0] + 7.0, GROVE_Y - 4.0, GROVE_Y + 4.0, GROVE_Z, GROVE_Z + 5.8)
grove_plug = box(-L / 2 - 10.0, BRD[0], GROVE_Y - 3.9, GROVE_Y + 3.9, GROVE_Z + 0.4, GROVE_Z + 5.4)
ldo = box(-18.0, -15.0, 10.0, 11.6, Z_BT, Z_BT + 1.2).union(box(-13.0, -11.0, 9.8, 11.8, Z_BT, Z_BT + 1.0)) \
    .union(box(-21.0, -19.0, 9.8, 11.8, Z_BT, Z_BT + 1.0))
j1 = box(26.0, 30.0, -5.0, 5.0, Z_BT, Z_BT + 4.0)                     # MX1.25, top entry, under the module's end
j1_plug = box(26.3, 29.7, -4.6, 4.6, Z_BT + 4.0, Z_BT + 7.0)
vein_plug = box(VEIN[1], VEIN[1] + 2.6, -6.0, 6.0, VEIN_Z0 + 1.5, VEIN_Z0 + 5.0)
cable = cyl_z(31.0, 0.0, 1.2, Z_BT + 7.0, VEIN_Z0 + 1.5).union(box(28.0, 31.0, -1.2, 1.2, Z_BT + 5.8, Z_BT + 7.0))

# ---- case (Takachi SW-75, simplified from the drawing) ------------------------------------------------------
body = rbox(-L / 2, L / 2, -W / 2, W / 2, 0, ZC, 1.75).cut(box(-IX, IX, -IY, IY, T, ZC + 1))
cover = rbox(-L / 2, L / 2, -W / 2, W / 2, ZC, H, 1.75).union(
    box(-IX, IX, -IY, IY, ZC - LIP, ZC).cut(box(-IX + 1.6, IX - 1.6, -IY + 1.6, IY - 1.6, ZC - LIP - 1, ZC + 1)))
cover = cover.cut(rbox(*VEIN_WIN[:4], ZC - LIP - 1, H + 1, VEIN_WIN[4]))
GROVE_HOLE = (GROVE_Y - 4.6, GROVE_Y + 4.6, GROVE_Z - 0.4, GROVE_Z + 6.2)
body = body.cut(box(-L / 2 - 1, -IX + 0.1, *GROVE_HOLE))

# ---- interference ----------------------------------------------------------------------------------------
case = body.union(cover)
bad = []
for name, obj in [('指静脈', vein), ('board', board), ('spacers', spacers), ('screws', screws), ('Grove', grove),
                  ('Grove plug', grove_plug), ('LDO', ldo), ('J1', j1), ('J1 plug', j1_plug),
                  ('vein plug', vein_plug), ('cable', cable)]:
    v = case.intersect(obj).val().Volume()
    print(f'interference case x {name:10s} = {v:.3f} mm3')
    if v > 0.01:
        bad.append(name)
for na, a, nb, b in [('指静脈', vein, 'J1 plug', j1_plug), ('指静脈', vein, 'cable', cable), ('spacers', spacers, 'J1', j1),
                     ('spacers', spacers, 'LDO', ldo), ('spacers', spacers, 'Grove', grove)]:
    v = a.intersect(b).val().Volume()
    if v > 0.01:
        print(f'interference {na} x {nb} = {v:.3f} mm3')
        bad.append(f'{na}/{nb}')

# ---- 3D preview ------------------------------------------------------------------------------------------
Z_TOP = VEIN_Z0 + 15.0
parts = [
    ('shell', 'カバー(タカチ SW-75、上面に指静脈の窓)', '#5c6166', 0.45, 'shell', cover),
] + vein_parts(VEIN, VEIN_Z0) + [
    ('board', '中継基板(Grove 5V → LDO 3.3V → MX1.25)', '#1f7a4d', 1, 'mods', board),
    ('grove', 'Grove ソケット(HY2.0 4P、横向き)', '#f1efe8', 1, 'mods', grove),
    ('groveplug', 'Grove プラグ(PortABC の PORT.C へ)', '#c47f0e', 1, 'mods', grove_plug),
    ('ldo', 'LDO 5V→3.3V とコンデンサ', '#202326', 1, 'mods', ldo),
    ('j1', 'J1 MX1.25(指静脈のケーブル)', '#f1efe8', 1, 'mods', j1),
    ('j1plug', '指静脈ケーブルのプラグ', '#e7e1cf', 1, 'mods', j1_plug.union(vein_plug)),
    ('cable', '指静脈ケーブル(箱の中だけ、数 cm)', '#3a4046', 1, 'mods', cable),
    ('spacers', 'M3 メスメス 10(上面に VHB テープ)', '#c9a227', 1, 'mods', spacers),
    ('screws', 'M3 × 4 なべ(基板の足)', '#9aa0a6', 1, 'mods', screws),
    ('lid', 'ボディー(タカチ SW-75、端面に Grove の穴)', '#8a8f96', 0.6, 'lid', body),
]
SUB = ('指静脈モジュールだけをタカチ SW-75 に入れ、M5Stack の Unit のように Grove 1 本で VoiceS3R(PortABC)につなぐ案。'
       '指静脈の MX1.25 ケーブルは箱の中だけで動かない。ドラッグで回転、ホイール/ピンチで拡大。')
DIMS = [('ケース', 'タカチ SW-75(50 × 75 × 30、ABS、はめ込み式のカバー、¥200)'), ('内側', '42.8 × 67.8 × 23(有効寸法)'),
        ('加工', 'カバーに指静脈の窓(外形 + 0.2、R2.2)、端面に Grove の穴 9.2 × 6.6'),
        ('指静脈', 'M3 メスメス 10 × 4 の上に VHB、カバーから 1.6 突き出す'),
        ('中継基板', f'{BRD[1] - BRD[0]:.1f} × {BRD[3] - BRD[2]:.1f}、M3 × 4 のなべ頭を足にして床に置く(床は加工なし)'),
        ('電源', 'Grove の 5V を LDO で 3.3V に(指静脈は DC3.3V)')]
NOTE = ('ケースはタカチの図面(SW-75B.pdf)の寸法からの簡略形状、壁の抜き勾配は内側の有効寸法で代用。指静脈の外形は公式値、'
        '細部は製品写真を見て描いたイメージで、コネクタの位置は未確定。中継基板と部品は仮の形。単位 mm。')
write_page('vein-unit', '指静脈 Unit ' + REV, parts, SUB, DIMS, NOTE, Z_TOP, tz='-15')

if bad:
    raise SystemExit('interference: ' + ', '.join(bad))
