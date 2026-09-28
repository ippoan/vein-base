"""Vein Station SW (alternative): the station in the smallest Takachi case the modules fit, an SW-85B (60 × 40 × 85,
ABS, snap-in cover, ¥350), with the Atom VoiceS3R's circuit on the board itself (pcb/station_esp_board,
`build_board.py sw`, 52 × 76) instead of the Atom. Against the PF13-4-9 (125 × 40 × 85) it takes half the desk.
Run from the repository root:  python3 station/build_station_sw.py
Writes the 3D preview site/station-sw/index.html and fails if the case collides with a module, plug, spacer or the
board, or two of those collide with each other.

Case coordinates = the board's: x across the 60 side, y along the 85 side, the DB9 / USB-C end on -y, origin = case
centre, z = 0 at the inside of the floor. The case is written from Takachi's drawing (SW-85□, 2024/07/16, DXF/PDF on
takachi-el.co.jp): outside 60 × 85 R2 × 40, floor 2.3, cover 2 thick with a 5 deep skirt; inside ("有効寸法")
52.8 × 77.8 × 32.7, kept here as the free space at every height (the walls lean out to 53.7 × 78.7 at the floor, and
everything from 32.7 up to the cover's top face at 37.7 is taken as solid, so the model is on the safe side); two
floor ribs 2.5 wide at |x| 17.5..20 along the whole length (their height is not dimensioned: 2.0 assumed).
Stack (z): Takachi ASL-12 stick-on snap spacers on the floor (□14 tape base, between the ribs) | board 11.9..13.5 |
vein module on M3 × 12 male-female spacers (nut under the board) + 1.0 VHB tape, 26.5..41.5: 3.8 proud of the cover
through a window of its outline + 0.2 | Unit NFC on M3 × 10 spacers, 23.5..31.5, taped to the cover's underside
(below the skirt band, it reads through the cover) | DB9 and USB-C on the -y end through cut-outs in the end wall.
The speaker and the mic sit in front of the NFC, under holes in the cover.
"""
import os
from shapes import box, rbox, cyl_z, cyl_y, stl_at, vein_parts, write_page

REV = 'sw1'

# ---- case (Takachi SW-85B, from the drawing) --------------------------------------------------------------
OUT = (-30.0, 30.0, -42.5, 42.5)
FLOOR, CEIL, TOP = -2.3, 32.7, 37.7
IN = (-26.4, 26.4, -38.9, 38.9)
body = rbox(*OUT, FLOOR, TOP, 2.0).cut(box(*IN, 0, CEIL))
for sx in (1, -1):
    body = body.union(box(*sorted((sx * 17.5, sx * 20.0)), IN[2], IN[3], 0, 2.0))       # floor ribs

# ---- board (pcb/station_esp_board, build_board.py sw) and what stands on it: keep these lists together with it ----
BX0, BX1, BY0, BY1 = -26.0, 26.0, -38.0, 38.0
HOLES = [(-22.5, -8.0), (-3.3, -8.0), (-22.5, 6.0), (-3.3, 6.0),        # H1..H4 vein spacers
         (6.5, -24.5), (22.5, -24.5), (21.2, 16.0)]                     # H5..H7 NFC spacers
VEIN_H, NFC_H = (1, 2, 3, 4), (5, 6, 7)
ASL = [(-8.0, -13.5), (-10.0, 8.5), (0.5, 12.5)]
DB9_BX, UX = -10.0, 12.5
WROOM = (-14.0, 25.25)                     # module centre, antenna end on the +y edge
J3 = (-20.0, -21.0)                        # opening +y
GROVE = [('J6 NFC', 15.5, -13.3), ('J7 G38/G39', 12.8, 2.5)]              # openings +y
SPK, MIC = (18.5, 30.5), (7.8, 30.3)      # speaker centre, mic sound port
U1, SW1 = (-7.5, -21.0), (-12.9, -3.0)

ZB = 11.9                                  # ASL-12
ZBT = ZB + 1.6
MALE, NUT, TAPE = 6.0, 2.4, 1.0
SP_VEIN, SP_NFC = 12.0, 10.0
VEIN = (-25.8, 0.2, -26.0, 33.0)           # 26 across, 59 along y, the socket end at -y
VEIN_Z0 = ZBT + SP_VEIN + TAPE             # 26.5, top 41.5
NFC = (1.2, 25.2, -27.0, 21.0)             # 24 × 48, the Grove end at -y
NFC_Z0 = ZBT + SP_NFC                      # 23.5, top 31.5
NFC_TOP = NFC_Z0 + 8.0
NX = (NFC[0] + NFC[1]) / 2

