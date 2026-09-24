"""Vein Station: desktop enclosure for VoiceS3R on the one-piece station board (pcb/station_board), Finger Vein
Module (A) and Unit NFC, all facing up. The board also carries the RS232 (MAX3232 + straight/cross DIP + DB9 male,
the same gender as the RS232M Module 13.2) for the FC-1200 alcohol checker. No screen, no LAN: one USB-C cable to
the Windows PC carries power and data.
Run from the repository root:  python3 station/build_station.py
Writes station/vein_station_<REV>_{shell,lid}.{step,stl} and the 3D preview site/station/index.html,
and fails if the enclosure collides with a module, plug or cable, or if the shell cannot be lowered onto them.

Coordinates: x = left→right, y = back→front is NEGATIVE (the top-view drawing's y is used as `ys`, Y = -ys),
z = 0 at the top surface, down is negative. Outer 99 × 70 × 27.6.
Every wall is at least 1.0 thick in every direction (DMM's minimum for resin SLA; measured on the STL, r11).
Every connection is on the back wall: the NFC Grove socket, the VoiceS3R's side (USB-C over PORT.A) and the DB9
all sit right behind windows in the back wall, so the cables plug in from outside; the PORT.A ↔ NFC Grove cable
loops outside. The vein module is at the front.
The board hangs on the VoiceS3R Ext.Pin headers; lid rails push it (and the VoiceS3R) up against the lip.
Every module is held the same way: supported from below by the lid, pressed against a lip in the top plate, and
located sideways by a frame (縁取り) hanging from the top plate. No screws in the modules.
The shell goes on from above: a wall opening that something passes through is a slot open at the bottom of the wall,
closed from below by a tongue on the lid (the DB9 D shell and its hex posts).
Module sizes come from the photo measurements (±1–2 mm); the finger vein module is still a 59×26×15 block.
"""
import base64, json, os
import numpy as np
import cadquery as cq

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REV = 'r13'

W, D = 99.0, 70.0            # outer size (x, ys)
WALL, TOP, LID = 2.0, 1.5, 2.0
Z_BOT = -27.6                # bottom of the walls / lid
Z_LID = Z_BOT + LID          # lid top (-25.6): 0.9 under the DB9 pin tails
R_OUT = 4.0
CLR = 0.1
FIT = 0.2                    # side clearance to the locating frames


def box(x0, x1, ys0, ys1, z0, z1):
    return cq.Workplane('XY').box(x1 - x0, ys1 - ys0, z1 - z0, centered=False).translate((x0, -ys1, z0))


def cyl_z(x, ys, r, z0, z1):
    return cq.Workplane('XY').workplane(offset=z0).center(x, -ys).circle(r).extrude(z1 - z0)


def cyl_y(x, ys0, ys1, z, r):
    return cq.Workplane('XZ').workplane(offset=ys0).center(x, z).circle(r).extrude(ys1 - ys0)  # XZ normal is -Y


def rbox(x0, x1, ys0, ys1, z0, z1, r):
    return box(x0, x1, ys0, ys1, z0, z1).edges('|Z').fillet(r)


# ---- modules (reference geometry, placed in the enclosure) -----------------------------------------------
BACK = WALL + FIT             # modules that show a side in the back wall start here
NFC = (3, 27, BACK, BACK + 48)  # 24 × 48, Grove socket at the back
VOICE = (29, 53, BACK, BACK + 24)  # 24 × 24, USB-C / PORT.A side at the back
VEIN = (31, 90, 41, 67)       # 59 × 26, front
TOP_VOICE = 1.0               # top plate thinned around the VoiceS3R (1.0 = the SLA minimum)
VOICE_LIP = 1.2
Z_ATOM_BOT = -TOP_VOICE - 16.8  # -17.6
NX = (NFC[0] + NFC[1]) / 2

