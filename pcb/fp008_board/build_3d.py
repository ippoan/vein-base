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
cx = (bb.xmin + bb.xmax) / 2                       # the board's centre (x); y is centred already

# ---- how it sits on the stand (a sketch: what is not measured yet is a guess, said so on the page) -------------------
# z = the board's normal. The board hangs behind the tablet stand's backrest with its parts facing the backrest, on
# spacers; the FP008 is in front of the backrest, its back on the backrest, held by screws from behind through the
# board, the spacers and the backrest into the module's own threaded holes. USB-C plugs leave the board's lower (-y)
# edge; J3's cable runs in the gap and through the backrest's window to the module's socket.
SPACER = 7.0                                       # board top -> backrest (parts 3.3 + the J3 plug and cable)
BT = 3.0                                           # backrest thickness (guess from the photo)
STAND_W, STAND_H = 99.8, 85.9                      # MooniStar stand backrest (product image)
WIN_W, WIN_H = 45.0, 28.0                          # backrest window (guess)
FW, FH, FL = 59.54, 38.54, 2.2                     # FP008 flange (manual 1.3.1)
BW, BH, BD = 55.45, 34.45, 15.35                   # FP008 body behind the flange
zb = T + SPACER                                    # backrest back face
zf = zb + BT                                       # backrest front face = FP008's back
holes = [(x, sy * 11.5) for x in (bb.xmin + 2.5, bb.xmax - 2.5) for sy in (-1, 1)]

fp_body = cq.Workplane().center(cx, 0).ellipse(BW / 2, BH / 2).extrude(BD).translate((0, 0, zf))
fp_flange = cq.Workplane().center(cx, 0).ellipse(FW / 2, FH / 2).extrude(FL).translate((0, 0, zf + BD))
fp = fp_body.union(fp_flange)
sock = (cq.Workplane().box(10.0, 4.0, 3.5).translate((cx, 0, zf + 1.75)))       # the module's 8P socket (place guessed)
stand = (cq.Workplane().box(STAND_W, STAND_H, BT).translate((cx, FH / 2 + 8.0 - STAND_H / 2, zb + BT / 2))
         .cut(cq.Workplane().box(WIN_W, WIN_H, BT + 2).translate((cx, 0, zb + BT / 2))))
spacers = None
screws = None
for x, y in holes:
    sp = cq.Workplane().circle(2.2).circle(1.1).extrude(SPACER).translate((x, y, T))
    sc = cq.Workplane().circle(1.0).extrude(zf + 1.0).translate((x, y, -1.0)).union(
        cq.Workplane().circle(1.9).extrude(1.2).translate((x, y, -1.2)))
    spacers = sp if spacers is None else spacers.union(sp)
    screws = sc if screws is None else screws.union(sc)

# J3 (opening +y) -> out past its plug in the gap -> back over the parts -> up through the window to the socket
j3x, j3y = pos['J3'][0], pos['J3'][1]
w, t = 10.0, 1.0                                   # 8 wires at 1.25 as a flat band
y_out, z_run = bb.ymax + 2.0, T + 5.0              # bend just past the plug, run between the parts and the backrest


def seg(a, b_):
    (x0, y0, z0), (x1, y1, z1) = a, b_
    lx, ly, lz = abs(x1 - x0) or w, abs(y1 - y0) or t, abs(z1 - z0) or t
    if x0 == x1 and z0 == z1:
        lx = w
    if x0 == x1 and y0 == y1:
        lx, ly = w, t
    return cq.Workplane().box(lx + (t if lx != w else 0), ly + t, lz + t).translate(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))


path = [(j3x, j3y + 3.0, T + 1.6), (j3x, y_out, T + 1.6), (j3x, y_out, z_run), (j3x, 4.0, z_run), (cx, 4.0, z_run),
        (cx, 4.0, zf - 0.5), (cx, 1.0, zf - 0.5)]
cable = None
for a, b_ in zip(path, path[1:]):
    sgm = seg(a, b_)
    cable = sgm if cable is None else cable.union(sgm)

