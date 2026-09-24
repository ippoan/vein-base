"""Vein Station SE: desktop enclosure for CoreS3 SE + RS232M Module 13.2 (FC-1200 alcohol checker), Unit NFC and
Finger Vein Module (A), all facing up. No LAN base: one USB-C cable to the Windows PC carries power and data.
Run from the repository root:  python3 station/build_station_se.py
Writes station/vein_station_se<N>_{shell,lid}.{step,stl} and the 3D preview site/station-se/index.html,
and fails if the enclosure collides with a module, plug or cable.

Coordinates are the same as build_station.py: x = left→right, `ys` = back→front (Y = -ys), z = 0 at the top surface,
down is negative.
Layout (se1, for a look at the outside — every size below is provisional until measured):
  left column: finger vein module at the back, NFC below it (Grove end facing the CoreS3)
  right: CoreS3 SE (screen up) on top of the RS232M Module 13.2. PORT.A faces left (NFC), USB-C faces right and
  leaves through the right wall, the DB9 of the RS232M leaves through the back wall.
  CoreS3 SE has no PORT.B connector, so G8/G9 for the vein UART come from a small M-Bus breakout PCB plugged under
  the RS232M (J3 MX1.25 4P on its underside, the same cable as vein-base).
Every module is held as in build_station.py: pushed up by the lid, against a lip in the top plate, located by frames.
"""
import base64, json, os
import numpy as np
import cadquery as cq

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REV = 'se1'

W, D = 131.0, 60.0           # outer size (x, ys)
WALL, TOP, LID = 2.0, 1.5, 2.0
R_OUT = 4.0
CLR = 0.1
FIT = 0.2                    # side clearance to the locating frames


def box(x0, x1, ys0, ys1, z0, z1):
    return cq.Workplane('XY').box(x1 - x0, ys1 - ys0, z1 - z0, centered=False).translate((x0, -ys1, z0))


def cyl_z(x, ys, r, z0, z1):
    return cq.Workplane('XY').workplane(offset=z0).center(x, -ys).circle(r).extrude(z1 - z0)


def rbox(x0, x1, ys0, ys1, z0, z1, r):
    return box(x0, x1, ys0, ys1, z0, z1).edges('|Z').fillet(r)


# ---- modules (reference geometry; sizes are provisional) ---------------------------------------------------
VEIN = (3, 62, 3, 29)         # 59 × 26 × 15 placeholder block (still not measured)
NFC = (3, 51, 33, 56.5)       # 48 × 23.5 × 8, lying along x, Grove end at x=51 (towards the CoreS3)
CORE = (74, 128, 3, 57)       # CoreS3 SE 54 × 54
TOP_CORE = 1.0                # top plate thinned around the CoreS3 (screen almost flush)
CORE_LIP = 1.5
H_CORE, H_RS232 = 16.0, 13.2  # CoreS3 SE body / RS232M Module 13.2 (provisional)
Z_CORE_BOT = -TOP_CORE - H_CORE          # -17.0
Z_MOD_BOT = Z_CORE_BOT - H_RS232         # -30.2
# M-Bus breakout PCB under the RS232M (header plastic 2.5 + PCB 1.6), J3 MX1.25 on its underside
Z_BRK_TOP = Z_MOD_BOT - 2.5
Z_BRK_BOT = Z_BRK_TOP - 1.6
Z_J3_BOT = Z_BRK_BOT - 3.4
Z_LID = Z_J3_BOT - 0.5                   # lid top
Z_BOT = Z_LID - LID                      # bottom of the walls / lid
CX = (CORE[0] + CORE[1]) / 2

