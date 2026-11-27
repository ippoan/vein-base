"""3D preview of the FP008 USB board (f13: the board grown above the module, a 1/4" mount hole with its nut, J1 / J2 at the top edge for straight plugs; f12: the heat sink drawn; f11: round holes for the supplied nominal 2 self-tapping screws; f10: slots; f9: the parts face the module, a notch in the bottom edge for the L adapters; J3 vertical) (site/fp008-board/) from the STEP with parts that the CI writes
(fab/fp008/fp008_board_v<VER>_full.step, KiCad library models fetched by tools/kicad_3d_models.py) and the CI's
pos.csv. The two USB-C (HRO TYPE-C-31-M-12) have no model in the KiCad library and are drawn as plain boxes.
    python3 pcb/fp008_board/build_3d.py      # from the repo root, with CadQuery (after the board's CI step)
"""
import csv, math, os, sys
import cadquery as cq

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'station'))
from shapes import VER, write_page  # noqa: E402

FAB = os.path.join(ROOT, 'fab', 'fp008')
STEP = os.path.join(FAB, f'fp008_board_v{VER}_full.step')
OX, OY = 100.0, 100.0                 # build_board.py's page offset: board (x, y) = KiCad (X - 100, -(Y - 100))
T = 1.6                               # board thickness; the STEP has the board on z 0..1.6
# HRO TYPE-C-31-M-12 body in footprint coordinates (y toward the opening): 8.94 wide, 7.35 long, 3.26 high,
# the front 0.3 past the board edge (the footprint origin is 3.05 in from the edge)
USB_W, USB_L, USB_H, USB_FRONT = 8.94, 7.35, 3.26, 3.35

pos = {r['Ref']: (float(r['PosX']) - OX, float(r['PosY']) + OY, float(r['Rot']))
       for r in csv.DictReader(open(os.path.join(FAB, 'pos.csv')))}
top = cq.importers.importStep(STEP).val()
items = [s.translate(cq.Vector(-OX, OY, 0)) for s in (list(top) if hasattr(top, '__iter__') else [top])]
board = max(items, key=lambda s: s.BoundingBox().xlen * s.BoundingBox().ylen)
groups = {'ics': [], 'conn': [], 'pass': [], 'led': []}
for s in items:
    if s is board:
        continue
    c = s.Center()
    ref = min(pos, key=lambda r: (pos[r][0] - c.x) ** 2 + (pos[r][1] - c.y) ** 2)
    groups['ics' if ref[0] in 'UY' else 'conn' if ref[0] == 'J' else 'led' if ref[0] == 'D' else 'pass'].append(s)
for k, v in groups.items():
    assert v, f'no {k} in the STEP (were the 3D models fetched?)'


def flip(s):
    """f4: the parts (F) face the module. Board (KiCad) coordinates -> the page's: turned 180 deg about y, so z = up =
    out of the module's back, the board on z 0..1.6 with its F face on z = 0 and the parts below it, inside the module."""
    return s.rotate((0, 0, 0), (0, 1, 0), 180).translate((0, 0, T))


def usb(ref):
    """The USB-C body at its footprint: the opening on the footprint's -y (KiCad), turned with the part."""
    x, y, rot = pos[ref]
    b = cq.Workplane().box(USB_W, USB_L, USB_H, centered=(True, False, False)).translate((0, -USB_FRONT, T))
    return flip(b.rotate((0, 0, 0), (0, 0, 1), rot).translate((x, y, 0)))


def comp(lst):
    return cq.Workplane().add(cq.Compound.makeCompound([flip(s) for s in lst]))


bb = board.BoundingBox()
size = (bb.xlen, bb.ylen)