parts = [('shell', 'FP008(楕円 59.5 × 38.5、厚み 17.6。マニュアル 1.3.1)。後ろの面が背もたれに当たる', '#30343a', 1, 'shell', fp),
         ('sock', 'FP008 の MX1.25 8P のソケット(位置は仮。実物で確かめる)', '#f1efe8', 1, 'shell', sock),
         ('cable', 'J3 → FP008 のケーブル(MX1.25 8P、1 → 1。基板と背もたれのすき間を通して窓から。道は仮)', '#d9775c', 1, 'mods', cable),
         ('stand', f'タブレットスタンドの背もたれ({STAND_W:g} × {STAND_H:g}、厚み {BT:g} と窓 {WIN_W:g} × {WIN_H:g} は写真からの推定)', '#c9ccd1', 0.45, 'mods', stand),
         ('spacer', f'スペーサー × 4(高さ {SPACER:g}、仮)と M2 ねじ(基板の後ろから FP008 のねじ穴へ。基板の穴の位置は仮で、FP008 のねじ穴に合わせて直す。図のねじは背もたれの前の面で止めてある)', '#a5631d', 1, 'mods', spacers.union(screws)),
         ('usb', 'USB-C J1(PC へ)・J2(USB スピーカーなどの機器、ハブのポート 3)、どちらも下の縁。KiCad に 3D モデルが無いので外形だけの箱',
          '#b8bcc2', 1, 'lid', usb('J1').union(usb('J2'))),
         ('conn', 'J3 PicoBlade 53261-0871(MX1.25 8P、FP008 のケーブル)', '#f1efe8', 1, 'lid', comp(groups['conn'])),
         ('ics', 'CH334F(ハブ)・CH340C(UART)・USBLC6 × 2・XC6206(3.3 V)・水晶 12 MHz', '#202326', 1, 'lid',
          comp(groups['ics'])),
         ('pass', 'C・R', '#b08850', 1, 'lid', comp(groups['pass'])),
         ('led', 'D1(電源 LED)', '#d23c3c', 1, 'lid', comp(groups['led'])),
         ('lid', f'基板 f2({size[0]:.0f} × {size[1]:.0f} × {T:g})。部品面を背もたれに向ける', '#2f6b45', 1, 'lid',
          cq.Workplane().add(board))]
dims = [('基板', f'{size[0]:.0f} × {size[1]:.0f} × {T:g}(部品は USB-C の高さ 3.3 まで)'),
        ('J1 / J2', 'USB-C、どちらも下(−y)の縁。J1 = PC へ 1 本(FP008 のカメラ(UVC)と COM ポートが見える)、'
                    'J2 = USB スピーカーなどの機器(ハブのポート 3、電源は PC のポートから)'),
        ('J3', 'MX1.25 8P、上(+y)の縁: FP008 のケーブル(1 = 5V、2 = GND、3 = TX、4 = RX、5 = IRQ、6 = 3V3、7 = D+、8 = D-)'),
        ('取り付け', f'FP008 → 背もたれ({BT:g}、推定)→ スペーサー {SPACER:g}(仮)→ 基板。'
                     '基板の後ろから M2 ねじで FP008 のねじ穴に締め、背もたれを挟む'),
        ('未確認', 'FP008 のねじ穴の間隔・ねじの太さ・ソケットの位置、背もたれの厚みと窓。基板の四隅の M2 は仮')]
write_page('fp008-board', 'FP008 USB 基板 f2', [(k, l, c, o, g, s) for k, l, c, o, g, s in parts],
           'Grow FP008(顔・手のひら静脈)を USB-C 1 本で PC につなぐ基板(マイコンなし)と、タブレットスタンドへの付け方のたたき台。'
           'ドラッグで回転、ホイール/ピンチで拡大。分解表示で FP008・スタンド・基板が離れる。', dims,
           '基板の部品は KiCad の 3D モデル(CI で取得)、USB-C は外形だけの箱。FP008 は外形の楕円だけ。単位 mm。', 0,
           [('部品込みの STEP(基板だけ)', STEP)], tz=f'{zf / 2:.1f}')