pcb = box(BX0, BX1, BY0, BY1, ZB, ZBT)
for x, y in HOLES:
    pcb = pcb.cut(cyl_z(x, y, 1.6, ZB - 1, ZBT + 1))
for x, y in ASL:
    pcb = pcb.cut(cyl_z(x, y, 1.5, ZB - 1, ZBT + 1))


def on(x0, x1, y0, y1, z0, z1):
    """Box on the board, z from the board's top face."""
    return box(x0, x1, y0, y1, ZBT + z0, ZBT + z1)


# DB9 male RA on the -y edge (as build_station_pf.py, from the KiCad footprint)
db9_body = on(DB9_BX - 15.0, DB9_BX + 15.0, BY0 + 0.5, BY0 + 10.5, 0, 12.5)
db9_flange = on(DB9_BX - 15.4, DB9_BX + 15.4, BY0 - 1.0, BY0, 0, 12.5)
db9_shell = on(DB9_BX - 8.5, DB9_BX + 8.5, BY0 - 7.0, BY0 - 1.0, 2.0, 10.5)
db9_tails = on(DB9_BX - 6.5, DB9_BX + 6.5, BY0 + 3.0, BY0 + 8.5, -4.6, -1.6)
DB9_ZC = ZBT + 6.25
db9_posts = (cyl_y(DB9_BX - 12.5, BY0 - 5.0, BY0 - 1.0, DB9_ZC, 2.5)
             .union(cyl_y(DB9_BX + 12.5, BY0 - 5.0, BY0 - 1.0, DB9_ZC, 2.5)))
DB9_X0, DB9_X1 = DB9_BX - 15.4, DB9_BX + 15.4
# the plug's hood goes into the end wall's cut-out and stops 0.8 short of the flange
db9_plug = box(DB9_X0 + 0.25, DB9_X1 - 0.25, -80, BY0 - 1.8, ZBT - 0.75, ZBT + 13.25)

# USB-C receptacle (TYPE-C-31-M-12, front 0.6 past the edge) and the Sanwa KU-CCP L plug (as build_station_pf.py)
UF = BY0 - 0.6
UZ = ZBT + 1.63
usb = on(UX - 4.47, UX + 4.47, UF, UF + 7.3, 0, 3.26)
usb_plug = box(UX - 4.2, UX + 4.2, UF - 6.5, UF, UZ - 1.5, UZ + 1.5).union(
    box(UX - 6.0, UX + 6.0, UF - 24.2, UF - 6.5, UZ - 3.5, UZ + 3.5))

j3 = on(J3[0] - 5.0, J3[0] + 5.0, J3[1] - 3.7, J3[1] + 3.1, 0, 3.4)
j3_plug = on(J3[0] - 3.0, J3[0] + 3.0, J3[1] + 3.1, J3[1] + 9.1, 0.3, 3.1)
u1 = on(U1[0] - 5.0, U1[0] + 5.0, U1[1] - 1.95, U1[1] + 1.95, 0, 1.75)
sw1 = on(SW1[0] - 5.7, SW1[0] + 5.7, SW1[1] - 6.2, SW1[1] + 6.2, 0, 2.0)
wroom = on(WROOM[0] - 9.0, WROOM[0] + 9.0, WROOM[1] - 12.75, WROOM[1] + 12.75, 0, 3.1)
spk = on(SPK[0] - 6.5, SPK[0] + 6.5, SPK[1] - 6.5, SPK[1] + 6.5, 0, 4.0)
grove = grove_plugs = None
for _, x, y in GROVE:
    g = on(x - 5.0, x + 5.0, y - 3.9, y + 3.9, 0, 6.0)
    p = on(x - 4.5, x + 4.5, y + 3.9, y + 9.9, 0.6, 5.4)
    grove = g if grove is None else grove.union(g)
    grove_plugs = p if grove_plugs is None else grove_plugs.union(p)
nfc_plug = box(NX - 4.0, NX + 4.0, NFC[2] - 8.2, NFC[2], NFC_TOP - 5.2, NFC_TOP - 0.4)

# spacers: M3 male-female (hex 5.5 as r 3.2), male end down through the board with a nut; ASL-12: □14 tape base,
# body taken as r 3.5 up to the board
spacers = None
for i, (x, y) in enumerate(HOLES, 1):
    top = ZBT + (SP_VEIN if i in VEIN_H else SP_NFC)
    for s in (cyl_z(x, y, 3.2, ZBT, top), cyl_z(x, y, 1.5, ZBT - MALE, ZBT), cyl_z(x, y, 3.2, ZB - NUT, ZB)):
        spacers = s if spacers is None else spacers.union(s)