nfc = rbox(*NFC, -9.5, -1.5, 1.5)
vein = rbox(*VEIN, -16.5, -1.5, 2.0)
atom = rbox(*VOICE, Z_ATOM_BOT, -TOP_VOICE, 3.0)
# station board, in board coords (x, y; z from the VoiceS3R bottom face). The board is turned 180° (USB-C side to
# the back): x_st = VX - x, ys = VYS + y
VX, VYS = (VOICE[0] + VOICE[1]) / 2, (VOICE[2] + VOICE[3]) / 2
BX0, BX1, BY0, BY1 = -48.0, 12.0, -11.0, 24.0     # pcb/station_board/build_board.py outline


def board(bx0, bx1, by0, by1, z0, z1):
    """Box given in board coords (x, y; z from the VoiceS3R bottom face) -> station coords."""
    return box(VX - bx1, VX - bx0, VYS + by0, VYS + by1, Z_ATOM_BOT + z0, Z_ATOM_BOT + z1)


pcb = board(BX0, BX1, BY0, BY1, -4.1, -2.5)
hdr_plastic = hdr_pins = None
for bx, bys in ((7.62, (2.54, 0, -2.54, -5.08, -7.62)), (-7.62, (0, -2.54, -5.08, -7.62))):
    for by in bys:
        pl = board(bx - 1.27, bx + 1.27, by - 1.27, by + 1.27, -2.5, 0)
        pn = board(bx - 0.32, bx + 0.32, by - 0.32, by + 0.32, -7.1, -2.5)
        hdr_plastic = pl if hdr_plastic is None else hdr_plastic.union(pl)
        hdr_pins = pn if hdr_pins is None else hdr_pins.union(pn)
# parts on the board's Atom side (F), from the KiCad footprints' extents
j3 = board(-35.0, -25.0, 17.2, 24.0, -2.5, 0.9)                      # MX1.25 4P, opening to the vein module
j3_plug = board(-33.0, -27.0, 24.0, 30.0, -2.2, 0.6)
u1 = board(-31.0, -21.0, 3.05, 6.95, -2.5, -0.75)                    # MAX3232 SOIC-16
caps = board(-31.3, -19.2, 10.3, 11.7, -2.5, -1.6).union(board(-19.2, -17.8, 3.6, 6.4, -2.5, -1.6))
sw1 = board(-46.9, -35.5, 0.1, 12.5, -2.5, -0.5)                     # DIP 4, low profile
# DB9 male RA on the board's -y edge: housing, flange on the edge, D shell and hex posts through the back wall
DB9_BX = -31.9
db9_body = board(DB9_BX - 15.0, DB9_BX + 15.0, BY0 + 0.5, BY0 + 10.5, -2.5, 10.0)
db9_flange = board(DB9_BX - 15.4, DB9_BX + 15.4, BY0 - 1.0, BY0, -2.5, 10.0)
db9_shell = board(DB9_BX - 8.5, DB9_BX + 8.5, BY0 - 7.0, BY0 - 1.0, -0.5, 8.0)
tails = board(DB9_BX - 6.5, DB9_BX + 6.5, BY0 + 3.0, BY0 + 8.5, -7.1, -4.1)
DB9_XC, DB9_ZC = VX - DB9_BX, Z_ATOM_BOT + 3.75                      # D-shell centre in station coords
DB9_X0, DB9_X1 = DB9_XC - 15.4, DB9_XC + 15.4
DB9_S0, DB9_S1 = DB9_XC - 17.0, DB9_XC + 17.0        # wall split: 1.7 of wall/tongue outside the post holes
DB9_Z0, DB9_Z1 = Z_ATOM_BOT - 3.5, Z_ATOM_BOT + 11.0                  # cable plug body height
db9_posts = cyl_y(DB9_XC - 12.5, -3, BACK, DB9_ZC, 2.5).union(cyl_y(DB9_XC + 12.5, -3, BACK, DB9_ZC, 2.5))
db9_plug = box(DB9_X0 + 0.25, DB9_X1 - 0.25, -40, 1.0 - 0.2, DB9_Z0 + 0.25, DB9_Z1 - 0.25)
# plugs outside the back wall (the Grove cable between the two Grove plugs loops outside)
usb_plug = box(VX - 6, VX + 6, -22, BACK - 6.5, Z_ATOM_BOT + 4.0, Z_ATOM_BOT + 11.0).union(
    box(VX - 4.2, VX + 4.2, BACK - 6.5, BACK, Z_ATOM_BOT + 6.0, Z_ATOM_BOT + 9.0))    # overmold + USB-C neck
