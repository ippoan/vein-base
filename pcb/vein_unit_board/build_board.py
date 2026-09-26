"""Vein Unit board (u2): the board inside the Takachi SIC5-9-2B of the vein unit (station/build_vein_unit.py sic).
The finger vein module sits on it with VHB tape; the board carries
  - J2: Grove (HY2.0 4P right angle, JST PH S4B-PH-SM4-TB footprint), opening to +x through a hole in the case's end
        wall, to the PortABC's PORT.C: 1 = G6 (yellow), 2 = G5 (white), 3 = 5V, 4 = GND
  - U1 XC6206P332MR 5 V -> 3.3 V (200 mA; the module takes 43 mA) with C1 (in) and C2 (out) 1 uF, beside J1 on the
        board edge side (clear of the module and of the cable's run above the board)
  - J1: MX1.25 4P right angle (Molex 53261-0471, MP pads narrowed: pcb/vein_base.pretty), opening to -x, in the gap
        beside the module, for the kit's 9P -> 4P cable re-pinned to 3..6: 1 = RXD (<- G5), 2 = TXD (-> G6),
        3 = 3V3, 4 = GND (the order of J3 on vein-base / the station board)
  - four M2 holes over the case's PCB bosses (66 × 25)
Board coords = the unit's: origin = case centre, x along the case (Grove end +x), y across, F faces up (the module).
The outline and the holes follow the case (STP measured, see station/build_vein_unit.py); the module lies on
x -29.5..29.5, y -16.5..9.5, so nothing but flat pads and tracks goes under it. Keep J1 / the module's place in step
with station/build_vein_unit.py.
Routing is written here (a handful of tracks). Run with KiCad's python from pcb/vein_unit_board/.
"""
import os
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
REV = 'u2'
NAME = 'vein_unit_board'
FP = '/usr/share/kicad/footprints/'
OX, OY = 100.0, 100.0
mm = pcbnew.FromMM

BX, BY, BR = 39.0, 19.5, 9.4         # outline: 78 × 39, R9.4 (the case inside ±39.6 × ±20.1 R10, 0.6 in)
HOLES = [(sx * 33.0, sy * 12.5) for sx in (1, -1) for sy in (1, -1)]
VEIN = (-29.5, 29.5, -16.5, 9.5)
JC = 14.3                            # J1's centre across (pads 9.6..19.0, nails 10.3..18.3)
XJ = 2.65                            # J1's origin: its front (the opening) at x = 0
XG = BX - 4.45 - 1.3                 # J2's origin: its footprint front 1.3 inside the edge; JLC's HY2.0 body stands
                                     # 0.7 further out (assembly preview), so it ends 0.6 inside the edge, 1.2 off the case wall


def P(x, y):
    return pcbnew.VECTOR2I(mm(OX + x), mm(OY - y))


def xy(v):
    return (round(pcbnew.ToMM(v.x) - OX, 3), round(OY - pcbnew.ToMM(v.y), 3))


b = pcbnew.BOARD()
ds = b.GetDesignSettings()
ds.SetCopperLayerCount(2)
ds.SetBoardThickness(mm(1.6))
nc = ds.m_NetSettings.m_DefaultNetClass
nc.SetClearance(mm(0.2)); nc.SetTrackWidth(mm(0.3)); nc.SetViaDiameter(mm(0.6)); nc.SetViaDrill(mm(0.3))

nets = {}
for n in ['GND', '5V', '3V3', 'RXD', 'TXD']:
    ni = pcbnew.NETINFO_ITEM(b, n); b.Add(ni); nets[n] = ni

LIBS = {}


def load(lib, name, ref, value, x, y, rot=0, base=FP, uri_base=FP):
    fp = pcbnew.FootprintLoad(base + lib, name)
    nick = lib.removesuffix('.pretty'); LIBS[nick] = uri_base + lib
    fp.SetFPID(pcbnew.LIB_ID(nick, name))
    fp.SetReference(ref); fp.SetValue(value)
    b.Add(fp)
    fp.SetPosition(P(x, y))
    fp.SetOrientationDegrees(rot)
    return fp


def wire(fp, table):
    for p in fp.Pads():
        n = table.get(p.GetNumber())
        if n:
            p.SetNet(nets[n])


