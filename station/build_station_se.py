"""Vein Station SE: desktop enclosure for CoreS3 SE + RS232M Module 13.2 (FC-1200 alcohol checker), Unit NFC and
Finger Vein Module (A), all facing up. No LAN base: one USB-C cable to the Windows PC carries power and data.
Run from the repository root:  python3 station/build_station_se.py
Writes station/vein_station_se<N>_{shell,lid}.{step,stl} and the 3D preview site/station-se/index.html,
and fails if the enclosure collides with a module, plug or cable.

Coordinates are the same as build_station.py: x = left→right, `ys` = back→front (Y = -ys), z = 0 at the top surface,
down is negative.

CoreS3 SE and Unit NFC come from M5Stack's official STL (m5stack/M5_Hardware, MIT, pinned in m5_cad.py; downloaded into
station/cad/ on first run). Port positions measured from them:
  CoreS3 SE 54 × 54 × 16.5. Screen landscape, touch buttons at the front. PWR / USB-C / PORT.A are all on the LEFT
  side (back → front); microSD and the reset button on the front; speaker on the right; M-Bus along the right half
  of the bottom. There is no PORT.B / PORT.C on the body.
  Unit NFC 24 × 48 × 8, Grove in the middle of one short end, screw head on the back 12 from that end.
Layout (se2):
  left: NFC standing along ys, Grove at the front / middle: CoreS3 SE (screen up) on the RS232M, ports facing left
  into a 15 mm bay / right: finger vein module along ys (finger points to the back).
  PORT.A ↔ NFC Grove loop in the front of the bay; the USB-C is an L plug turning back, its cable leaves through the
  back wall. DB9 of the RS232M leaves through the back wall (its real side is not known yet).
  G8/G9 for the vein UART come from an M-Bus breakout PCB under the RS232M, J3 (MX1.25 4P) facing the vein module.
The finger vein module is a 59 × 26 × 15 block of the official outline (Waveshare product page,
https://www.waveshare.com/finger-vein-scanner-module-a.htm); only its connector position is not known yet.
Still provisional: RS232M (no official CAD; 54 × 54 × 13.2 block, DB9 side), the breakout PCB.
"""
import base64, json, os
import numpy as np
import cadquery as cq
from m5_cad import stl_tris

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REV = 'se2'

W, D = 129.0, 65.0           # outer size (x, ys)
WALL, TOP, LID = 2.0, 1.5, 2.0
R_OUT = 4.0
CLR = 0.1
FIT = 0.2                    # side clearance to the locating frames


def box(x0, x1, ys0, ys1, z0, z1):
    return cq.Workplane('XY').box(x1 - x0, ys1 - ys0, z1 - z0, centered=False).translate((x0, -ys1, z0))


def cyl_z(x, ys, r, z0, z1):
    return cq.Workplane('XY').workplane(offset=z0).center(x, -ys).circle(r).extrude(z1 - z0)


def cyl_x(x0, x1, ys, z, r):
    return cq.Workplane('YZ').workplane(offset=x0).center(-ys, z).circle(r).extrude(x1 - x0)


def rbox(x0, x1, ys0, ys1, z0, z1, r):
    return box(x0, x1, ys0, ys1, z0, z1).edges('|Z').fillet(r)


# ---- modules ----------------------------------------------------------------------------------------------
# CoreS3 SE: CAD x → x, CAD z (front +) → ys, CAD y (up, -5.3..11.2) → z
TOP_CORE = 1.0                # top plate thinned around the CoreS3 (screen almost flush)
CORE_LIP = 1.5
H_CORE, H_RS232 = 16.5, 13.2
CX, CYS = 69.0, 32.5          # CoreS3 centre
CORE = (CX - 27, CX + 27, CYS - 27, CYS + 27)
Z_CORE_TOP = -TOP_CORE
Z_CORE_BOT = Z_CORE_TOP - H_CORE          # -17.5
Z_MOD_BOT = Z_CORE_BOT - H_RS232          # -30.7


def core_z(y_cad):
    return Z_CORE_TOP - 11.2 + y_cad


# NFC: CAD x → x, CAD -y (Grove end) → front, CAD z (label face +5.2) → up; top at -1.5 (under the plate)
NX, NYS = 15.0, 29.0
NFC = (NX - 12, NX + 12, NYS - 24, NYS + 24)
Z_NFC_TOP = -TOP
VEIN = (100, 126, 3, 62)      # 26 × 59 placeholder block along ys
# M-Bus breakout PCB under the RS232M (header plastic 2.5 + PCB 1.6), J3 on its underside facing +x (vein)
Z_BRK_TOP = Z_MOD_BOT - 2.5
Z_BRK_BOT = Z_BRK_TOP - 1.6
Z_J3_BOT = Z_BRK_BOT - 3.4
Z_LID = Z_J3_BOT - 0.5
Z_BOT = Z_LID - LID