# ---- the board as the FP008's back lid, parts inside (f4). z = up = out of the module's back: the board on z 0..1.6,
# its parts below z = 0 in the module's back; the module's four rear screw holes take nominal 2 x 8 self-tapping screws through the bracket and the lid (f11; M3 x 6 in f8..f10).
# f12: J1 at the bottom edge (opening -y), J2 at the top edge (opening +y), each at its notch (world +x = the board's -x: seen from behind);
# the cables take an L-shaped (90 deg) adapter at the plug. The module's inside (user's caliper, 2026-11-26, from the
# rim the board sits on): the 8P socket's top 10.9 down (drawn as a recess CAV deep), in the middle; a heat sink at the
# bottom edge's left (board x -14.4..-4.7, y -14.2..-5.6, its place from a straight photo scaled on the four holes, +-1)
# whose top is HS_DEPTH 4.4 down. The bosses at the screw holes are guesses.
FW, FH, FL = 59.54, 38.54, 2.2                     # flange (manual 1.3.1)
BW, BH, BD = 55.45, 34.45, 15.35                   # rear body
R_BODY, R_FLANGE = 12.4, 14.0                      # corner radii (guess from the drawing)
HOLES = [(sx * 18.35, sy * 12.5) for sx in (-1, 1) for sy in (-1, 1)]    # = build_board.py's HX / HY (f11, user's caliper
# 2026-11-26: A ~36.4..36.9, y ~25); the board's holes 2.4 take a 2.0 screw +-0.2
CAV, WALL, BOSS = 10.9, 1.4, 3.0                   # the recess down to the 8P socket's top, the rear wall (measured 2026-11-26); boss radius (guess)
HS_DEPTH = 4.4                                     # the heat sink's top under the rim (measured): parts <= 3.3 clear it by 1.1
HS = (-14.4, -4.7, -14.2, -5.6)                    # = build_board.py's HS (board x0, x1, y0, y1)
MOUNT = (0.0, 25.5)                                # = build_board.py's MOUNT (f13): the clip mount's 1/4"-20 stud, a nut on F
NUT_AF, NUT_T, STUD_R, STUD_TIP = 11.1, 4.0, 6.35 / 2, 6.0   # thin nut across flats / thick; the stud, its tip under the board
SOCKET = (-7.0, 7.0, 0.4, 4.4)                     # the module's 8P socket (board x0, x1, y0, y1; f12, from the photo; the
# gap from the heat sink's edge to the socket's, measured 6.3 (user, 2026-11-26), the photo gave 6.0: within its +-1)


def rrect(w, h, r, z0, z1):
    return cq.Workplane().sketch().rect(w, h).vertices().fillet(r).finalize().extrude(z1 - z0).translate((0, 0, z0))


fp = (rrect(BW, BH, R_BODY, -BD, 0).union(rrect(FW, FH, R_FLANGE, -BD - FL, -BD))
      .cut(rrect(BW - 2 * WALL, BH - 2 * WALL, R_BODY - WALL, -CAV, 0)))
for x, y in HOLES:
    fp = fp.union(cq.Workplane().circle(BOSS).circle(1.0).extrude(CAV).translate((x, y, -CAV)))
heat = cq.Workplane().box(HS[1] - HS[0], HS[3] - HS[2], CAV - HS_DEPTH, centered=False).translate(
    (-HS[1], HS[2], -CAV))                         # world x = the board's -x
fp = fp.union(heat)
screws = None
for x, y in HOLES:
    sc = (cq.Workplane().circle(1.0).extrude(8.0).translate((x, y, T - 8.0))     # nominal 2 tapping x 8 (f11)
          .union(cq.Workplane().circle(1.6).extrude(1.3).translate((x, y, T))))   # pan head 3.2 (on the bracket)
    screws = sc if screws is None else screws.union(sc)

# J3 (f7: vertical, the plug in straight from below the board) -> over to the module's socket in the middle (f12), down
# into it
j3x, j3y = -pos['J3'][0], pos['J3'][1]
w, t = 10.0, 1.0                                   # 8 wires at 1.25 as a flat band
J3_MATED, J3_ROOM = 5.7, 1.8                       # the mated plug under the board, the wires' bend under it
zc = -J3_MATED - J3_ROOM / 2                       # the band's middle under the plug


def seg(a, b_):
    (x0, y0, z0), (x1, y1, z1) = a, b_
    lx = abs(x1 - x0) + t if x1 != x0 else w
    ly = abs(y1 - y0) + t
    lz = abs(z1 - z0) + t
    return cq.Workplane().box(lx, ly, lz).translate(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))


sy_ = (SOCKET[2] + SOCKET[3]) / 2
path = [(j3x, j3y, zc), (j3x, sy_, zc), (0.0, sy_, zc), (0.0, sy_, -CAV + 0.5)]
cable = None
for a, b_ in zip(path, path[1:]):
    sgm = seg(a, b_)
    cable = sgm if cable is None else cable.union(sgm)