asl = None
for x, y in ASL:
    s = box(x - 7.0, x + 7.0, y - 7.0, y + 7.0, 0, 1.0).union(cyl_z(x, y, 3.5, 1.0, ZB))
    asl = s if asl is None else asl.union(s)

vein = rbox(*VEIN, VEIN_Z0, VEIN_Z0 + 15.0, 2.0)
nfc = rbox(*NFC, NFC_Z0, NFC_TOP, 1.5)

# ---- machining ---------------------------------------------------------------------------------------------
VEIN_WIN = (VEIN[0] - 0.2, VEIN[1] + 0.2, VEIN[2] - 0.2, VEIN[3] + 0.2, 2.2)
SPK_HOLES = [(SPK[0] + dx, SPK[1] + dy) for dx, dy in ((0, 0), (3.5, 0), (-3.5, 0), (1.75, 3.0), (-1.75, 3.0),
                                                       (1.75, -3.0), (-1.75, -3.0))]
cover_cut = rbox(*VEIN_WIN[:4], CEIL - 1, TOP + 1, VEIN_WIN[4])
for x, y in SPK_HOLES:
    cover_cut = cover_cut.union(cyl_z(x, y, 1.0, CEIL - 1, TOP + 1))
cover_cut = cover_cut.union(cyl_z(*MIC, 0.75, CEIL - 1, TOP + 1))
END_WALL = (OUT[2] - 1, IN[2] + 0.5)
end_cut = (box(DB9_X0 - 0.25, DB9_X1 + 0.25, *END_WALL, ZBT - 1.5, ZBT + 14.0)                 # DB9 hood
           .union(rbox(UX - 4.8, UX + 4.8, *END_WALL, UZ - 2.1, UZ + 2.1, 1.0))                # USB-C plug
           .union(cyl_y(21.5, *END_WALL, ZBT + 9.0, 3.5)))                                     # J7 cable
case = body.cut(cover_cut).cut(end_cut)

# ---- interference ------------------------------------------------------------------------------------------
checks = [('指静脈', vein), ('NFC', nfc), ('board', pcb), ('J3', j3), ('J3 plug', j3_plug), ('MAX3232', u1),
          ('DIP', sw1), ('WROOM', wroom), ('speaker', spk), ('USB-C', usb), ('Grove', grove),
          ('Grove plugs', grove_plugs), ('NFC Grove plug', nfc_plug), ('DB9 body', db9_body),
          ('DB9 flange', db9_flange), ('DB9 shell', db9_shell), ('DB9 posts', db9_posts), ('DB9 tails', db9_tails),
          ('spacers', spacers), ('ASL-12', asl), ('DB9 plug', db9_plug), ('USB plug', usb_plug)]
bad = []
for name, obj in checks:
    v = case.intersect(obj).val().Volume()
    print(f'interference case x {name:14s} = {v:.3f} mm3')
    if v > 0.01:
        bad.append(f'case/{name}')
mutual = [('指静脈', vein), ('NFC', nfc), ('spacers', spacers), ('ASL-12', asl), ('J3 plug', j3_plug), ('DIP', sw1),
          ('WROOM', wroom), ('speaker', spk), ('Grove', grove), ('Grove plugs', grove_plugs),
          ('NFC Grove plug', nfc_plug), ('DB9 body', db9_body), ('DB9 plug', db9_plug), ('USB plug', usb_plug)]
for i, (na, a) in enumerate(mutual):
    for nb, b in mutual[i + 1:]:
        v = a.intersect(b).val().Volume()
        if v > 0.01:
            print(f'interference {na} x {nb} = {v:.3f} mm3')
            bad.append(f'{na}/{nb}')
# the modules must stand clear of the board's parts, the vein module 13 above the board and the NFC 10
print('parts among themselves: ' + ('ok' if not any(not b.startswith('case/') for b in bad) else 'NG'))

