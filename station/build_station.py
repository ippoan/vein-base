"""Vein Station: desktop enclosure for VoiceS3R (+ vein-base), Finger Vein Module (A) and Unit NFC, all facing up.
Run from the repository root:  python3 station/build_station.py
Writes station/vein_station_<REV>_{shell,lid}.{step,stl} and the 3D preview site/station/index.html,
and fails if the enclosure collides with a module, plug or cable.

Coordinates: x = left→right, y = back→front is NEGATIVE (the top-view drawing's y is used as `ys`, Y = -ys),
z = 0 at the top surface, down is negative. Outer 91 × 63 × 30.3.
Each module is located sideways by a frame (縁取り) hanging from the top plate. The VoiceS3R top is flush and fully
visible; VoiceS3R + vein-base are held down by one M2x16 screw from the lid into the vein-base.
Module sizes come from the photo measurements (±1–2 mm); the finger vein module is still a 59×26×15 block.
"""
import base64, json, os
import numpy as np
import cadquery as cq

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REV = 'r5'

W, D = 91.0, 63.0            # outer size (x, ys)
WALL, TOP, LID = 2.0, 1.5, 2.0
Z_BOT = -30.3                # bottom of the walls / lid
Z_LID = Z_BOT + LID          # lid top (-28.3)
R_OUT = 4.0
CLR = 0.1


def box(x0, x1, ys0, ys1, z0, z1):
    return cq.Workplane('XY').box(x1 - x0, ys1 - ys0, z1 - z0, centered=False).translate((x0, -ys1, z0))


def cyl_z(x, ys, r, z0, z1):
    return cq.Workplane('XY').workplane(offset=z0).center(x, -ys).circle(r).extrude(z1 - z0)


def cyl_x(x0, x1, ys, z, r):
    return cq.Workplane('YZ').workplane(offset=x0).center(-ys, z).circle(r).extrude(x1 - x0)


def rbox(x0, x1, ys0, ys1, z0, z1, r):
    return box(x0, x1, ys0, ys1, z0, z1).edges('|Z').fillet(r)


# ---- modules (reference geometry, placed in the enclosure) -----------------------------------------------
NFC = (3, 27, 3, 51)          # 24 × 48, Grove end at ys=51 (front)
VEIN = (29, 88, 3, 29)        # 59 × 26
VOICE = (29, 53, 33, 57)      # 24 × 24, USB-C / PORT.A / J3 face +x
Z_ATOM_BOT = -16.8            # VoiceS3R top is flush with the top surface (z=0), fully visible
Z_BASE_BOT = Z_ATOM_BOT - 9.5  # -26.3

nfc = rbox(*NFC, -9.5, -1.5, 1.5)
vein = rbox(*VEIN, -16.5, -1.5, 2.0)
atom = rbox(*VOICE, Z_ATOM_BOT, 0, 3.0)
base = rbox(*VOICE, Z_BASE_BOT, Z_ATOM_BOT, 3.0)
nfc_plug = box(11, 19, 51, 59, -8.0, -3.0)
usb_head = cyl_x(53, 60, 44.5, Z_ATOM_BOT + 7.5, 4.0).union(box(60, 67, 40, 49, Z_ATOM_BOT + 3.3, Z_ATOM_BOT + 11.7))
usb_cable = (box(67, 71, 42.75, 46.25, Z_ATOM_BOT + 6.0, Z_ATOM_BOT + 9.5)
             .union(box(71, 74.5, 42.75, 46.25, Z_LID, Z_ATOM_BOT + 9.5))
             .union(box(71, W + 6, 42.75, 46.25, Z_LID, Z_LID + 3.5)))
porta_plug = box(53, 65, 46, 55, Z_ATOM_BOT, Z_ATOM_BOT + 4.0)
j3_plug = box(53, 58, 41, 48, Z_ATOM_BOT - 6.8, Z_ATOM_BOT - 4.7)

# ---- enclosure: shell (top plate + walls) ----------------------------------------------------------------
shell = rbox(0, W, 0, D, Z_BOT, 0, R_OUT)
shell = shell.cut(rbox(WALL, W - WALL, WALL, D - WALL, Z_BOT - 1, -TOP, R_OUT - WALL))
# top openings: NFC label window, vein with a 1 mm lip, VoiceS3R fully open (its top is flush)
FIT = 0.2                     # side clearance to the locating frames
shell = shell.cut(box(5, 25, 5, 35, -TOP - 1, 1))
shell = shell.cut(rbox(VEIN[0] + 1, VEIN[1] - 1, VEIN[2] + 1, VEIN[3] - 1, -TOP - 1, 1, 1.5))
shell = shell.cut(rbox(VOICE[0] - FIT, VOICE[1] + FIT, VOICE[2] - FIT, VOICE[3] + FIT, -TOP - 1, 1, 3.0 + FIT))


def frame(r, depth, t=1.2, cuts=()):
    """Locating frame hanging from the top plate: a ring around rectangle r (+FIT), minus `cuts` (plug openings)."""
    x0, x1, y0, y1 = r[0] - FIT, r[1] + FIT, r[2] - FIT, r[3] + FIT
    ring = box(x0 - t, x1 + t, y0 - t, y1 + t, depth, -TOP).cut(box(x0, x1, y0, y1, depth - 1, 0))
    ring = ring.intersect(box(WALL, W - WALL, WALL, D - WALL, depth - 1, 0))
    for c in cuts:
        ring = ring.cut(c)
    return ring