def pad(fp, num):
    return xy([p for p in fp.Pads() if p.GetNumber() == num][0].GetPosition())


# ---- J2 Grove on the +x edge, opening +x (footprint front = its +y, turned 90°)
J2 = load('Connector_JST.pretty', 'JST_PH_S4B-PH-SM4-TB_1x04-1MP_P2.00mm_Horizontal', 'J2', 'Grove HY2.0-4P RA', XG, 0, rot=90)
wire(J2, {'1': 'TXD', '2': 'RXD', '3': '5V', '4': 'GND', 'MP': 'GND'})

# ---- J1 vein cable, opening -x (footprint front = its +y, turned 270°)
J1 = load('vein_base.pretty', 'Molex_PicoBlade_53261-0471_1x04-1MP_P1.25mm_Horizontal_NarrowMP', 'J1',
          'MX1.25-4P RA (Molex 53261-0471)', XJ, JC, rot=270, base=os.path.join(HERE, '..') + '/', uri_base='${KIPRJMOD}/../')
wire(J1, {'1': 'RXD', '2': 'TXD', '3': '3V3', '4': 'GND', 'MP': 'GND'})

# ---- U1 LDO and its caps beside J1, towards the board edge (SOT-23: 1 VSS, 2 VOUT, 3 VIN)
UX, UY = 13.0, 17.3
U1 = load('Package_TO_SOT_SMD.pretty', 'SOT-23', 'U1', 'XC6206P332MR', UX, UY)
wire(U1, {'1': 'GND', '2': '3V3', '3': '5V'})
C1 = load('Capacitor_SMD.pretty', 'C_0603_1608Metric', 'C1', '1uF', UX + 3.0, UY, rot=90)
wire(C1, {'1': '5V', '2': 'GND'})
C2 = load('Capacitor_SMD.pretty', 'C_0603_1608Metric', 'C2', '1uF', UX - 3.0, UY, rot=90)
wire(C2, {'1': '3V3', '2': 'GND'})
for fp in (U1, C1, C2):
    fp.Reference().SetVisible(False)             # no room for the refs by the edge (the CPL still has them)

# ---- M2 holes over the case's bosses
for i, (x, y) in enumerate(HOLES, 1):
    load('MountingHole.pretty', 'MountingHole_2.2mm_M2', f'H{i}', 'M2', x, y)

for fp in (J1, J2, U1, C1, C2):
    print(fp.GetReference(), {p.GetNumber(): pad(fp, p.GetNumber()) for p in fp.Pads()})

# ---- outline: 78 × 39 rounded rectangle


def seg(a, c, layer=pcbnew.Edge_Cuts):
    s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(P(*a)); s.SetEnd(P(*c)); s.SetLayer(layer); s.SetWidth(mm(0.1)); b.Add(s)


def arc(cx, cy, a0):
    import math
    pts = [(cx + BR * math.cos(math.radians(a)), cy + BR * math.sin(math.radians(a))) for a in (a0, a0 + 45, a0 + 90)]
    s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_ARC)
    s.SetArcGeometry(P(*pts[0]), P(*pts[1]), P(*pts[2])); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.1)); b.Add(s)


ix, iy = BX - BR, BY - BR
seg((-ix, -BY), (ix, -BY)); seg((BX, -iy), (BX, iy)); seg((ix, BY), (-ix, BY)); seg((-BX, iy), (-BX, -iy))
arc(ix, -iy, -90); arc(ix, iy, 0); arc(-ix, iy, 90); arc(-ix, -iy, 180)

# ---- tracks: RXD / TXD drop to B.Cu beside J1 and run under the module to the Grove; 3V3 / 5V on F.Cu / B.Cu;
# GND is a pour on both layers, stitched by vias


def track(pts, net, layer=pcbnew.F_Cu, w=0.3):
    for a, c in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(b); t.SetStart(P(*a)); t.SetEnd(P(*c)); t.SetWidth(mm(w))
        t.SetLayer(layer); t.SetNet(nets[net]); b.Add(t)


def via(x, y, net):
    v = pcbnew.PCB_VIA(b); v.SetPosition(P(x, y)); v.SetWidth(mm(0.6)); v.SetDrill(mm(0.3)); v.SetNet(nets[net]); b.Add(v)