core = rbox(*CORE, Z_CORE_BOT, Z_CORE_TOP, 3.0)
# the official STL has no LCD / cover glass: show one in the preview (black glass inside the 1.2 white rim)
glass = rbox(CORE[0] + 1.2, CORE[1] - 1.2, CORE[2] + 1.2, CORE[3] - 1.2, Z_CORE_TOP - 1.0, Z_CORE_TOP - 0.05, 2.0)
rs232 = rbox(*CORE, Z_MOD_BOT, Z_CORE_BOT, 3.0)
nfc = rbox(*NFC, Z_NFC_TOP - 8.0, Z_NFC_TOP, 1.5)
vein = rbox(*VEIN, -16.5, -1.5, 2.0)
brk_hdr = box(CX + 15, CX + 20, CYS - 19, CYS + 19, Z_BRK_TOP, Z_MOD_BOT)   # under the M-Bus (CAD x 15..20)
brk_pcb = box(CX + 10, CX + 24, CYS - 20, CYS + 20, Z_BRK_BOT, Z_BRK_TOP)
j3 = box(CX + 17.5, CX + 24, CYS - 4, CYS + 4, Z_J3_BOT, Z_BRK_BOT)
j3_plug = box(CX + 24, CX + 29.5, CYS - 3, CYS + 3, Z_J3_BOT + 0.4, Z_BRK_BOT - 0.4)
# PORT.A: CAD z 9.0..19.0, y -0.5..4.7 on the left side; the Grove plug sticks out 10
porta_plug = box(CORE[0] - 10, CORE[0], CYS + 9.2, CYS + 18.8, core_z(-0.3), core_z(4.5))
# NFC Grove at the front end (CAD x -5..5, z 0..5)
nfc_plug = box(NX - 4.5, NX + 4.5, NFC[3], NFC[3] + 8, Z_NFC_TOP - 5.2 + 0.2, Z_NFC_TOP - 5.2 + 5.0)
# USB-C: CAD z -4.4..4.4, y 1.5..4.5 → L plug (sanwa KU-CCP100KAW18BK type: head 14 from the side, ⌀9),
# cable ⌀3.5 turning back along the bay and out of the back wall
Z_USB = core_z(3.0)
usb_head = cyl_x(CORE[0] - 14, CORE[0], CYS, Z_USB, 4.5)
usb_cable = box(CORE[0] - 13.5, CORE[0] - 10, -8, CYS, Z_USB - 1.75, Z_USB + 1.75)
db9_z = (Z_CORE_BOT + Z_MOD_BOT) / 2
DB9X = CX - 8                 # DB9 on the back of the RS232M (side not confirmed)
db9_plug = box(DB9X - 16.5, DB9X + 16.5, -40, CORE[2], db9_z - 8, db9_z + 8)

# ---- enclosure: shell (top plate + walls) ----------------------------------------------------------------
shell = rbox(0, W, 0, D, Z_BOT, 0, R_OUT)
shell = shell.cut(rbox(WALL, W - WALL, WALL, D - WALL, Z_BOT - 1, -TOP, R_OUT - WALL))
# top openings: vein with a 1 mm lip, NFC label window, CoreS3 with a 1.5 lip on a plate thinned to 1.0
shell = shell.cut(rbox(VEIN[0] + 1, VEIN[1] - 1, VEIN[2] + 1, VEIN[3] - 1, -TOP - 1, 1, 1.5))
shell = shell.cut(box(NFC[0] + 2, NFC[1] - 2, NFC[2] + 3, NFC[3] - 5, -TOP - 1, 1))
shell = shell.cut(rbox(CORE[0] - FIT, CORE[1] + FIT, CORE[2] - FIT, CORE[3] + FIT, -TOP - 1, -TOP_CORE, 3.0 + FIT))
shell = shell.cut(rbox(CORE[0] + CORE_LIP, CORE[1] - CORE_LIP, CORE[2] + CORE_LIP, CORE[3] - CORE_LIP, -TOP - 1, 1,
                       3.0 - CORE_LIP))


def frame(r, depth, t=1.2, cuts=()):
    """Locating frame hanging from the top plate: a ring around rectangle r (+FIT), minus `cuts` (plug openings)."""
    x0, x1, y0, y1 = r[0] - FIT, r[1] + FIT, r[2] - FIT, r[3] + FIT
    ring = box(x0 - t, x1 + t, y0 - t, y1 + t, depth, -TOP).cut(box(x0, x1, y0, y1, depth - 1, 0))
    ring = ring.intersect(box(WALL, W - WALL, WALL, D - WALL, depth - 1, 0))
    for c in cuts:
        ring = ring.cut(c)
    return ring


