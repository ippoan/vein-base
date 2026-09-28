"""Vein Station SW75 (alternative, smallest): the station in a Takachi SW-75B (50 × 30 × 75, ABS, snap-in cover, ¥200)
with the Unit NFC left outside on its Grove cable, and the Atom VoiceS3R's circuit on the board (pcb/station_esp_board,
`build_board.py sw75`, 40.8 × 68.1). A third of the PF13-4-9's desk area and 10 lower.
Run from the repository root:  python3 station/build_station_sw75.py
Writes the 3D preview site/station-sw75/index.html and fails if the case collides with a module, plug, spacer or the
board, or two of those collide with each other.

Case coordinates = the board's: x across the 50 side, y along the 75 side, origin = case centre, z = 0 at the inside
of the floor. DB9 and USB-C on the +x side, both Groves on the +y end, the WROOM's antenna to the -x wall.
The case is written from Takachi's drawing (SW-75□, 2024/07/16, DXF/PDF on takachi-el.co.jp): outside 50 × 75 R2 × 30,
floor 2, cover 2 thick with a 5 deep skirt, no floor ribs; inside 44.8 × 69.8 at the floor leaning in to the effective
42.8 × 67.8 at 23 (the skirt's lower edge), modelled as that loft; everything from 23 up to the cover's top face at 28 is
taken as solid (so the model is on the safe side).
Stack (z): Takachi ASR-7 stick-on tapped bosses on the floor (□20 tape base) under H1 / H4 | board 7.2..8.8 |
vein module on M3 × 6 spacers (male-female into the ASR-7 at H1 / H4, female-female with a screw from below at H2 / H3)
+ 1.0 VHB tape, 15.8..30.8: 2.8 proud of the cover through a window of its outline + 0.2 | DB9, USB-C and the Grove plugs
through cut-outs in the walls. The speaker and the mic sit beside the vein module under holes in the cover.
"""
import cadquery as cq
from shapes import box, rbox, cyl_z, cyl_y, stl_at, vein_parts, write_page

REV = 'sw75b'

# ---- case (Takachi SW-75B, from the drawing) --------------------------------------------------------------
OUT = (-25.0, 25.0, -37.5, 37.5)
FLOOR, CEIL, TOP = -2.0, 23.0, 28.0
inside = (cq.Workplane('XY').rect(44.8, 69.8).workplane(offset=CEIL).rect(42.8, 67.8).loft())
body = rbox(*OUT, FLOOR, TOP, 2.0).cut(inside)

# ---- board (pcb/station_esp_board, build_board.py sw75) and what stands on it: keep these lists together with it ----
BX0, BX1, BY0, BY1 = -20.4, 20.4, -33.8, 34.3
HOLES = [(-6.3, -15.0), (1.2, -19.5), (-10.9, 20.5), (1.3, 20.5)]      # H1..H4 vein spacers
ASR = (1, 4)                                                            # the ones on ASR-7 bosses
DB9_BY = 0.0                                                            # DB9 on the +x edge
USB = (17.35, 26.0)                                                     # opening +x
WROOM = (-7.65, 0.0)                                                    # antenna to -x
J3 = (-8.35, -22.5)                                                     # opening -y, under the vein socket
GROVE = [('J6 NFC', -7.75, 29.2), ('J7 G38/G39', 5.45, 29.2)]           # openings +y (the end wall)
SPK, MIC = (13.2, -24.0), (8.6, -11.8)                                  # speaker centre, mic sound port
U1 = (2.4, -28.4)                          # MAX3232, not turned

ZB = 7.2                                   # ASR-7
ZBT = ZB + 1.6
SP_VEIN, TAPE = 6.0, 1.0
VEIN = (-21.2, 4.8, -26.5, 32.5)           # 26 across, 59 along y, the socket end at -y, 8 from the end wall
                                           # (the cable's C loop down to J3)
VEIN_Z0 = ZBT + SP_VEIN + TAPE             # 15.8, top 30.8

pcb = box(BX0, BX1, BY0, BY1, ZB, ZBT)
for x, y in HOLES:
    pcb = pcb.cut(cyl_z(x, y, 1.6, ZB - 1, ZBT + 1))


def on(x0, x1, y0, y1, z0, z1):
    """Box on the board, z from the board's top face."""
    return box(x0, x1, y0, y1, ZBT + z0, ZBT + z1)