# f13: straight USB-C plugs from the top edge (the cables up to the monitor's back; f5..f12's L adapters gone): the
# overmold ~12.2 x 6.5, from 0.5 past the receptacle's front, drawn 20 long
PLUG_W, PLUG_T, PLUG_L, PLUG_GAP = 12.2, 6.5, 20.0, 0.5
plugs = None
for r in ('J1', 'J2'):
    ub = usb(r).val().BoundingBox()
    assert pos[r][2] % 360 == 180, (r, 'not opening +y')
    p_ = cq.Workplane().box(PLUG_W, PLUG_L, PLUG_T, centered=(True, False, True)).translate(
        (ub.center.x, ub.ymax + PLUG_GAP, ub.center.z))
    plugs = p_ if plugs is None else plugs.union(p_)
# f13: the clip mount's stud through the board's mount hole from the outside (B, z > T), the nut on F (z 0..-NUT_T)
mx, my = -MOUNT[0], MOUNT[1]                       # world x = the board's -x
nut = cq.Workplane().polygon(6, NUT_AF / math.cos(math.pi / 6)).extrude(NUT_T).translate((mx, my, -NUT_T))
stud = cq.Workplane().circle(STUD_R).extrude(STUD_TIP + T + 6.0).translate((mx, my, -STUD_TIP))
mount = nut.union(stud)
lid = cq.Workplane().add(flip(board))
allparts = comp(sum(groups.values(), []))
for name, other in (('the board', lid), ('the module (wall, heat sink)', fp), ('the parts', allparts), ('the mount', mount)):
    clash = plugs.intersect(other).val().Volume()
    assert clash < 0.01, f'the plugs hit {name} ({clash:.3f} mm3)'
for name, other in (('the module (wall, heat sink, socket)', fp), ('the parts', allparts), ('J3\'s plug and cable', cable),
                    ('the screws', screws)):
    clash = mount.intersect(other).val().Volume()
    assert clash < 0.01, f'the nut / stud hits {name} ({clash:.3f} mm3)'
clash = allparts.intersect(heat).val().Volume()
assert clash < 0.01, f'a part hits the heat sink ({clash:.3f} mm3)'
clash = allparts.intersect(fp).val().Volume()
assert clash < 0.01, f'a part hits the module ({clash:.3f} mm3)'
print(f"mount: nut {NUT_AF:g} AF x {NUT_T:g}, stud tip {STUD_TIP:g} under the board, clear of the module and the parts")

parts = [('lid', f'FP008(マニュアル 1.3.1: つば 59.5 × 38.5、後ろの本体 55.5 × 34.5 × 15.4。後ろのくぼみは中の 8P のソケットのてっぺんまで {CAV:g}(実測)。下の辺の左寄りに放熱板(てっぺんは縁から {HS_DEPTH:g}、実測。位置は写真から ±1、ソケットとの間は実測 6.3)。壁 {WALL:g}(実測)。ねじのボスは仮)',
          '#30343a', 0.55, 'lid', fp),
         ('cable', 'J3 → FP008 のケーブル(MX1.25 8P、1 → 1)。中のソケットは真ん中(写真から)', '#d9775c', 1, 'mods', cable),
         ('plug', f'USB-C のプラグ(まっすぐ、モールド {PLUG_W:g} × {PLUG_T:g} を {PLUG_L:g} の長さで描いた)。上の端から挿し、ケーブルは上からモニターの裏へ', '#8a8f96', 0.6, 'mods', plugs),
         ('mount', f'クリップ型マウントの 1/4"-20 のねじ(外から基板の穴 ⌀6.5 に通す)と薄ナット(対辺 {NUT_AF:g} × 厚さ {NUT_T:g}、FP008 の側)。ねじの先は基板から {STUD_TIP:g} 下まで。FP008 より上なので中のものには当たらない', '#c0603a', 1, 'mods', mount),
         ('screw', '呼び 2 のタッピング × 8 × 4(付属の 2 × 6 に基板の 1.6 を足した長さ。ブラケットの上から FP008 の後ろのねじ穴へ。ブラケットは描いていない。穴の間隔は実測: 前後 25・左右 36.7)', '#6b6f75', 1, 'mods', screws),
         ('shell', 'USB-C J1(PC へ、上へ伸ばした部分の右)・J2(USB スピーカーなどの機器、ハブのポート 3。左)。どちらも口は上(f13)。KiCad に 3D モデルが無いので外形だけの箱',
          '#b8bcc2', 1, 'shell', usb('J1').union(usb('J2'))),
         ('conn', 'J3 PicoBlade 53398-0871(MX1.25 8P 縦型、ハウジング 4.7、FP008 のケーブル)', '#f1efe8', 1, 'shell', comp(groups['conn'])),
         ('ics', 'CH334F(ハブ)・USBLC6 × 2・XC6206(3.3 V)・水晶 12 MHz(RP2354A とそのまわりは Raspberry Pi の参考設計のフットプリントで 3D モデルが無く、出ていない)', '#202326', 1, 'shell',
          comp(groups['ics'])),
         ('pass', 'C・R', '#b08850', 1, 'shell', comp(groups['pass'])),
         ('led', 'D1(電源 LED、内側)', '#d23c3c', 1, 'shell', comp(groups['led'])),
         ('board', f'基板 f13(FP008 の裏のふた + 上へ伸ばした部分、{size[0]:.0f} × {size[1]:.0f} × {T:g})。部品は内側', '#2f6b45', 1, 'shell', lid)]