porta_plug = box(VX - 4.9, VX + 4.9, -8, BACK, Z_ATOM_BOT + 0.0, Z_ATOM_BOT + 4.0)
nfc_plug = box(NX - 4.0, NX + 4.0, -6, BACK, -6.7, -1.9)

# ---- enclosure: shell (top plate + walls) ----------------------------------------------------------------
shell = rbox(0, W, 0, D, Z_BOT, 0, R_OUT)
shell = shell.cut(rbox(WALL, W - WALL, WALL, D - WALL, Z_BOT - 1, -TOP, R_OUT - WALL))
# top openings: NFC label window, vein with a 1 mm lip, VoiceS3R with a 1.2 mm lip on a plate thinned to 1.0
shell = shell.cut(box(NFC[0] + 2, NFC[1] - 2, NFC[2] + 8, NFC[3] - 5, -TOP - 1, 1))
shell = shell.cut(rbox(VEIN[0] + 1, VEIN[1] - 1, VEIN[2] + 1, VEIN[3] - 1, -TOP - 1, 1, 1.5))
# the thinned pocket is square: its neighbours (frame, back wall, fill strip) are square, and a rounded pocket left
# crescent-shaped 0.5 mm steps in its corners (r12). It is under the plate, so the square corners do not show.
shell = shell.cut(box(VOICE[0] - FIT, VOICE[1] + FIT, VOICE[2] - FIT, VOICE[3] + FIT, -TOP - 1, -TOP_VOICE))
shell = shell.cut(rbox(VOICE[0] + VOICE_LIP, VOICE[1] - VOICE_LIP, VOICE[2] + VOICE_LIP, VOICE[3] - VOICE_LIP, -TOP - 1, 1, 3.0 - VOICE_LIP))


def frame(r, depth, t=1.2, cuts=()):
    """Locating frame hanging from the top plate: a ring around rectangle r (+FIT), minus `cuts` (plug openings)."""
    x0, x1, y0, y1 = r[0] - FIT, r[1] + FIT, r[2] - FIT, r[3] + FIT
    ring = box(x0 - t, x1 + t, y0 - t, y1 + t, depth, -TOP).cut(box(x0, x1, y0, y1, depth - 1, 0))
    ring = ring.intersect(box(WALL, W - WALL, WALL, D - WALL, depth - 1, 0))
    for c in cuts:
        ring = ring.cut(c)
    return ring