def cyl_x(x0, x1, y, z, r):
    return cq.Workplane('YZ').workplane(offset=x0).center(y, z).circle(r).extrude(x1 - x0)


# DB9 male RA turned to +x (as build_station_pf.py, from the KiCad footprint)
db9_body = on(BX1 - 10.5, BX1 - 0.5, DB9_BY - 15.0, DB9_BY + 15.0, 0, 12.5)
db9_flange = on(BX1, BX1 + 1.0, DB9_BY - 15.4, DB9_BY + 15.4, 0, 12.5)
db9_shell = on(BX1 + 1.0, BX1 + 7.0, DB9_BY - 8.5, DB9_BY + 8.5, 2.0, 10.5)
db9_tails = on(BX1 - 8.5, BX1 - 3.0, DB9_BY - 6.5, DB9_BY + 6.5, -4.6, -1.6)
DB9_ZC = ZBT + 6.25
db9_posts = cyl_x(BX1 + 1.0, BX1 + 5.0, DB9_BY - 12.5, DB9_ZC, 2.5).union(cyl_x(BX1 + 1.0, BX1 + 5.0, DB9_BY + 12.5, DB9_ZC, 2.5))
DB9_Y0, DB9_Y1 = DB9_BY - 15.4, DB9_BY + 15.4
db9_plug = box(BX1 + 1.8, 80, DB9_Y0 + 0.25, DB9_Y1 - 0.25, ZBT - 0.75, ZBT + 13.25)   # stops 0.8 short of the flange

# USB-C receptacle turned to +x (front 0.6 past the edge) and the Sanwa KU-CCP L plug
UF = BX1 + 0.6
UZ = ZBT + 1.63
usb = on(UF - 7.3, UF, USB[1] - 4.47, USB[1] + 4.47, 0, 3.26)
usb_plug = box(UF, UF + 6.5, USB[1] - 4.2, USB[1] + 4.2, UZ - 1.5, UZ + 1.5).union(
    box(UF + 6.5, UF + 24.2, USB[1] - 6.0, USB[1] + 6.0, UZ - 3.5, UZ + 3.5))

j3 = on(J3[0] - 5.0, J3[0] + 5.0, J3[1] - 3.1, J3[1] + 3.7, 0, 3.4)
j3_plug = on(J3[0] - 3.0, J3[0] + 3.0, J3[1] - 9.1, J3[1] - 3.1, 0.3, 3.1)
# the vein cable (MX1.25 9P -> 4P, approx 3 × 1 flat bundle): level out of the module's socket at the -y end, one C loop
# down in the gap before the end wall and back +y into J3's plug
VCX = (J3[0] - 1.5, J3[0] + 1.5)
YS, YP, YL = VEIN[2], J3[1] - 9.1, VEIN[2] - 7.0          # socket face, plug's back, the loop's far side
ZS, ZP = VEIN_Z0 + 3.2, ZBT + 1.7                         # socket and plug centre heights
vein_cable = (box(*VCX, YL, YS, ZS - 0.5, ZS + 0.5).union(box(*VCX, YL, YL + 1.0, ZP - 0.5, ZS + 0.5))
              .union(box(*VCX, YL, YP, ZP - 0.5, ZP + 0.5)))
u1 = on(U1[0] - 1.95, U1[0] + 1.95, U1[1] - 5.0, U1[1] + 5.0, 0, 1.75)
wroom = on(WROOM[0] - 12.75, WROOM[0] + 12.75, WROOM[1] - 9.0, WROOM[1] + 9.0, 0, 3.1)
spk = on(SPK[0] - 6.5, SPK[0] + 6.5, SPK[1] - 6.5, SPK[1] + 6.5, 0, 4.0)
grove = grove_plugs = None
for _, x, y in GROVE:
    g = on(x - 5.0, x + 5.0, y - 3.9, y + 3.9, 0, 6.0)
    p = on(x - 4.5, x + 4.5, y + 3.9, y + 12.0, 0.6, 5.4)          # through the end wall
    grove = g if grove is None else grove.union(g)
    grove_plugs = p if grove_plugs is None else grove_plugs.union(p)

