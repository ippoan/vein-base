"""Vein Unit: the finger vein module alone in a small Takachi case, like an M5Stack Unit, so the only cable that leaves
is a Grove cable (to a PortABC PORT.C, 5 V) and the module's own cable stays inside, a few cm long, and never moves.
Two cases, one run each:
  python3 station/build_vein_unit.py cs    CS75N-B  35 × 75 × 12 (¥190): the module fills the case between its four
                                           screw posts; no board, the wires are spliced in the end pocket
  python3 station/build_vein_unit.py sic   SIC5-9-2B 45 × 90 × 20 (¥270): a board as large as the inside on the
                                           four M2 bosses carries the module, the Grove socket and the LDO; the
                                           module's cable runs along its side to J1 (MX1.25 4P) beside its middle
Each writes the 3D preview site/vein-unit-<variant>/index.html and fails if the case collides with the module or the
parts inside.

Coordinates: x along the case (the module's cable end at -x), y across, z = 0 on the desk; origin = centre.
Cases: simplified from numbers measured on Takachi's STP (CS75N-B.stp, SIC5-9-2B.stp, takachi-el.co.jp, 2026-09;
nobody may redistribute them), with the inside taken a little smaller than measured (conservative).
Module: 59 × 26 × 15 (Waveshare); its cable leaves the end face of the flat window's end, low and level (Waveshare's
photo), with an MX1.25 9P plug; the far end of the supplied cable is Dupont female. UART use needs pins 3..6 only
(3.3V, GND, RXD, TXD, wiki). The kit's cable 4 (MX1.25 9P to 4P) serves the USB path with the kit's 3.3 V adapter
board; its four crimped terminals are moved in the 9P housing to 3, 4, 5, 6 (nothing is cut) and its 4P end goes
into J1 on the board (sic). For cs the kit's cable 6 (9P to 2.54, 200 mm) is cut about 3 cm from the plug and the
four wires are soldered to the Grove cable. 5 V from the Grove goes through a 3.3 V LDO and RXD / TXD go to the
Grove's G5 / G6.
"""
import sys
from shapes import box, rbox, cyl_z, union, vein_parts, write_page
import cadquery as cq

REV = 'vu9'
VARIANT = sys.argv[1] if len(sys.argv) > 1 else 'cs'
VEIN = (-29.5, 29.5, -13.0, 13.0)                 # 59 × 26, centred (sic moves it, see there)


def cyl_x(y, z, r, x0, x1):
    return cq.Workplane('YZ').workplane(offset=x0).center(y, z).circle(r).extrude(x1 - x0)