# frames (縁取り) that hold each module in place sideways (the back wall is their back side)
shell = shell.union(frame(NFC, -5.25))
shell = shell.union(frame(VEIN, -5.75))
shell = shell.union(frame(VOICE, -6.75))
# the NFC and VoiceS3R frames run side by side: fill the strip between them so no thin notch is left
shell = shell.union(box(NFC[1] + FIT, VOICE[0] - FIT, BACK, NFC[3] + FIT + 1.2, -5.25, -TOP))
# back wall windows: NFC Grove socket, VoiceS3R side (PORT.A at the bottom, USB-C above it)
shell = shell.cut(box(NX - 5.5, NX + 5.5, -1, WALL + 1, -7.2, -TOP))
shell = shell.cut(box(VX - 7.0, VX + 7.0, -1, WALL + 1, Z_ATOM_BOT - 0.5, Z_ATOM_BOT + 12.0))
# DB9: the back wall is split at the D-shell centre. The shell keeps the upper half of the D opening, the post
# holes and the 1 mm recess outside for the cable plug (the wall there is 1 mm so the D shell still engages the plug
# fully); everything below the centre is a tongue on the lid. The flange rests on the inside of both.
DB9_D = box(DB9_XC - 8.65, DB9_XC + 8.65, -1, WALL + 1, Z_ATOM_BOT - 0.8, Z_ATOM_BOT + 8.3)
# the post holes are joined to the D opening (r13): a 1.05 mm web between them was a thin post like the old lid tabs.
# The plug hood covers the whole opening from outside.
DB9_HOLES = (cyl_y(DB9_XC - 12.5, -1, WALL + 1, DB9_ZC, 2.8).union(cyl_y(DB9_XC + 12.5, -1, WALL + 1, DB9_ZC, 2.8))
             .union(box(DB9_XC - 12.5, DB9_XC + 12.5, -1, WALL + 1, DB9_ZC - 2.8, DB9_ZC + 2.8)))
DB9_RECESS = box(DB9_X0, DB9_X1, -1, 1.0, DB9_Z0, DB9_Z1)
shell = shell.cut(box(DB9_S0, DB9_S1, -1, WALL + 1, Z_BOT - 1, DB9_ZC))
shell = shell.cut(DB9_D).cut(DB9_HOLES).cut(DB9_RECESS)
# screw bosses (M3 self-tapping, pilot 2.5): front-left beside the vein module, back-right beside the board
SCREWS = [(8.0, 60.0), (W - 6.7, 20.0)]   # head counterbore (r3.0) keeps 1.6 to the lid edge
PAD = 1.0                                 # pad on the lid around each screw: 2.0 - 1.2 counterbore + 1.0 = 1.8
for x, ys in SCREWS:
    shell = shell.union(cyl_z(x, ys, 2.6, Z_LID + PAD, -TOP).cut(cyl_z(x, ys, 1.25, Z_LID - 1, -TOP - 2)))

# ---- enclosure: lid with pedestals ----------------------------------------------------------------------
lid = rbox(WALL + CLR, W - WALL - CLR, WALL + CLR, D - WALL - CLR, Z_BOT, Z_LID, R_OUT - WALL - CLR)
# no hook tabs (r12): the lid sits inside the walls, so the two diagonal M3 screws are enough to hold it
# NFC pedestal (pushes the unit up against the top plate), with a relief for the screw head on its back
ped_nfc = box(NFC[0] + 3, NFC[1] - 3, NFC[2] + 3, NFC[3] - 3, Z_LID, -9.5).cut(cyl_z(NX, NFC[2] + 12, 3.0, Z_LID, 0))
# vein pedestal: two rails under the long edges; the back rail leaves room for the J3 plug
J3X0, J3X1 = VX + 27.0 - 1.0, VX + 33.0 + 1.0
ped_vein = (box(VEIN[0] + 4, J3X0, 43, 47, Z_LID, -16.5).union(box(J3X1, VEIN[1] - 4, 43, 47, Z_LID, -16.5))
            .union(box(VEIN[0] + 4, VEIN[1] - 4, 61, 65, Z_LID, -16.5)))
# board supports: rails under the back and front edges and between the VoiceS3R and the RS232 parts
# (clear of the J1/J2 and DB9 pin tails). They push the board + VoiceS3R up against the lip.
pcb_sup = (board(BX0 + 1, BX1 - 1, BY0 + 0.5, BY0 + 2.0, -30, -4.1)
           .union(board(BX0 + 1, BX1 - 1, BY1 - 2.0, BY1 - 0.5, -30, -4.1))
           .union(board(-14.0, -12.5, BY0 + 3.0, BY1 - 3.0, -30, -4.1)))
