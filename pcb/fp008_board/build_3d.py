"""3D preview of the FP008 USB board (site/fp008-board/) from the STEP with parts that the CI writes
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


def usb(ref):
    """The USB-C body at its footprint: the opening on the footprint's -y (KiCad), turned with the part."""
    x, y, rot = pos[ref]
    b = cq.Workplane().box(USB_W, USB_L, USB_H, centered=(True, False, False)).translate((0, -USB_FRONT, T))
    return b.rotate((0, 0, 0), (0, 0, 1), rot).translate((x, y, 0))


def comp(lst):
    return cq.Workplane().add(cq.Compound.makeCompound(lst))


bb = board.BoundingBox()
size = (bb.xlen, bb.ylen)

# ---- the board as the FP008's back lid (f3). z = the board's normal: the board on z 0..1.6, parts up (outside), the
# FP008 below with its back face on the board's underside; the module's four rear screw holes take M2 screws from the
# lid. The module's 8P socket is on its own board inside, top centre, opening up; J3's cable goes through the slot.
FW, FH, FL = 59.54, 38.54, 2.2                     # flange (manual 1.3.1)
BW, BH, BD = 55.45, 34.45, 15.35                   # rear body
R_BODY, R_FLANGE = 12.4, 14.0                      # corner radii (guess from the drawing)
HOLES = [(sx * 18.35, sy * 11.95) for sx in (-1, 1) for sy in (-1, 1)]   # = build_board.py's HOLES
SOCK = (0.0, 12.0, -3.0)                           # the module's 8P socket (guess from the photo: top centre)


def rrect(w, h, r, z0, z1):
    return cq.Workplane().sketch().rect(w, h).vertices().fillet(r).finalize().extrude(z1 - z0).translate((0, 0, z0))


fp = rrect(BW, BH, R_BODY, -BD, 0).union(rrect(FW, FH, R_FLANGE, -BD - FL, -BD))
sock = cq.Workplane().box(11.0, 4.0, 3.5).translate(SOCK)
screws = None
for x, y in HOLES:
    sc = (cq.Workplane().circle(1.0).extrude(T + 6.0).translate((x, y, -6.0))
          .union(cq.Workplane().circle(1.9).extrude(1.3).translate((x, y, T))))
    screws = sc if screws is None else screws.union(sc)

# J3 (opening +y) -> the plug -> over the slot -> down through it -> back to the socket
j3x, j3y = pos['J3'][0], pos['J3'][1]
w, t = 10.0, 1.0                                   # 8 wires at 1.25 as a flat band
ys = 14.5                                          # the slot's middle (build_board.py SLOT)


def seg(a, b_):
    (x0, y0, z0), (x1, y1, z1) = a, b_
    lx = abs(x1 - x0) + t if x1 != x0 else w
    ly = abs(y1 - y0) + t
    lz = abs(z1 - z0) + t
    return cq.Workplane().box(lx, ly, lz).translate(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))


path = [(j3x, j3y + 7.5, T + 1.6), (j3x, ys, T + 1.6), (j3x, ys, SOCK[2]), (j3x, SOCK[1] + 2.0, SOCK[2])]
cable = None
for a, b_ in zip(path, path[1:]):
    sgm = seg(a, b_)
    cable = sgm if cable is None else cable.union(sgm)

parts = [('lid', f'FP008(マニュアル 1.3.1: つば 59.5 × 38.5、後ろの本体 55.5 × 34.5 × 15.4、角の丸みは図からの推定)',
          '#30343a', 0.55, 'lid', fp),
         ('sock', 'FP008 の中の MX1.25 8P のソケット(写真から: 上の真ん中、口は上。位置は仮)', '#f1efe8', 1, 'lid', sock),
         ('cable', 'J3 → FP008 のケーブル(MX1.25 8P、1 → 1)。基板の切り欠きを通して中へ', '#d9775c', 1, 'mods', cable),
         ('screw', 'M2 ねじ × 4(ふたの上から FP008 の後ろのねじ穴へ。穴の位置は図からの読み取りで、実物で確かめる)', '#6b6f75', 1, 'mods', screws),
         ('shell', 'USB-C J1(PC へ)・J2(USB スピーカーなどの機器、ハブのポート 3)、どちらも下の縁。KiCad に 3D モデルが無いので外形だけの箱',
          '#b8bcc2', 1, 'shell', usb('J1').union(usb('J2'))),
         ('conn', 'J3 PicoBlade 53261-0871(MX1.25 8P、FP008 のケーブル)', '#f1efe8', 1, 'shell', comp(groups['conn'])),
         ('ics', 'CH334F(ハブ)・CH340C(UART)・USBLC6 × 2・XC6206(3.3 V)・水晶 12 MHz', '#202326', 1, 'shell',
          comp(groups['ics'])),
         ('pass', 'C・R', '#b08850', 1, 'shell', comp(groups['pass'])),
         ('led', 'D1(電源 LED)', '#d23c3c', 1, 'shell', comp(groups['led'])),
         ('board', f'基板 f3(FP008 の裏のふた、{size[0]:.0f} × {size[1]:.0f} × {T:g})。部品は外側', '#2f6b45', 1, 'shell',
          cq.Workplane().add(board))]
dims = [('基板', f'{size[0]:.0f} × {size[1]:.0f} × {T:g}、FP008 の後ろの本体の形(角 R12)。部品は外側(USB-C の高さ 3.3 まで)'),
        ('固定', 'FP008 の後ろの 4 つのねじ穴(中心から ±18.35, ±11.95。マニュアルの図からの読み取り)に M2 ねじで。基板がそのままふたになる'),
        ('J1 / J2', 'USB-C、どちらも下の縁。J1 = PC へ 1 本、J2 = USB スピーカーなどの機器(ハブのポート 3)'),
        ('J3', 'MX1.25 8P、上の真ん中。ケーブルは口の先の切り欠き(12 × 1.8)から FP008 の中のソケットへ'),
        ('未確認', 'ねじ穴の位置と太さ、本体の角の形、中のソケットの位置と高さ、ケーブルの長さ')]
write_page('fp008-board', 'FP008 USB 基板 f3', [(k, l, c, o, g, s) for k, l, c, o, g, s in parts],
           'Grow FP008(顔・手のひら静脈)の裏にふたとしてねじで留め、USB-C 1 本で PC につなぐ基板(マイコンなし)。'
           'ドラッグで回転、ホイール/ピンチで拡大。分解表示で基板と FP008 が離れる。', dims,
           '基板の部品は KiCad の 3D モデル(CI で取得)、USB-C は外形だけの箱。FP008 は外形だけ。単位 mm。', 0,
           [('部品込みの STEP(基板だけ)', STEP)], tz='-6')