j1 = {n: pad(J1, n) for n in '1234'}
j2 = {n: pad(J2, n) for n in '1234'}
u1 = {n: pad(U1, n) for n in '123'}
c1 = {n: pad(C1, n) for n in '12'}
c2 = {n: pad(C2, n) for n in '12'}
XV = j1['1'][0] + 1.85                # the two vias beside J1
XE = j2['1'][0] - 3.0                 # the two vias before the Grove
for net, pin, xd, jp in (('RXD', '1', 8.9, '2'), ('TXD', '2', 7.9, '1')):
    y0, y1 = j1[pin][1], j2[jp][1]
    track([j1[pin], (XV, y0)], net); via(XV, y0, net)
    track([(XV, y0), (xd, y0), (xd, y1), (XE, y1)], net, layer=pcbnew.B_Cu); via(XE, y1, net)
    track([(XE, y1), j2[jp]], net)
# 3V3: J1-3 -> along +x under the vias -> up to C2-1 -> U1-2
track([j1['3'], (c2['1'][0], j1['3'][1]), c2['1'], (u1['2'][0], c2['1'][1]), u1['2']], '3V3')
# 5V: J2-3 -> via under the Grove body -> B.Cu along y = +1 and up -> via -> C1-1 -> U1-3
v5a = (j2['3'][0] + 2.4, j2['3'][1]); v5b = (c1['1'][0] + 1.5, c1['1'][1])
track([j2['3'], v5a], '5V'); via(*v5a, '5V')
track([v5a, (v5b[0], v5a[1]), v5b], '5V', layer=pcbnew.B_Cu); via(*v5b, '5V')
track([v5b, c1['1'], (u1['3'][0] + 0.9, c1['1'][1]), u1['3']], '5V')
# GND stitching vias (the pours on both layers carry GND)
for x, y in [(-20.0, -8.0), (0.0, -12.0), (20.0, -12.0), (-20.0, 6.0), (0.0, 6.0), (20.0, 6.0), (-34.0, 0.0),
             (24.0, 17.5), (-4.0, 16.0), (35.0, 9.0), (35.0, -9.0)]:
    via(x, y, 'GND')


def text(s, x, y, layer=pcbnew.F_SilkS, size=1.0, rot=0):
    t = pcbnew.PCB_TEXT(b); t.SetText(s); t.SetPosition(P(x, y)); t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size))); t.SetTextThickness(mm(0.15)); t.SetTextAngleDegrees(rot)
    if layer == pcbnew.B_SilkS:
        t.SetMirrored(True)
    b.Add(t)


text('VEIN MODULE (VHB)', 0, -3.5, size=1.2)
text('J1 1RX 2TX 3V3 4G', 23.0, 18.0, size=0.8)
text('GROVE 1:G6 2:G5 3:5V 4:G', 26.0, -17.5, size=0.8)
text(f'vein unit board {REV}', 0, 0, layer=pcbnew.B_SilkS)

os.chdir(HERE)
b.Save(f'{NAME}.kicad_pcb')
# GND pours on both layers over the whole board, filled on a reloaded board (as the station board does)
b = pcbnew.LoadBoard(f'{NAME}.kicad_pcb')
for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
    z = pcbnew.ZONE(b); z.SetLayer(layer); z.SetNet(b.FindNet('GND'))
    ol = z.Outline(); ol.NewOutline()
    for x, y in ((-BX, -BY), (BX, -BY), (BX, BY), (-BX, BY)):
        ol.Append(mm(OX + x), mm(OY - y))
    z.SetLocalClearance(mm(0.3)); z.SetMinThickness(mm(0.25))
    b.Add(z)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(f'{NAME}.kicad_pcb')
LIBS['MountingHole'] = FP + 'MountingHole.pretty'
with open('fp-lib-table', 'w') as f:
    f.write('(fp_lib_table\n  (version 7)\n')
    for nick, uri in sorted(LIBS.items()):
        f.write(f'  (lib (name "{nick}")(type "KiCad")(uri "{uri}")(options "")(descr ""))\n')
    f.write(')\n')
print('saved')