# frames (縁取り) that hold each module in place sideways
shell = shell.union(frame(NFC, -9.0, cuts=[box(9, 21, 50, 60, -20, 0)]))
shell = shell.union(frame(VEIN, -10.0))
shell = shell.union(frame(VOICE, -12.0, cuts=[box(53, 60, 35.5, 54.5, -20, 0), box(53, 60, 30, 60, -20, -6.0)]))
# USB exit: notch at the bottom of the right wall, closed by the lid
shell = shell.cut(box(W - WALL - 1, W + 1, 42.25, 46.75, Z_BOT - 1, Z_LID + 4.0))
# lid hook slots in the left wall
for ys0 in (20, 40):
    shell = shell.cut(box(0.8, WALL + 0.1, ys0, ys0 + 8, Z_BOT - 1, Z_BOT + 1.2))
# screw bosses (M3 self-tapping, pilot 2.5) in the cable bay
SCREWS = [(84.5, 35.0), (84.5, 55.5)]
for x, ys in SCREWS:
    shell = shell.union(cyl_z(x, ys, 2.6, Z_LID, -TOP).cut(cyl_z(x, ys, 1.25, Z_LID - 1, -TOP - 2)))

# ---- enclosure: lid with pedestals ----------------------------------------------------------------------
lid = rbox(WALL + CLR, W - WALL - CLR, WALL + CLR, D - WALL - CLR, Z_BOT, Z_LID, R_OUT - WALL - CLR)
for ys0 in (20, 40):
    lid = lid.union(box(1.0, WALL + CLR + 0.5, ys0 + 0.3, ys0 + 7.7, Z_BOT + 0.1, Z_BOT + 1.1))
# NFC pedestal (pushes the unit up against the top plate), with a relief for the screw head on its back
ped_nfc = box(6, 24, 6, 48, Z_LID, -9.5).cut(cyl_z(15, 39, 3.0, Z_LID, 0))
# vein pedestal: two rails under the long edges (bottom details of the module still unknown)
ped_vein = box(33, 84, 5, 9, Z_LID, -16.5).union(box(33, 84, 23, 27, Z_LID, -16.5))
# pad under the vein-base: VoiceS3R + vein-base are held by one M2 screw from the lid into the vein-base
# (replaces its own M2x12: lid 2 + pad 2 + stack 12 -> M2x16)
VX, VYS = (VOICE[0] + VOICE[1]) / 2, (VOICE[2] + VOICE[3]) / 2
pad = box(VOICE[0] + 3, VOICE[1] - 3, VOICE[2] + 3, VOICE[3] - 3, Z_LID, Z_BASE_BOT)
lid = lid.union(ped_nfc).union(ped_vein).union(pad)
lid = lid.cut(cyl_z(VX, VYS, 1.15, Z_BOT - 1, Z_BASE_BOT + 1)).cut(cyl_z(VX, VYS, 2.2, Z_BOT - 1, Z_BOT + 1.3))
m2 = cyl_z(VX, VYS, 1.0, Z_BOT + 1.3, Z_ATOM_BOT - 1.0).union(cyl_z(VX, VYS, 1.9, Z_BOT, Z_BOT + 1.3))
for x, ys in SCREWS:
    lid = lid.cut(cyl_z(x, ys, 1.7, Z_BOT - 1, Z_LID + 1)).cut(cyl_z(x, ys, 3.0, Z_BOT - 1, Z_BOT + 1.2))

# ---- interference check ---------------------------------------------------------------------------------
checks = [('NFC', nfc), ('指静脈', vein), ('VoiceS3R', atom), ('vein-base', base), ('NFC Grove', nfc_plug),
          ('USB head', usb_head), ('USB cable', usb_cable),
          ('PORT.A Grove', porta_plug), ('J3 plug', j3_plug)]
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
    ('nfc', 'NFC Unit 48×24×8', '#f2f2ee', 1, 'mods', nfc),
    ('vein', '指静脈モジュール(仮の箱)', '#2e3538', 1, 'mods', vein),
    ('atom', 'VoiceS3R', '#1fa49a', 1, 'mods', atom),
    ('base', 'vein-base', '#5b8fd6', 1, 'mods', base),
    ('nfcplug', 'NFC 側 Grove プラグ', '#c47f0e', 1, 'mods', nfc_plug),
    ('portaplug', 'PORT.A Grove プラグ', '#c47f0e', 1, 'mods', porta_plug),
    ('j3plug', 'J3 プラグ(指静脈ケーブル)', '#e7e1cf', 1, 'mods', j3_plug),
    ('usbhead', 'USB-C L字の頭', '#24292d', 1, 'mods', usb_head),
    ('usbcable', 'USB ケーブル', '#3a4046', 1, 'mods', usb_cable),
    ('m2', 'M2×16 ネジ(底蓋 → vein-base)', '#a9adb2', 1, 'lid', m2),
    ('lid', '底蓋+台', '#8fa09c', 0.9, 'lid', lid),
]
model = [dict(key=k, label=l, color=c, opacity=o, group=g, data=base64.b64encode(tri(s).tobytes()).decode())
         for k, l, c, o, g, s in parts]
tpl = open(os.path.join(ROOT, 'tools/station_template.html'), encoding='utf-8').read()
os.makedirs(os.path.join(ROOT, 'site/station'), exist_ok=True)
page = os.path.join(ROOT, 'site/station/index.html')
open(page, 'w', encoding='utf-8').write(tpl.replace('__MODEL__', json.dumps(model)).replace('__REV__', REV))
print('wrote', page, os.path.getsize(page), 'bytes')

if bad:
    raise SystemExit('interference: ' + ', '.join(bad))