pcb_sup = pcb_sup.intersect(box(0, W, 0, D, Z_LID, 0))
lid = lid.union(ped_nfc).union(ped_vein).union(pcb_sup)
# tongue that closes the DB9 slot from below (in the wall line, joined to the lid under the board)
lid = lid.union(box(DB9_S0 + CLR, DB9_S1 - CLR, 0, WALL, Z_BOT, DB9_ZC)
                .union(box(DB9_S0 + CLR, DB9_S1 - CLR, WALL, WALL + CLR + 0.5, Z_BOT, Z_LID))
                .cut(DB9_D).cut(DB9_HOLES).cut(DB9_RECESS))
for x, ys in SCREWS:
    lid = lid.union(cyl_z(x, ys, 3.8, Z_LID, Z_LID + PAD)).cut(cyl_z(x, ys, 1.7, Z_BOT - 1, Z_LID + 1)).cut(cyl_z(x, ys, 3.0, Z_BOT - 1, Z_BOT + 1.2))

# ---- interference check ---------------------------------------------------------------------------------
checks = [('NFC', nfc), ('指静脈', vein), ('VoiceS3R', atom), ('board', pcb), ('header plastic', hdr_plastic),
          ('header pins', hdr_pins), ('J3', j3), ('J3 plug', j3_plug), ('MAX3232', u1), ('caps', caps), ('DIP', sw1),
          ('DB9 body', db9_body), ('DB9 flange', db9_flange), ('DB9 shell', db9_shell), ('DB9 posts', db9_posts),
          ('DB9 plug', db9_plug), ('DB9 tails', tails), ('NFC Grove', nfc_plug), ('USB plug', usb_plug),
          ('PORT.A Grove', porta_plug)]
bad = []
for name, obj in checks:
    for cname, case in (('shell', shell), ('lid', lid)):
        v = case.intersect(obj).val().Volume()
        print(f'interference {cname:5s} x {name:12s} = {v:.3f} mm3')
        if v > 0.01:
            bad.append(f'{cname}/{name}')
# assembly: the shell is lowered from above onto the lid with everything on it, so nothing inside may sit under
# shell material in its own footprint — sweep each inside part down and check it against the shell (catches a wall
# closed under something that passes through it). The plugs outside go in after assembly and are not swept.
for name, obj in checks:
    if name in ('DB9 plug', 'NFC Grove', 'USB plug', 'PORT.A Grove'):
        continue
    sweep = obj
    for dz in (2, 4, 8, 16, 32):
        sweep = sweep.union(obj.translate((0, 0, -dz)))
    v = shell.intersect(sweep).val().Volume()
    print(f'assembly  shell x {name:12s} lowered = {v:.3f} mm3')
    if v > 0.01:
        bad.append(f'assembly/{name}')
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