dims = [('基板', f'{size[0]:.0f} × {size[1]:.0f} × {T:g}。下は FP008 の後ろの本体の形(角 R12)、f13 で上へ約 16 伸ばした(上の端 y 33、角 R2)。伸ばした部分に J2・取付穴・J1 を横 1 列。切り欠きは無い。部品は内側(FP008 の側、高さ 3.3 まで。J3 は 4.7、プラグを挿すと約 5.7)'),
        ('取付', 'クリップ型マウント(ばねで挟む、角度ノブ付き、上に 1/4"-20 のおねじ)のねじを外(裏)から穴 ⌀6.5(中心 (0, 25.5))に通し、FP008 の側から薄ナット(対辺 11.1・厚さ 4)で締める。穴の中心から半径 7.0 は表裏とも部品・パッド・銅なし。先にナットを締めてから基板を FP008 に付ける(後から締め直せない)'),
        ('固定', 'FP008 の後ろの 4 つのねじ穴(溝のない下穴)に、ブラケットの上から付属と同じ呼び 2 のタッピングで(付属は 2 × 6、基板 1.6 を挟むので 2 × 8)。基板の穴は丸穴 2.4(f11、中心 ±18.35, ±12.5)。部品・パッドは穴の中心から 3.5 離す'),
        ('J1 / J2', 'J1 = PC へ(x 15.5)、J2 = USB スピーカーなどの機器(ハブのポート 3、x −15.5)。どちらも口は上で、まっすぐのプラグを上から挿す(f13。f5〜f12 の L 字の変換と切り欠きは無くした)。ESD・CC の抵抗・コンデンサーはそれぞれの下(伸ばした部分)'),
        ('J3', 'MX1.25 8P の縦型(53398-0871)、内側の上の真ん中(f13)。FP008 の中のソケット(真ん中、縁から 10.9)とはプラグ込みで 3.4 空く。プラグは FP008 の側からまっすぐ挿す'),
        ('未確認', 'クリップの台が基板の裏のブラケット(y ±22 まで)に乗り上げないか、ブラケットの長さと位置(44、真ん中とみた)、放熱板とソケットの位置の精度(写真から ±1)、本体の角の形、ケーブルの長さ')]
write_page('fp008-board', 'FP008 USB 基板 f13', [(k, l, c, o, g, s) for k, l, c, o, g, s in parts],
           'Grow FP008(顔・手のひら静脈)の裏にふたとしてねじで留め、USB-C 1 本で PC につなぐ基板(RP2354A が UART・鍵・シリアル OTA を持つ)。部品は FP008 の内側。f13 で上へ伸ばし、クリップ型マウントでモニターの上に付ける。'
           'ドラッグで回転、ホイール/ピンチで拡大。分解表示で基板と FP008 が離れる。', dims,
           '基板の部品は KiCad の 3D モデル(CI で取得)、USB-C は外形だけの箱。FP008 は外形だけで、中は仮。単位 mm。', 0,
           [('部品込みの STEP(基板だけ)', STEP)], tz='-6')
