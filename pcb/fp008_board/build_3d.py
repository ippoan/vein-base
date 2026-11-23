"""3D preview of the FP008 USB board (f7, as f5 / f6: the parts face the module, windows for the L adapters; J3 vertical) (site/fp008-board/) from the STEP with parts that the CI writes
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
# its parts below z = 0 in the module's back; the module's four rear screw holes take M3 x 6 screws from the lid (f8). The two
# USB-C sit side by side at the bottom edge (f8), openings -y at the windows (world +x = the board's -x: seen from behind);
# the cables take an L-shaped (90 deg) adapter at the plug. The module's inside is not known: drawn as a recess
# CAV deep with bosses at the screw holes (guesses), the 8P socket somewhere inside (top centre, from the photo).
FW, FH, FL = 59.54, 38.54, 2.2                     # flange (manual 1.3.1)
BW, BH, BD = 55.45, 34.45, 15.35                   # rear body
R_BODY, R_FLANGE = 12.4, 14.0                      # corner radii (guess from the drawing)
HOLES = [(sx * 18.15, sy * 12.5) for sx in (-1, 1) for sy in (-1, 1)]    # = build_board.py's HOLES (symmetric, M3, f8)
CAV, WALL, BOSS = 5.0, 1.5, 3.0                    # the module's rear recess depth, wall, boss radius (guesses; M3 f8)


def rrect(w, h, r, z0, z1):
    return cq.Workplane().sketch().rect(w, h).vertices().fillet(r).finalize().extrude(z1 - z0).translate((0, 0, z0))


fp = (rrect(BW, BH, R_BODY, -BD, 0).union(rrect(FW, FH, R_FLANGE, -BD - FL, -BD))
      .cut(rrect(BW - 2 * WALL, BH - 2 * WALL, R_BODY - WALL, -CAV, 0)))
for x, y in HOLES:
    fp = fp.union(cq.Workplane().circle(BOSS).circle(1.7).extrude(CAV).translate((x, y, -CAV)))
screws = None
for x, y in HOLES:
    sc = (cq.Workplane().circle(1.5).extrude(6.0).translate((x, y, T - 6.0))     # M3 x 6 (the maker, 2026-11-23)
          .union(cq.Workplane().circle(2.75).extrude(2.1).translate((x, y, T))))   # pan head 5.5
    screws = sc if screws is None else screws.union(sc)

# J3 (f7: vertical, just under the module's socket, the plug in straight from below the board) -> +y to the wall,
# then into the module's socket by the top wall (its exact place is not known)
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


ye = BH / 2 - WALL - 1.0
path = [(j3x, j3y, zc), (j3x, ye, zc), (j3x, ye, min(zc, -CAV + 0.5))]
cable = None
for a, b_ in zip(path, path[1:]):
    sgm = seg(a, b_)
    cable = sgm if cable is None else cable.union(sgm)

# the L adapters on the two USB-C (f5: USB-C plug -> female turned 90 deg, the female end up; size from a product
# photo, = build_board.py's AD_W / AD_D): the elbow sits against the receptacle's face under the board, in the module's
# rear recess, and the body rises through the board's window (asserted clear of the board; the recess is a guess, so
# its overlap with the elbow is only reported)
AD_W, AD_D, AD_DOWN, AD_UP = 12.4, 7.5, 3.5, 19.0   # across, deep, below / above the plug's centre line
zc = -USB_H / 2
adapters = None
for r in ('J1', 'J2'):
    ub = usb(r).val().BoundingBox()
    a_ = cq.Workplane().box(AD_W, AD_D, AD_DOWN + AD_UP, centered=(True, False, False)).translate(   # f8: the
        (ub.center.x, ub.ymin - AD_D, zc - AD_DOWN))           # openings face -y, the windows at the bottom edge
    adapters = a_ if adapters is None else adapters.union(a_)
lid = cq.Workplane().add(flip(board))
clash = adapters.intersect(lid).val().Volume()
assert clash < 0.01, f'the adapters hit the board ({clash:.3f} mm3): the windows are too small'
AD_BOTTOM = zc - AD_DOWN
print(f'adapter elbows reach {-AD_BOTTOM:.1f} under the board; the guessed recess is {CAV:g} deep')

parts = [('lid', f'FP008(マニュアル 1.3.1: つば 59.5 × 38.5、後ろの本体 55.5 × 34.5 × 15.4。後ろのくぼみ {CAV:g}・壁 {WALL:g}・ねじのボスは仮)',
          '#30343a', 0.55, 'lid', fp),
         ('cable', 'J3 → FP008 のケーブル(MX1.25 8P、1 → 1)。中のソケットの位置は未確認', '#d9775c', 1, 'mods', cable),
         ('adapter', f'USB-C の L 字の変換(オス → 90° のメス、参考の外形 {AD_W:g} × {AD_D:g} × {AD_DOWN + AD_UP:g}、写真から)。根元は FP008 の後ろのくぼみ(基板から {-AD_BOTTOM:.1f} 下まで)、胴は基板の窓を通る', '#8a8f96', 0.6, 'mods', adapters),
         ('screw', 'M3 × 6 ねじ × 4(ふたの上から FP008 の後ろのねじ穴へ。前後 25 はメーカー回答、左右 36.3 は図の実測。穴は 3.4)', '#6b6f75', 1, 'mods', screws),
         ('shell', 'USB-C J1(PC へ)・J2(USB スピーカーなどの機器、ハブのポート 3)。基板の内側の下の辺の真ん中に並べ(f8: ブラケットとブラケットの間)、口は下の窓に向く。KiCad に 3D モデルが無いので外形だけの箱',
          '#b8bcc2', 1, 'shell', usb('J1').union(usb('J2'))),
         ('conn', 'J3 PicoBlade 53398-0871(MX1.25 8P 縦型、ハウジング 4.7、FP008 のケーブル)', '#f1efe8', 1, 'shell', comp(groups['conn'])),
         ('ics', 'CH334F(ハブ)・USBLC6 × 2・XC6206(3.3 V)・水晶 12 MHz(RP2354A とそのまわりは Raspberry Pi の参考設計のフットプリントで 3D モデルが無く、出ていない)', '#202326', 1, 'shell',
          comp(groups['ics'])),
         ('pass', 'C・R', '#b08850', 1, 'shell', comp(groups['pass'])),
         ('led', 'D1(電源 LED、内側)', '#d23c3c', 1, 'shell', comp(groups['led'])),
         ('board', f'基板 f8(FP008 の裏のふた、{size[0]:.0f} × {size[1]:.0f} × {T:g})。部品は内側', '#2f6b45', 1, 'shell', lid)]
dims = [('基板', f'{size[0]:.0f} × {size[1]:.0f} × {T:g}。FP008 の後ろの本体の形(角 R12、外にはみ出さない)。下の辺の真ん中に L 字の変換が通る窓 2 つ(13.4 × 8.8、f8 でブラケットの帯の内側へ)。部品は内側(FP008 の中、高さ 3.3 まで。J3 は 4.7、プラグを挿すと約 5.7)'),
        ('固定', 'FP008 の後ろの 4 つのねじ穴(中心から ±18.15, ±12.5。前後 25 はメーカー回答(2026-11-23)、左右 36.3 はマニュアルの背面図の実測(縮尺を前後 25 に合わせて補正、誤差 ±0.2)。穴は M3 のゆるめ 3.4)に M3 × 6 ねじで。部品・パッド・窓は穴の中心から 3.5 離す'),
        ('J1 / J2', 'USB-C を下の辺の真ん中に 2 つ並べ、口は下の窓に向く。J1 = PC へ、J2 = USB スピーカーなどの機器(ハブのポート 3)。L 字の変換(オス → 90° のメス)は基板を FP008 から外して挿し、胴が窓を通って上を向く。ケーブルは後ろへ'),
        ('J3', 'MX1.25 8P の縦型(53398-0871)、内側の上の真ん中で、FP008 の中のソケット(上のふちの壁ぎわ)のすぐ下。プラグは FP008 の側からまっすぐ挿す'),
        ('未確認', 'L 字の変換の寸法(窓 13.4 × 8.8 に入るか)、根元が FP008 の後ろのくぼみに入るか(約 5.1 の深さが要る)、ねじ穴の位置と太さ、本体の角の形、後ろのくぼみの深さ(部品 3.3、J3 のプラグと線の曲がり約 7.5 が入るか)、中のソケットの位置、ケーブルの長さ')]
write_page('fp008-board', 'FP008 USB 基板 f7', [(k, l, c, o, g, s) for k, l, c, o, g, s in parts],
           'Grow FP008(顔・手のひら静脈)の裏にふたとしてねじで留め、USB-C 1 本で PC につなぐ基板(RP2354A が UART・鍵・シリアル OTA を持つ)。部品は FP008 の内側。'
           'ドラッグで回転、ホイール/ピンチで拡大。分解表示で基板と FP008 が離れる。', dims,
           '基板の部品は KiCad の 3D モデル(CI で取得)、USB-C は外形だけの箱。FP008 は外形だけで、中は仮。単位 mm。', 0,
           [('部品込みの STEP(基板だけ)', STEP)], tz='-6')