def downloads_html(files, site_dir):
    """Copy the STLs next to the page and return the download links (file name carries the version)."""
    import shutil
    rows = []
    for label, path in files:
        name = os.path.basename(path)
        shutil.copyfile(path, os.path.join(site_dir, name))
        kb = os.path.getsize(path) // 1024
        rows.append(f'<a href="{name}" download>{label}<span>{name} · {kb} KB</span></a>')
    rows.append('<p>DMM.make の本番材料は「PA12｜MJF」(グレー、磨きなし)。形の確認だけならエコノミーレジン(SLA)。</p>')
    return ''.join(rows)


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
    ('pcb', 'Station 基板(1 枚)', '#1f7a4d', 1, 'mods', pcb),
    ('hdrpl', 'ピンヘッダー樹脂', '#2b2f33', 1, 'mods', hdr_plastic),
    ('hdrpin', 'ピン', '#d8b25a', 1, 'mods', hdr_pins),
    ('j3', 'J3 MX1.25 4P(指静脈)', '#f1efe8', 1, 'mods', j3),
    ('j3plug', 'J3 プラグ(指静脈ケーブル)', '#e7e1cf', 1, 'mods', j3_plug),
    ('u1', 'U1 MAX3232', '#202326', 1, 'mods', u1),
    ('caps', 'C1〜C5 0.1µF', '#b8a27a', 1, 'mods', caps),
    ('sw1', 'SW1 ストレート/クロス DIP', '#c0392b', 1, 'mods', sw1),
    ('db9', 'J4 DB9 オス(RS232M と同じ)', '#8a8f96', 1, 'mods', db9_body.union(db9_flange).union(db9_shell).union(db9_posts)),
    ('db9plug', 'DB9 プラグ(FC-1200 へ)', '#5c6166', 1, 'mods', db9_plug),
    ('usbplug', 'USB-C プラグ(Windows PC へ)', '#24292d', 1, 'mods', usb_plug),
    ('portaplug', 'PORT.A Grove プラグ(外で NFC へ折り返し)', '#c47f0e', 1, 'mods', porta_plug),
    ('nfcplug', 'NFC 側 Grove プラグ', '#c47f0e', 1, 'mods', nfc_plug),
    ('lid', '底蓋+台', '#8fa09c', 0.9, 'lid', lid),
]
model = [dict(key=k, label=l, color=c, opacity=o, group=g, data=base64.b64encode(tri(s).tobytes()).decode())
         for k, l, c, o, g, s in parts]
SUB = ('VoiceS3R・指静脈・NFC と、FC-1200 用の RS232(DB9)を 1 枚の基板で収める卓上筐体の案。接続口はすべて奥の壁'
       '(画面なし、LAN なし、USB 1 本で Windows PC へ)。ドラッグで回転、ホイール/ピンチで拡大。')
DIMS = [('外形', f'{W:g} × {D:g} × {-Z_BOT:g}'), ('壁 / 天板 / 底蓋', '2 / 1.5 / 2'),
        ('奥の壁', 'NFC Grove ・ VoiceS3R 側面(USB-C / PORT.A)・ DB9'),
        ('DB9', 'D 部の中心で上下分割(下は底蓋の舌)、外側 1 mm の座ぐり'),
        ('基板', '60 × 35、VoiceS3R の下と DB9 の横'), ('RS232', 'MAX3232 + DIP でストレート/クロス切替'),
        ('底蓋', 'M3 × 2(対角)、爪なし'), ('VoiceS3R', '返し 1.2(天板 1.0)/ 縁取り')]
NOTE = ('モジュールは写真からの実測(±1〜2 mm)による簡略形状です。指静脈モジュールは採寸待ちのため仮の箱、DB9 と基板上の部品は'
        'KiCad のフットプリント寸法からの簡略形状です。DIP は底蓋を開けて設定します。単位 mm。')
dims = ''.join(f'        <tr><td>{k}</td><td>{v}</td></tr>\n' for k, v in DIMS)
tpl = open(os.path.join(ROOT, 'tools/station_template.html'), encoding='utf-8').read()
os.makedirs(os.path.join(ROOT, 'site/station'), exist_ok=True)
page = os.path.join(ROOT, 'site/station/index.html')
DOWNLOADS = downloads_html([('ケース上部(天板+壁)', os.path.join(out, f'vein_station_{REV}_shell.stl')),
                            ('底蓋+台', os.path.join(out, f'vein_station_{REV}_lid.stl'))], os.path.join(ROOT, 'site/station'))
page_html = (tpl.replace('__MODEL__', json.dumps(model)).replace('__REV__', REV).replace('__SUB__', SUB)
             .replace('__DIMS__', dims).replace('__NOTE__', NOTE).replace('__TZ__', '-15')
             .replace('__DOWNLOADS__', DOWNLOADS))
open(page, 'w', encoding='utf-8').write(page_html)
print('wrote', page, os.path.getsize(page), 'bytes')

if bad:
    raise SystemExit('interference: ' + ', '.join(bad))