shell = shell.union(frame(VEIN, -5.75))
shell = shell.union(frame(NFC, -4.5, cuts=[box(NX - 6, NX + 6, NFC[3] - 1, D, -20, 0)]))
shell = shell.union(frame(CORE, -6.0, cuts=[box(CORE[0] - 3, CORE[0] + 1, CYS - 6, CYS + 20, -20, 0)]))  # USB / PORT.A
# cable exits in the back wall: USB cable in the bay, DB9 plug behind the RS232M
shell = shell.cut(box(CORE[0] - 14, CORE[0] - 9.5, -1, WALL + 1, Z_USB - 2.25, Z_USB + 2.25))
shell = shell.cut(box(DB9X - 17, DB9X + 17, -1, WALL + 1, db9_z - 8.5, db9_z + 8.5))
# reset button (CAD x 10.6..17.6 on the front face) — pin hole in the front wall
shell = shell.cut(cq.Workplane('XZ').workplane(offset=-(D + 1)).center(CX + 14.1, core_z(3.9)).circle(2.0).extrude(4))
# lid hook slots in the left and right walls
for ys0 in (10, 45):
    shell = shell.cut(box(0.8, WALL + 0.1, ys0, ys0 + 8, Z_BOT - 1, Z_BOT + 1.2))
    shell = shell.cut(box(W - WALL - 0.1, W - 0.8, ys0, ys0 + 8, Z_BOT - 1, Z_BOT + 1.2))
# screw bosses (M3 self-tapping, pilot 2.5) in the bay, clear of the USB head / cable and the Grove plugs
SCREWS = [(CORE[0] - 4.5, 8.0), (CORE[0] - 4.5, 59.0)]
for x, ys in SCREWS:
    shell = shell.union(cyl_z(x, ys, 2.6, Z_LID, -TOP).cut(cyl_z(x, ys, 1.25, Z_LID - 1, -TOP - 2)))

# ---- enclosure: lid with pedestals ----------------------------------------------------------------------
lid = rbox(WALL + CLR, W - WALL - CLR, WALL + CLR, D - WALL - CLR, Z_BOT, Z_LID, R_OUT - WALL - CLR)
for ys0 in (10, 45):
    lid = lid.union(box(1.0, WALL + CLR + 0.5, ys0 + 0.3, ys0 + 7.7, Z_BOT + 0.1, Z_BOT + 1.1))
    lid = lid.union(box(W - WALL - CLR - 0.5, W - 1.0, ys0 + 0.3, ys0 + 7.7, Z_BOT + 0.1, Z_BOT + 1.1))
ped_nfc = box(NFC[0] + 3, NFC[1] - 3, NFC[2] + 3, NFC[3] - 3, Z_LID, Z_NFC_TOP - 8.0).cut(
    cyl_z(NX, NFC[3] - 12, 3.0, Z_LID, 0))                      # relief for the screw head on its back
ped_vein = box(VEIN[0] + 1, VEIN[0] + 4, VEIN[2] + 4, VEIN[3] - 4, Z_LID, -16.5).union(
    box(VEIN[1] - 4, VEIN[1] - 1, VEIN[2] + 4, VEIN[3] - 4, Z_LID, -16.5))
# rails under the RS232M edges, clear of the breakout PCB, J3 and its plug
ped_core = (box(CORE[0] + 1, CORE[0] + 4, CORE[2] + 3, CORE[3] - 3, Z_LID, Z_MOD_BOT)
            .union(box(CORE[0] + 6, CX + 8, CORE[2] + 1, CORE[2] + 4, Z_LID, Z_MOD_BOT))
            .union(box(CORE[0] + 6, CX + 8, CORE[3] - 4, CORE[3] - 1, Z_LID, Z_MOD_BOT))
            .union(box(CORE[1] - 2.5, CORE[1] - 0.5, CORE[2] + 3, CYS - 6, Z_LID, Z_MOD_BOT))
            .union(box(CORE[1] - 2.5, CORE[1] - 0.5, CYS + 6, CORE[3] - 3, Z_LID, Z_MOD_BOT)))
lid = lid.union(ped_nfc).union(ped_vein).union(ped_core)
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
def mesh_core(t):
    x, y, z = t[..., 0], t[..., 1], t[..., 2]
    return np.stack([CX + x, -(CYS + z), core_z(y)], axis=-1)


def mesh_nfc(t):
    x, y, z = t[..., 0], t[..., 1], t[..., 2]
    return np.stack([NX + x, -(NYS - y), Z_NFC_TOP - 5.2 + z], axis=-1)


def to_view(v):
    v = v.reshape(-1, 3).copy()
    v[:, 0] -= W / 2
    v[:, 1] += D / 2
    return v.reshape(-1).astype(np.float32)


def tri(shape):
    vs, ts = shape.val().tessellate(0.03, 0.15)
    v = np.array([(p.x, p.y, p.z) for p in vs], dtype=np.float32)
    return to_view(v[np.array(ts)])