if VARIANT == 'cs':
    # ---- Takachi CS75N-B (measured on the STP) ---------------------------------------------------------------
    # body 0..10.2 (floor 1.8, walls ~1.5: inside 31.7 × 71.8 at the top, 30 × 70 at the floor), cover plate
    # 10.2..12 with a skirt inside the walls; four screw posts r 2.25 at (±31.75, ±11.75) the full height; locating
    # pegs 0.8 wide hanging from the cover to z 6.8 at |y| 11..11.8 and 13.1..13.9 (x ±1, ±27..29).
    # The catalogue's 26.6 × 59 is between the pegs and between the posts.
    NAME, CASE, PRICE = 'CS75N-B', '35 × 75 × 12', '¥190'
    L, W, H, ZC, FLOOR = 75.0, 35.0, 12.0, 10.2, 1.8
    IX, IY = 35.0, 15.0
    body = rbox(-L / 2, L / 2, -W / 2, W / 2, 0, ZC, 3.0).cut(box(-IX, IX, -IY, IY, FLOOR, ZC + 1))
    cover = rbox(-L / 2, L / 2, -W / 2, W / 2, ZC, H, 3.0)
    posts = union(*[cyl_z(sx * 31.75, sy * 11.75, 2.25, FLOOR, ZC) for sx in (1, -1) for sy in (1, -1)])
    pegs = union(*[box(x0, x1, y0, y1, 6.8, ZC) for x0, x1 in ((-1.03, 1.03), (26.94, 29.04), (-29.04, -26.94))
                   for y0, y1 in ((13.14, 13.94), (-13.94, -13.14))])
    cover = cover.union(posts).union(pegs)
    VEIN_Z0 = FLOOR + 0.5                         # on VHB 0.5: top 17.3, 5.3 proud
    STAND = None
    # the plug sits in the end pocket between the two -x posts (y ±9.5, 5.5 deep); the four wires, the LDO and the
    # Grove cable are soldered and heat-shrunk there, the Grove cable leaves through a hole in the end wall
    Z_P = VEIN_Z0 + 1.5
    plug = box(VEIN[0] - 2.6, VEIN[0], -7.2, 7.2, Z_P, Z_P + 3.5)
    splice = box(-IX + 0.2, VEIN[0] - 2.8, -8.0, 8.0, FLOOR + 0.3, ZC - 1.0)
    grove_cable = cyl_x(0.0, 5.5, 2.3, -L / 2 - 15.0, -IX + 0.2)
    hole = cyl_x(0.0, 5.5, 2.6, -L / 2 - 1, -IX + 0.5)
    body = body.cut(hole)
    inner = [('plug', 'MX1.25 9P プラグ(付属ケーブル)', '#e7e1cf', plug),
             ('splice', '4 本の線 + LDO 3.3V をはんだ付けして熱収縮チューブ(端のすき間)', '#3a4046', splice),
             ('grovecable', 'Grove ケーブル(直付け、PortABC の PORT.C へ)', '#c47f0e', grove_cable)]
    DIMS = [('ケース', f'タカチ {NAME}({CASE}、ABS、ねじ 4 本、{PRICE})'),
            ('中', '31.7 × 71.8 × 8.4(ねじの柱の間 59、STP の実測)'),
            ('加工', '蓋に指静脈の窓(外形 + 0.2、蓋の位置決めの突起ごと切る)、端に Grove ケーブルの穴 ⌀5.2'),
            ('指静脈', '床に VHB 0.5 で貼る、横は壁とねじの柱で止まる、蓋から 5.3 突き出す'),
            ('配線', 'プラグは端のねじの柱の間(奥行き 5.5)。付属ケーブルの 3・4・5・6 と Grove ケーブルを LDO をはさんではんだ付け')]
    SUB = ('指静脈モジュールを最小のタカチ CS75N-B(35 × 75 × 12)にはめ込み、Grove ケーブルを直接出す案(基板なし)。')