# ---- 3D preview ------------------------------------------------------------------------------------------
cover = case.intersect(box(-31, 31, -44, 44, CEIL, TOP + 1))
shell = case.intersect(box(-31, 31, -44, 44, FLOOR - 1, CEIL))
parts = [
    ('shell', 'カバー(タカチ SW-85B、指静脈の窓・スピーカー/マイクの穴)', '#2b2f33', 0.45, 'shell', cover),
    ('nfc', 'NFC Unit(公式 CAD、M3 × 10 の上、カバーの裏に両面テープ)', '#f2f2ee', 1, 'mods',
     stl_at('nfc', NX, (NFC[2] + NFC[3]) / 2, NFC_Z0 + 2.8, TOP)),   # CAD z -2.8..5.2
] + vein_parts(VEIN, VEIN_Z0, along_y=True) + [
    ('pcb', 'ESP 基板 sw(52 × 76、VoiceS3R の回路入り)', '#1f7a4d', 1, 'mods', pcb),
    ('wroom', 'ESP32-S3-WROOM-1(アンテナは前の端)', '#9aa3ab', 1, 'mods', wroom),
    ('spk', 'スピーカー 13 × 13(カバーの穴の下)', '#202326', 1, 'mods', spk),
    ('j3', 'J3 MX1.25 4P(指静脈)', '#f1efe8', 1, 'mods', j3),
    ('j3plug', 'J3 プラグ(指静脈ケーブル)', '#e7e1cf', 1, 'mods', j3_plug),
    ('u1', 'U1 MAX3232', '#202326', 1, 'mods', u1),
    ('sw1', 'SW1 ストレート/クロス DIP', '#c0392b', 1, 'mods', sw1),
    ('usb', 'J5 USB-C', '#8a8f96', 1, 'mods', usb),
    ('grove', 'J6(NFC)/ J7(G38 / G39)Grove', '#f1efe8', 1, 'mods', grove),
    ('groveplug', 'Grove プラグ', '#c47f0e', 1, 'mods', grove_plugs),
    ('db9', 'J4 DB9 オス', '#8a8f96', 1, 'mods', db9_body.union(db9_flange).union(db9_shell).union(db9_posts)),
    ('spacers', 'M3 オスメス+ナット(指静脈 12 / NFC 10)', '#c9a227', 1, 'mods', spacers),
    ('asl', 'タカチ ASL-12(床に貼るスナップ式スペーサー)', '#e8e4d8', 1, 'mods', asl),
    ('db9plug', 'DB9 プラグ(FC-1200 へ)', '#5c6166', 1, 'mods', db9_plug),
    ('usbplug', 'USB-C プラグ(Windows PC へ)', '#24292d', 1, 'mods', usb_plug),
    ('nfcplug', 'NFC 側 Grove プラグ', '#c47f0e', 1, 'mods', nfc_plug),
    ('lid', 'ボディ(タカチ SW-85B、端面に DB9 / USB-C / ケーブルの穴)', '#8fa09c', 0.9, 'lid', shell),
]
SUB = ('別案: VoiceS3R の回路を基板に載せ(ESP32-S3-WROOM-1 + ES8311 + スピーカー)、一番小さいタカチ SW-85B'
       '(60 × 40 × 85)に指静脈・NFC・DB9 を収める版。ドラッグで回転、ホイール/ピンチで拡大。')
DIMS = [('ケース', 'タカチ SW-85B(60 × 40 × 85、ABS、はめ込み式、¥350)。PF13-4-9(125 × 40 × 85)の半分以下の面積'),
        ('内側', '52.8 × 77.8 × 32.7(図面の有効寸法)、床 2.3、カバー 2 + 縁 5'),
        ('基板', 'ESP 基板 sw 52 × 76、床に貼る ASL-12 × 3 に差し込み(11.9)'),
        ('モジュール', '指静脈は M3 × 12(上面に VHB テープ)、NFC は M3 × 10 の上(基板の下でナット止め)'),
        ('カバーの穴', '指静脈(外形 + 0.2、3.8 突き出す)・スピーカー φ2 × 7・マイク φ1.5'),
        ('端面(-y)', 'DB9 のフードが入る角穴・USB-C プラグの穴・J7 ケーブルの穴'),
        ('NFC', '右、Grove を端面側に向けてカバーの裏に付ける(窓なし)')]
NOTE = ('ケースはタカチの外形図(SW-85□)からの簡略形状です(床のリブの高さは図面に無いので 2.0 と仮定、'
        'カバーの縁の下 32.7 から上は全部ふさがっているとして安全側に見ている)。NFC Unit の形は M5Stack 公式 STL'
        '(m5stack/M5_Hardware、Copyright (c) 2021 M5Stack、MIT License)、指静脈の外形は公式値(細部は写真からのイメージ)、'
        '基板上の部品は KiCad のフットプリント寸法からの簡略形状、指静脈のコネクタ位置は未確定。単位 mm。')
write_page('station-sw', 'SW ' + REV, parts, SUB, DIMS, NOTE, TOP)

if bad:
    raise SystemExit('interference: ' + ', '.join(bad))