# spacers: M3 × 6 (hex 5.5 as r 3.2) on the board; under it the male end into an ASR-7 (φ7 boss on a □20 tape
# base) at H1 / H4, a pan head screw (r 2.8 × 2) elsewhere
spacers = asr = None
for i, (x, y) in enumerate(HOLES, 1):
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
SPK_HOLES = [(SPK[0] + dx, SPK[1] + dy) for dx, dy in ((0, 0), (3.5, 0), (-3.5, 0), (1.75, 3.0), (-1.75, 3.0),
                                                       (1.75, -3.0), (-1.75, -3.0))]
cover_cut = rbox(*VEIN_WIN[:4], CEIL - 1, TOP + 1, VEIN_WIN[4])
for x, y in SPK_HOLES:
    cover_cut = cover_cut.union(cyl_z(x, y, 1.0, CEIL - 1, TOP + 1))
cover_cut = cover_cut.union(cyl_z(*MIC, 0.75, CEIL - 1, TOP + 1))
SIDE = (BX1 + 0.5, OUT[1] + 1)             # the +x wall
END = (BY1 - 0.5, OUT[3] + 1)              # the +y wall
wall_cut = (box(*SIDE, DB9_Y0 - 0.25, DB9_Y1 + 0.25, ZBT - 1.5, ZBT + 14.0)                   # DB9 hood
            .union(rbox(*SIDE, USB[1] - 4.8, USB[1] + 4.8, UZ - 2.1, UZ + 2.1, 1.0)))          # USB-C plug
for _, x, _y in GROVE:
    wall_cut = wall_cut.union(rbox(x - 5.0, x + 5.0, *END, ZBT + 0.1, ZBT + 5.9, 0.8))         # Grove plugs
case = body.cut(cover_cut).cut(wall_cut)

# ---- interference ------------------------------------------------------------------------------------------
checks = [('指静脈', vein), ('vein cable', vein_cable), ('board', pcb), ('J3', j3), ('J3 plug', j3_plug), ('MAX3232', u1), ('WROOM', wroom),
          ('speaker', spk), ('USB-C', usb), ('Grove', grove), ('Grove plugs', grove_plugs), ('DB9 body', db9_body),
          ('DB9 flange', db9_flange), ('DB9 shell', db9_shell), ('DB9 posts', db9_posts), ('DB9 tails', db9_tails),
          ('spacers', spacers), ('ASR-7', asr), ('DB9 plug', db9_plug), ('USB plug', usb_plug)]
bad = []
for name, obj in checks:
    v = case.intersect(obj).val().Volume()
    print(f'interference case x {name:14s} = {v:.3f} mm3')
    if v > 0.01:
        bad.append(f'case/{name}')
mutual = [('指静脈', vein), ('vein cable', vein_cable), ('spacers', spacers), ('ASR-7', asr), ('J3 plug', j3_plug), ('WROOM', wroom),
          ('speaker', spk), ('Grove', grove), ('Grove plugs', grove_plugs), ('DB9 body', db9_body),
          ('DB9 tails', db9_tails), ('DB9 plug', db9_plug), ('USB plug', usb_plug)]
for i, (na, a) in enumerate(mutual):
    for nb, b in mutual[i + 1:]:
        v = a.intersect(b).val().Volume()
        if v > 0.01:
            print(f'interference {na} x {nb} = {v:.3f} mm3')
            bad.append(f'{na}/{nb}')
print('parts among themselves: ' + ('ok' if not any(not b.startswith('case/') for b in bad) else 'NG'))