else:
    # ---- Takachi SIC5-9-2B (measured on the STP) -------------------------------------------------------------
    # body 0..17.5 (floor 2.0, walls ~2.2, inside ±39.8 × ±20.3 with R10 ends), cover plate 17.5..20 with a 1.0
    # lip down to z 15 inside the walls; four PCB bosses r 1.95 at (±33, ±12.5), floor to z 6.
    NAME, CASE, PRICE = 'SIC5-9-2B', '45 × 90 × 20', '¥270'
    VEIN = (-29.5, 29.5, -15.0, 11.0)             # 2.0 off centre: a 9.1 gap on +y for J1, 5.1 on -y
    L, W, H, ZC, FLOOR = 90.0, 45.0, 20.0, 17.5, 2.0
    IX, IY, IR = 39.6, 20.1, 10.0
    body = rbox(-L / 2, L / 2, -W / 2, W / 2, 0, ZC, 12.5).cut(rbox(-IX, IX, -IY, IY, FLOOR, ZC + 1, IR))
    cover = rbox(-L / 2, L / 2, -W / 2, W / 2, ZC, H, 12.5).union(
        rbox(-IX, IX, -IY, IY, 15.0, ZC, IR).cut(rbox(-IX + 1.0, IX - 1.0, -IY + 1.0, IY - 1.0, 14, ZC + 1, IR - 1.0)))
    bosses = union(*[cyl_z(sx * 33.0, sy * 12.5, 1.95, FLOOR, 6.0) for sx in (1, -1) for sy in (1, -1)])
    body = body.union(bosses)
    # a board as large as the inside, screwed onto the four M2 bosses: the module on it with VHB, the Grove socket and
    # the LDO in the +x end; the module's cable (kit cable 4, 9P re-pinned to 3..6) turns from its plug at -x into the
    # 7 wide gap beside the module and plugs straight into J1 (MX1.25 4P right angle, Molex 53261-0471 as J3 on the
    # station board, opening to -x) in that gap beside the module's middle: the only bend is the U-turn in the -x end
    # (vu4: J1 next to the plug, no room to bend; vu6: J1 at the +x end, ~95 of the cable's ~100; vu7: top entry,
    # a right-angle bend at the crimps in the 2.9 under the cover)
    BRD_T = 1.6
    Z_BRD, Z_BT = 6.0, 6.0 + BRD_T                # on the boss tops
    board = rbox(-IX + 0.6, IX - 0.6, -IY + 0.6, IY - 0.6, Z_BRD, Z_BT, IR - 0.6)
    screws = union(*[cyl_z(sx * 33.0, sy * 12.5, 1.9, Z_BT, Z_BT + 1.4) for sx in (1, -1) for sy in (1, -1)])
    for sx in (1, -1):
        for sy in (1, -1):
            board = board.cut(cyl_z(sx * 33.0, sy * 12.5, 1.1, Z_BRD - 1, Z_BT + 1))
    VEIN_Z0 = Z_BT + 0.5                          # on VHB 0.5: 8.1, top 23.1, 3.1 proud
    STAND = None
    GX1 = IX - 0.6
    grove = box(GX1 - 7.0, GX1, -4.0, 4.0, Z_BT, Z_BT + 5.8)
    grove_plug = box(GX1, L / 2 + 10.0, -3.9, 3.9, Z_BT + 0.4, Z_BT + 5.4)
    ldo = box(33.0, 36.0, -8.5, -5.5, Z_BT, Z_BT + 1.2)
    Z_P = VEIN_Z0 + 1.5
    YC = (VEIN[2] + VEIN[3]) / 2
    plug = box(VEIN[0] - 2.6, VEIN[0], YC - 7.2, YC + 7.2, Z_P, Z_P + 3.5)
    # 53261-0471 is 7.95 wide over its metal fitting nails (3.75 + 4.2), which stand up the housing's ends: it needs
    # the 9.1 gap the module's 2.0 offset leaves (the other side keeps 5.1)
    J1Y = (VEIN[3] + 0.6, VEIN[3] + 0.6 + 7.95)
    j1 = box(0.0, 5.5, *J1Y, Z_BT, Z_BT + 3.4)                          # opening at x = 0
    JC = (J1Y[0] + J1Y[1]) / 2
    j1_plug = box(-5.5, 0.0, JC - 2.5, JC + 2.5, Z_BT + 0.4, Z_BT + 3.0)
    zr = (Z_BT + 1.2, Z_BT + 4.0)                                       # the 4-wire cable in the gap, level
    cable = union(box(-35.0, VEIN[0] - 2.6, YC - 1.4, YC + 1.4, Z_P, Z_P + 2.8),  # out of the module's plug to -x,
                  box(-35.0, -33.2, YC - 1.4, JC + 1.4, zr[0], Z_P + 2.8),     # the U-turn in the -x end,
                  box(-35.0, -5.5, JC - 1.4, JC + 1.4, *zr))                     # straight along the gap into J1
    hole = box(IX - 0.5, L / 2 + 1, -4.6, 4.6, Z_BT - 0.4, Z_BT + 6.2)
    body = body.cut(hole)
    inner = [('plug', 'MX1.25 9P プラグ(付属ケーブル)', '#e7e1cf', plug),
             ('cable', '付属ケーブル④(9P → 4P、9P 側の端子を 3・4・5・6 に差し替え)、指静脈の脇を通す', '#3a4046', cable),
             ('j1', 'J1 MX1.25 4P 横向き(Molex 53261-0471、金具込み 7.95 幅、指静脈の脇の真ん中、口は -x)', '#f1efe8', j1),
             ('j1plug', '④ の 4P プラグ', '#e7e1cf', j1_plug),
             ('board', '基板(中いっぱい、M2 ボス 4 本にねじ止め、指静脈を VHB で載せる)', '#1f7a4d', board),
             ('screws', 'M2 なべねじ × 4', '#9aa0a6', screws),
             ('grove', 'Grove ソケット(HY2.0 4P、横向き)', '#f1efe8', grove),
             ('ldo', 'LDO 5V→3.3V とコンデンサ', '#202326', ldo),
             ('groveplug', 'Grove プラグ(PortABC の PORT.C へ)', '#c47f0e', grove_plug)]
    DIMS = [('ケース', f'タカチ {NAME}({CASE}、ABS 光沢、はめ込み式、{PRICE})'),
            ('中', '79.6 × 40.6 × 15.5(端は R10、STP の実測)、床に M2 用ボス 4 本(66 × 25、高さ 4)'),
            ('加工', '蓋に指静脈の窓(外形 + 0.2)、端に Grove の穴 9.2 × 6.6'),
            ('基板', f'{2 * (IX - 0.6):.1f} × {2 * (IY - 0.6):.1f}(R{IR - 0.6:g})、ボスの上に M2 × 4 で留める、JLCPCB で実装'),
            ('指静脈', '基板の上に VHB 0.5 で貼る、蓋から 3.1 突き出す。J1 の側へすき間 9.1 を空けるため中心から 2.0 ずらす'),
            ('配線', '付属ケーブル④(9P → 4P)の 9P 側の端子を 3・4・5・6 に差し替え、指静脈の脇(すき間 7)の真ん中の横向き J1 へまっすぐ挿す(切らない、曲げは -x 端の U ターンだけ)。J1 から LDO・Grove へは基板の配線')]
    SUB = ('指静脈モジュールをタカチ SIC5-9-2B(45 × 90 × 20)に入れ、中いっぱいの基板に載せて端の Grove ソケット 1 口で PortABC につなぐ案。')