vein = rbox(*VEIN, -16.5, -1.5, 2.0)
nfc = rbox(*NFC, -9.5, -1.5, 1.5)
core = rbox(*CORE, Z_CORE_BOT, -TOP_CORE, 4.0)
rs232 = rbox(*CORE, Z_MOD_BOT, Z_CORE_BOT, 4.0)
brk_hdr = box(CX - 19, CX + 19, 48, 53, Z_BRK_TOP, Z_MOD_BOT)
brk_pcb = box(CX - 20, CX + 20, 44, 56, Z_BRK_BOT, Z_BRK_TOP)
j3 = box(81, 87.5, 46, 54, Z_J3_BOT, Z_BRK_BOT)                 # opening faces -x (towards the vein column)
j3_plug = box(76, 81, 47, 53, Z_J3_BOT + 0.4, Z_BRK_BOT - 0.4)
nfc_plug = box(51, 59, 40.5, 49, -8.0, -3.0)                     # Grove on the NFC's short side
porta_plug = box(64, 74, 25, 34, Z_CORE_BOT + 1.0, Z_CORE_BOT + 5.0)  # PORT.A on the CoreS3's left side
usb_head = box(128, 142, 24, 36, -12.5, -5.5)                    # straight USB-C plug through the right wall
usb_cable = box(142, 160, 28, 32, -10.5, -7.5)
db9_z = (Z_CORE_BOT + Z_MOD_BOT) / 2
db9_plug = box(CX - 16.5, CX + 16.5, -40, 3, db9_z - 8, db9_z + 8)  # DB9 cable plug to the FC-1200, out the back

# ---- enclosure: shell (top plate + walls) ----------------------------------------------------------------
shell = rbox(0, W, 0, D, Z_BOT, 0, R_OUT)
shell = shell.cut(rbox(WALL, W - WALL, WALL, D - WALL, Z_BOT - 1, -TOP, R_OUT - WALL))
# top openings: vein with a 1 mm lip, NFC label window, CoreS3 screen with a 1.5 lip on a plate thinned to 1.0
shell = shell.cut(rbox(VEIN[0] + 1, VEIN[1] - 1, VEIN[2] + 1, VEIN[3] - 1, -TOP - 1, 1, 1.5))
shell = shell.cut(box(6, 46, 36, 54, -TOP - 1, 1))
shell = shell.cut(rbox(CORE[0] - FIT, CORE[1] + FIT, CORE[2] - FIT, CORE[3] + FIT, -TOP - 1, -TOP_CORE, 4.0 + FIT))
shell = shell.cut(rbox(CORE[0] + CORE_LIP, CORE[1] - CORE_LIP, CORE[2] + CORE_LIP, CORE[3] - CORE_LIP, -TOP - 1, 1,
                       4.0 - CORE_LIP))


def frame(r, depth, t=1.2, cuts=()):
    """Locating frame hanging from the top plate: a ring around rectangle r (+FIT), minus `cuts` (plug openings)."""
    x0, x1, y0, y1 = r[0] - FIT, r[1] + FIT, r[2] - FIT, r[3] + FIT
    ring = box(x0 - t, x1 + t, y0 - t, y1 + t, depth, -TOP).cut(box(x0, x1, y0, y1, depth - 1, 0))
    ring = ring.intersect(box(WALL, W - WALL, WALL, D - WALL, depth - 1, 0))
    for c in cuts:
        ring = ring.cut(c)
    return ring


shell = shell.union(frame(VEIN, -5.75))
shell = shell.union(frame(NFC, -5.25, cuts=[box(49, 61, 39, 51, -20, 0)]))
shell = shell.union(frame(CORE, -6.0, cuts=[box(60, 76, 23, 36, -20, 0), box(126, 131, 22, 38, -20, 0)]))
# cable exits: USB-C through the right wall, DB9 plug through the back wall
shell = shell.cut(box(W - WALL - 1, W + 1, 23.5, 36.5, -13.0, -5.0))
shell = shell.cut(box(CX - 17, CX + 17, -1, WALL + 1, db9_z - 8.5, db9_z + 8.5))
# lid hook slots in the left and right walls
for ys0 in (8, 42):
    shell = shell.cut(box(0.8, WALL + 0.1, ys0, ys0 + 8, Z_BOT - 1, Z_BOT + 1.2))
    shell = shell.cut(box(W - WALL - 0.1, W - 0.8, ys0, ys0 + 8, Z_BOT - 1, Z_BOT + 1.2))
