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
parts = [('shell', 'USB-C J1(PC へ)・J2(USB スピーカーなどの機器、ハブのポート 3)。KiCad に 3D モデルが無いので外形だけの箱',
          '#b8bcc2', 1, 'mods', usb('J1').union(usb('J2'))),
         ('conn', 'J3 PicoBlade 53261-0871(MX1.25 8P、FP008 のケーブル)', '#f1efe8', 1, 'mods', comp(groups['conn'])),
         ('ics', 'CH334F(ハブ)・CH340C(UART)・USBLC6 × 2・XC6206(3.3 V)・水晶 12 MHz', '#202326', 1, 'mods',
          comp(groups['ics'])),
         ('pass', 'C・R', '#b08850', 1, 'mods', comp(groups['pass'])),
         ('led', 'D1(電源 LED)', '#d23c3c', 1, 'mods', comp(groups['led'])),
         ('lid', f'基板 f1({size[0]:.0f} × {size[1]:.0f} × {T:g})', '#2f6b45', 1, 'lid', cq.Workplane().add(board))]
dims = [('外形', f'{size[0]:.0f} × {size[1]:.0f} × {T:g}(部品は USB-C の高さ 3.3 まで)'),
        ('J1', 'USB-C、手前(−y)の縁: PC へ 1 本。FP008 のカメラ(UVC)と COM ポートが見える'),
        ('J2', 'USB-C、右(+x)の縁: USB スピーカーなどの機器(ハブのポート 3)。電源は PC のポートから'),
        ('J3', 'MX1.25 8P、奥(+y)の縁: FP008 のケーブル(1 = 5V、2 = GND、3 = TX、4 = RX、5 = IRQ、6 = 3V3、7 = D+、8 = D-)'),
        ('穴', '四隅の M2(仮。FP008 のねじ穴の間隔を測ってから直す)')]
write_page('fp008-board', 'FP008 USB 基板 f1', [(k, l, c, o, g, s) for k, l, c, o, g, s in parts],
           'Grow FP008(顔・手のひら静脈)を USB-C 1 本で PC につなぐ基板(マイコンなし)。ドラッグで回転、ホイール/ピンチで拡大。',
           dims, '部品は KiCad の 3D モデル(CI で取得)、USB-C は外形だけの箱。単位 mm。', 0,
           [('部品込みの STEP', STEP)], tz='0')