VEIN_WIN = (VEIN[0] - 0.2, VEIN[1] + 0.2, VEIN[2] - 0.2, VEIN[3] + 0.2, 2.2)
cover = cover.cut(rbox(*VEIN_WIN[:4], FLOOR + 3, H + 2, VEIN_WIN[4]))
vein = rbox(*VEIN, VEIN_Z0, VEIN_Z0 + 15.0, 2.0)

# ---- interference ----------------------------------------------------------------------------------------
case = body.union(cover)
bad = []
for name, obj in [('指静脈', vein)] + [(k, s) for k, _, _, s in inner] + ([('stand', STAND)] if STAND else []):
    v = case.intersect(obj).val().Volume()
    print(f'interference case x {name:10s} = {v:.3f} mm3')
    if v > 0.01:
        bad.append(name)
for k, _, _, s in inner:
    if k in ('plug', 'grovecable', 'groveplug', 'grove'):
        continue
    v = vein.intersect(s).val().Volume()
    if v > 0.01:
        print(f'interference 指静脈 x {k} = {v:.3f} mm3')
        bad.append(f'指静脈/{k}')

# ---- 3D preview ------------------------------------------------------------------------------------------
parts = [('shell', f'蓋(タカチ {NAME}、指静脈の窓)', '#2b2f33', 0.45, 'shell', cover)] + vein_parts(VEIN, VEIN_Z0) + \
    [(k, l, c, 1, 'mods', s) for k, l, c, s in inner] + \
    [('lid', f'本体(タカチ {NAME})', '#3a3f44', 0.55, 'lid', body)]
NOTE = ('ケースはタカチ公式 STP を実測した数値からの簡略形状(STP は再配布しない)。指静脈の外形は公式値、細部は製品写真を見て描いた'
        'イメージ、ケーブルは写真どおり平らな窓の側の端面から水平に出る。ピン配置は Waveshare の Wiki による。基板と部品は仮の形。単位 mm。')
write_page(f'vein-unit-{VARIANT}', f'指静脈 Unit {REV} {NAME}', parts, SUB + 'ドラッグで回転、ホイール/ピンチで拡大。', DIMS, NOTE,
           VEIN_Z0 + 15.0, tz='-10')

if bad:
    raise SystemExit('interference: ' + ', '.join(bad))