# ---- 3D preview ------------------------------------------------------------------------------------------
cover = case.intersect(box(-26, 26, -39, 39, CEIL, TOP + 1))
shell = case.intersect(box(-26, 26, -39, 39, FLOOR - 1, CEIL))
NFC_Y = OUT[3] + 14.0 + 24.0               # the Unit NFC on the desk in front of the +y end, its Grove towards the case
parts = [
    ('shell', 'カバー(タカチ SW-75B、指静脈の窓・スピーカー/マイクの穴)', '#2b2f33', 0.45, 'shell', cover),
    ('nfc', 'NFC Unit(公式 CAD、箱の外に置く。Grove ケーブルで J6 へ)', '#f2f2ee', 1, 'mods',
     stl_at('nfc', 0.0, NFC_Y, FLOOR + 2.8, TOP)),   # CAD z -2.8..5.2
] + vein_parts(VEIN, VEIN_Z0, along_y=True) + [
    ('pcb', 'ESP 基板 sw75(40.8 × 68.1、VoiceS3R の回路入り)', '#1f7a4d', 1, 'mods', pcb),
    ('wroom', 'ESP32-S3-WROOM-1(アンテナは左の壁)', '#9aa3ab', 1, 'mods', wroom),
    ('spk', 'スピーカー 13 × 13(カバーの穴の下)', '#202326', 1, 'mods', spk),
    ('j3', 'J3 MX1.25 4P(指静脈)', '#f1efe8', 1, 'mods', j3),
    ('j3plug', 'J3 プラグ(指静脈ケーブル)', '#e7e1cf', 1, 'mods', j3_plug),
    ('veincable', '指静脈のケーブル(-y 端で C 字、おおよその通り道)', '#b04a2f', 1, 'mods', vein_cable),
    ('u1', 'U1 MAX3232', '#202326', 1, 'mods', u1),
    ('usb', 'J5 USB-C', '#8a8f96', 1, 'mods', usb),
    ('grove', 'J6(NFC)/ J7(G38 / G39)Grove', '#f1efe8', 1, 'mods', grove),
    ('groveplug', 'Grove プラグ(端面から外へ)', '#c47f0e', 1, 'mods', grove_plugs),
    ('db9', 'J4 DB9 オス(右の側面)', '#8a8f96', 1, 'mods', db9_body.union(db9_flange).union(db9_shell).union(db9_posts)),
    ('spacers', 'M3 × 6(指静脈、上面に VHB テープ)', '#c9a227', 1, 'mods', spacers),
    ('asr', 'タカチ ASR-7(床に貼るボス、H1 / H4 のスペーサーを受ける)', '#e8e4d8', 1, 'mods', asr),
    ('db9plug', 'DB9 プラグ(FC-1200 へ)', '#5c6166', 1, 'mods', db9_plug),
    ('usbplug', 'USB-C プラグ(Windows PC へ)', '#24292d', 1, 'mods', usb_plug),
    ('lid', 'ボディ(タカチ SW-75B、側面に DB9 / USB-C、端面に Grove の穴)', '#8fa09c', 0.9, 'lid', shell),
]
SUB = ('別案(最小): NFC を外に出し、タカチ SW-75B(50 × 30 × 75)に指静脈・DB9 と VoiceS3R の回路を載せた基板だけを'
       '収める版。ドラッグで回転、ホイール/ピンチで拡大。')
DIMS = [('ケース', 'タカチ SW-75B(50 × 30 × 75、ABS、はめ込み式)。PF13-4-9 の約 1/3 の面積、高さ 30'),
        ('内側', '床 44.8 × 69.8 → 縁の下 42.8 × 67.8、高さ 23(図面の有効寸法)'),
        ('基板', 'ESP 基板 sw75 40.8 × 68.1、0402・片面実装。床に貼る ASR-7 × 2 にスペーサーのオス側でねじ込む(7.2)'),
        ('指静脈', 'M3 × 6 の上に VHB テープ、カバーから 2.8 突き出す。ケーブルは -y 端で下へ C 字に曲げて J3(同じ -y 向き)へ'),
        ('NFC', '箱の外(Grove ケーブルで J6 へ)'),
        ('カバーの穴', '指静脈(外形 + 0.2)・スピーカー φ2 × 7・マイク φ1.5'),
        ('側面・端面', '+x の側面に DB9 の角穴と USB-C の穴、+y の端面に Grove × 2 の角穴')]
NOTE = ('ケースはタカチの外形図(SW-75□)からの簡略形状です(縁の下 23 から上は全部ふさがっているとして安全側に見ている)。'
        'NFC Unit の形は M5Stack 公式 STL(m5stack/M5_Hardware、Copyright (c) 2021 M5Stack、MIT License)、'
        '指静脈の外形は公式値(細部は写真からのイメージ)、基板上の部品は KiCad のフットプリント寸法からの簡略形状、'
        '指静脈のコネクタ位置は未確定。単位 mm。')
write_page('station-sw75', 'SW75 ' + REV, parts, SUB, DIMS, NOTE, TOP)

if bad:
    raise SystemExit('interference: ' + ', '.join(bad))