parts = [
    ('shell', 'ケース上部(天板+壁)', '#3d6fb6', 0.5, 'shell', tri(shell)),
    ('vein', '指静脈モジュール(外形は公式値、コネクタ位置は未確定)', '#2e3538', 1, 'mods', tri(vein)),
    ('nfc', 'Unit NFC(公式 CAD)', '#f2f2ee', 1, 'mods', to_view(mesh_nfc(stl_tris('nfc')))),
    ('core', 'CoreS3 SE(公式 CAD)', '#e9e9e6', 1, 'mods', to_view(mesh_core(stl_tris('core')))),
    ('glass', 'CoreS3 SE の画面(CAD に無いので板で表示)', '#15181b', 1, 'mods', tri(glass)),
    ('rs232', 'RS232M Module 13.2(仮の箱)', '#5b6168', 1, 'mods', tri(rs232)),
    ('brkhdr', 'M-Bus 分岐基板のピンヘッダー', '#2b2f33', 1, 'mods', tri(brk_hdr)),
    ('brkpcb', 'M-Bus 分岐基板(G8/G9 → 指静脈)', '#1f7a4d', 1, 'mods', tri(brk_pcb)),
    ('j3', 'J3 MX1.25 4P', '#f1efe8', 1, 'mods', tri(j3)),
    ('j3plug', 'J3 プラグ(指静脈ケーブル)', '#e7e1cf', 1, 'mods', tri(j3_plug)),
    ('nfcplug', 'NFC 側 Grove プラグ', '#c47f0e', 1, 'mods', tri(nfc_plug)),
    ('portaplug', 'PORT.A Grove プラグ', '#c47f0e', 1, 'mods', tri(porta_plug)),
    ('usbhead', 'USB-C L字の頭(Windows PC へ)', '#24292d', 1, 'mods', tri(usb_head)),
    ('usbcable', 'USB ケーブル', '#3a4046', 1, 'mods', tri(usb_cable)),
    ('db9', 'DB9 プラグ(FC-1200 へ・位置は仮)', '#8a8f96', 1, 'mods', tri(db9_plug)),
    ('lid', '底蓋+台', '#8fa09c', 0.9, 'lid', tri(lid)),
]
model = [dict(key=k, label=l, color=c, opacity=o, group=g, data=base64.b64encode(a.tobytes()).decode())
         for k, l, c, o, g, a in parts]
SUB = ('CoreS3 SE + RS232M(FC-1200)・指静脈・NFC を上向きに収める卓上筐体の案(LAN なし、USB 1 本で Windows PC へ)。'
       'ドラッグで回転、ホイール/ピンチで拡大。')
DIMS = [('外形', f'{W:g} × {D:g} × {-Z_BOT:.1f}'), ('壁 / 天板 / 底蓋', '2 / 1.5 / 2'),
        ('CoreS3 SE の左側', 'PWR・USB-C・PORT.A(奥→手前)'), ('USB-C', 'L字で奥へ曲げ、奥の壁から出す'),
        ('DB9 出口(奥の壁)', '34 × 17(位置は仮)'), ('リセット', '手前の壁に ⌀4 のピン穴'),
        ('底蓋', '左右 爪 + M3 × 2'), ('CoreS3 SE', '返し 1.5(天板 1.0)/ 縁取り'),
        ('指静脈の配線', 'M-Bus 分岐基板(G8/G9・3V3・GND)→ J3')]
NOTE = ('CoreS3 SE と Unit NFC は M5Stack 公式 STL(m5stack/M5_Hardware)を表示しています。指静脈は Waveshare 公式寸法'
        '(コネクタ位置は未確定)、RS232M・M-Bus 分岐基板は仮の箱で、DB9 の向きは未確認です。単位 mm。')
dims = ''.join(f'        <tr><td>{k}</td><td>{v}</td></tr>\n' for k, v in DIMS)
tpl = open(os.path.join(ROOT, 'tools/station_template.html'), encoding='utf-8').read()
os.makedirs(os.path.join(ROOT, 'site/station-se'), exist_ok=True)
page = os.path.join(ROOT, 'site/station-se/index.html')
page_html = (tpl.replace('__MODEL__', json.dumps(model)).replace('__REV__', 'SE ' + REV).replace('__SUB__', SUB)
             .replace('__DIMS__', dims).replace('__NOTE__', NOTE).replace('__TZ__', f'{Z_BOT / 2:.1f}')
             .replace('__DOWNLOADS__', '<p>CoreS3 SE 版は採用していないので、発注用の STL は置いていない。</p>'))
open(page, 'w', encoding='utf-8').write(page_html)
print('wrote', page, os.path.getsize(page), 'bytes')

if bad:
    raise SystemExit('interference: ' + ', '.join(bad))