# screw bosses (M3 self-tapping, pilot 2.5) in the gap between the left column and the CoreS3
SCREWS = [(68.0, 8.0), (68.0, 52.0)]
for x, ys in SCREWS:
    shell = shell.union(cyl_z(x, ys, 2.6, Z_LID, -TOP).cut(cyl_z(x, ys, 1.25, Z_LID - 1, -TOP - 2)))

# ---- enclosure: lid with pedestals ----------------------------------------------------------------------
lid = rbox(WALL + CLR, W - WALL - CLR, WALL + CLR, D - WALL - CLR, Z_BOT, Z_LID, R_OUT - WALL - CLR)
for ys0 in (8, 42):
    lid = lid.union(box(1.0, WALL + CLR + 0.5, ys0 + 0.3, ys0 + 7.7, Z_BOT + 0.1, Z_BOT + 1.1))
    lid = lid.union(box(W - WALL - CLR - 0.5, W - 1.0, ys0 + 0.3, ys0 + 7.7, Z_BOT + 0.1, Z_BOT + 1.1))
ped_vein = box(7, 58, 5, 9, Z_LID, -16.5).union(box(7, 58, 23, 27, Z_LID, -16.5))
ped_nfc = box(6, 48, 36, 54, Z_LID, -9.5)
# rails under the RS232M edges, clear of the breakout PCB, J3 and its plug; they push the stack up to the lip
ped_core = (box(75, 78, 5, 42, Z_LID, Z_MOD_BOT).union(box(124, 127, 5, 55, Z_LID, Z_MOD_BOT))
            .union(box(80, 122, 5, 9, Z_LID, Z_MOD_BOT)))
lid = lid.union(ped_vein).union(ped_nfc).union(ped_core)
for x, ys in SCREWS:
    lid = lid.cut(cyl_z(x, ys, 1.7, Z_BOT - 1, Z_LID + 1)).cut(cyl_z(x, ys, 3.0, Z_BOT - 1, Z_BOT + 1.2))

# ---- interference check ---------------------------------------------------------------------------------
checks = [('指静脈', vein), ('NFC', nfc), ('CoreS3 SE', core), ('RS232M', rs232),
          ('breakout hdr', brk_hdr), ('breakout PCB', brk_pcb), ('J3', j3), ('J3 plug', j3_plug),
          ('NFC Grove', nfc_plug), ('PORT.A Grove', porta_plug), ('USB head', usb_head), ('USB cable', usb_cable),
          ('DB9 plug', db9_plug)]
bad = []
for name, obj in checks:
    for cname, case in (('shell', shell), ('lid', lid)):
        v = case.intersect(obj).val().Volume()
        print(f'interference {cname:5s} x {name:12s} = {v:.3f} mm3')
        if v > 0.01:
            bad.append(f'{cname}/{name}')
v = shell.intersect(lid).val().Volume()
print(f'interference shell x lid = {v:.3f} mm3')
if v > 0.01:
    bad.append('shell/lid')

out = os.path.join(ROOT, 'station')
for name, part in (('shell', shell), ('lid', lid)):
    cq.exporters.export(part, os.path.join(out, f'vein_station_{REV}_{name}.step'))
    cq.exporters.export(part, os.path.join(out, f'vein_station_{REV}_{name}.stl'), tolerance=0.02, angularTolerance=0.1)
    bb = part.val().BoundingBox()
    print(name, round(bb.xlen, 2), round(bb.ylen, 2), round(bb.zlen, 2))


# ---- 3D preview ------------------------------------------------------------------------------------------
def tri(shape):
    vs, ts = shape.val().tessellate(0.03, 0.15)
    v = np.array([(p.x - W / 2, p.y + D / 2, p.z) for p in vs], dtype=np.float32)
    return v[np.array(ts)].reshape(-1).astype(np.float32)


parts = [
    ('shell', 'ケース上部(天板+壁)', '#3d6fb6', 0.5, 'shell', shell),
    ('vein', '指静脈モジュール(仮の箱)', '#2e3538', 1, 'mods', vein),
    ('nfc', 'NFC Unit 48×24×8', '#f2f2ee', 1, 'mods', nfc),
    ('core', 'CoreS3 SE(仮 54×54×16)', '#2b2f33', 1, 'mods', core),
    ('rs232', 'RS232M Module 13.2', '#5b6168', 1, 'mods', rs232),
    ('brkhdr', 'M-Bus 分岐基板のピンヘッダー', '#2b2f33', 1, 'mods', brk_hdr),
    ('brkpcb', 'M-Bus 分岐基板(G8/G9 → 指静脈)', '#1f7a4d', 1, 'mods', brk_pcb),
    ('j3', 'J3 MX1.25 4P', '#f1efe8', 1, 'mods', j3),
    ('j3plug', 'J3 プラグ(指静脈ケーブル)', '#e7e1cf', 1, 'mods', j3_plug),
    ('nfcplug', 'NFC 側 Grove プラグ', '#c47f0e', 1, 'mods', nfc_plug),
    ('portaplug', 'PORT.A Grove プラグ', '#c47f0e', 1, 'mods', porta_plug),
    ('usbhead', 'USB-C プラグ(Windows PC へ)', '#24292d', 1, 'mods', usb_head),
    ('usbcable', 'USB ケーブル', '#3a4046', 1, 'mods', usb_cable),
    ('db9', 'DB9 プラグ(FC-1200 へ)', '#8a8f96', 1, 'mods', db9_plug),
    ('lid', '底蓋+台', '#8fa09c', 0.9, 'lid', lid),
]
model = [dict(key=k, label=l, color=c, opacity=o, group=g, data=base64.b64encode(tri(s).tobytes()).decode())
         for k, l, c, o, g, s in parts]
SUB = ('CoreS3 SE + RS232M(FC-1200)・指静脈・NFC を上向きに収める卓上筐体の案(LAN なし、USB 1 本で Windows PC へ)。'
       'ドラッグで回転、ホイール/ピンチで拡大。')
DIMS = [('外形', f'{W:g} × {D:g} × {-Z_BOT:.1f}'), ('壁 / 天板 / 底蓋', '2 / 1.5 / 2'), ('NFC 窓', '40 × 18'),
        ('USB-C 出口(右の壁)', '13 × 8'), ('DB9 出口(奥の壁)', '34 × 17'),
        ('底蓋', '左右 爪 + M3 × 2'), ('CoreS3 SE', '返し 1.5(天板 1.0)/ 縁取り'),
        ('指静脈の配線', 'M-Bus 分岐基板(G8/G9・3V3・GND)→ J3')]
NOTE = ('外観確認用のたたき台です。CoreS3 SE・RS232M の高さ、USB-C / PORT.A / DB9 の位置、指静脈モジュール(仮の箱)は'
        'すべて未採寸の仮の値です。単位 mm。')
dims = ''.join(f'        <tr><td>{k}</td><td>{v}</td></tr>\n' for k, v in DIMS)
tpl = open(os.path.join(ROOT, 'tools/station_template.html'), encoding='utf-8').read()
os.makedirs(os.path.join(ROOT, 'site/station-se'), exist_ok=True)
page = os.path.join(ROOT, 'site/station-se/index.html')
page_html = (tpl.replace('__MODEL__', json.dumps(model)).replace('__REV__', 'SE ' + REV).replace('__SUB__', SUB)
             .replace('__DIMS__', dims).replace('__NOTE__', NOTE).replace('__TZ__', f'{Z_BOT / 2:.1f}'))
open(page, 'w', encoding='utf-8').write(page_html)
print('wrote', page, os.path.getsize(page), 'bytes')

if bad:
    raise SystemExit('interference: ' + ', '.join(bad))
