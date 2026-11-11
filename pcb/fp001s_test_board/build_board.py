"""FP001S test board (t1): a small board to try the Grow FP001S face / palm vein module (Hangzhou Grow, user manual
V1.01) from a PC, with nothing but USB cables:
  - J1  USB-C, power only (a USB charger): VBUS -> 5V. CC1 / CC2 5.1 k (R1 / R2). Its D+ / D- are not connected.
        The FP001S takes 400 mA (175 mA standby), so it is not powered from the PC's port.
  - J2  USB-C, data (to the PC): D+ / D- through U2 (USBLC6-2SC6) to U3's upstream port. CC1 / CC2 5.1 k (R3 / R4).
        Its VBUS pins are left unconnected: the PC's 5 V and the charger's 5 V must not meet. U2's VBUS pin (the
        clamp reference) is on the board's 5V, so the board works only with J1 powered (the hub needs it anyway).
  - U3  CH334F (QFN-24 4x4) USB 2.0 hub, self-powered from 5V (V5 -> internal LDO -> VDD33 = HUB33), Y1 12 MHz
        (load caps inside the CH334). Port 1 -> the FP001S's USB (UVC / MJPEG 320x240 15 fps, e.g. PotPlayer),
        port 2 -> U4. Ports 3 / 4 unused. RESET# / PSELF (self-powered) / LED / OVCUR# / PWREN# left open.
  - U4  CH340C (SOP-16, clock inside) at 3.3 V (VCC = V3 = 3V3): TXD -> FP001S RXD, RXD <- FP001S TXD (115200 8N1,
        Grow's Test Demo or our own code)
  - U1  AMS1117-3.3 (SOT-223): 5V -> 3V3 for the FP001S and U4. About 0.7 W at 400 mA: its tab (= 3V3) sits in a
        3V3 copper area on both layers (U1_HEAT, stitched by vias) that carries the heat.
  - J3  JST SH 1.0 6P (SM06B-SRSS-TB, horizontal, opening +y) for the FP001S cable: pins as the module's
        (manual 1.3.2): 1 VCC (3V3), 2 TXD (module out), 3 RXD (module in), 4 GND, 5 D-, 6 D+.
        SH_REVERSED: if the module's cable is crossed (its pin 1 on the other end's pin 6, as Pimoroni / Adafruit SH
        cables are), set it True so the board's pin 6 takes VCC. CHECK THE CABLE BEFORE ORDERING: swapped, the
        module gets 3.3 V on GND.
  - D1 + R5: 3V3 power LED. H1..H4: M2 holes in the corners.
Board coords: origin = board centre, both USB-C on the -y edge (J2 data on -x, J1 power on +x), J3 on the +y edge.
Routing comes from freerouting and is kept in fp001s_test_board.ses (the board file itself is always generated):
    python3 build_board.py dsn   # placement only -> .dsn (freerouting 2.4.1 -> .ses)
    python3 build_board.py       # placement + tracks / vias from the .ses -> fp001s_test_board.kicad_pcb
Run with KiCad's python from pcb/fp001s_test_board/.
"""
import math, os, re, sys
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from kicad_ses import import_ses  # noqa: E402

REV = 't1'
NAME = 'fp001s_test_board'
SH_REVERSED = False            # see the docstring: True if the module's SH cable crosses 1 <-> 6
FP = '/usr/share/kicad/footprints/'
OX, OY = 100.0, 100.0
mm = pcbnew.FromMM

X0, X1, Y0, Y1 = -21.0, 21.0, -16.0, 16.0          # 42 x 32
HOLES = [(sx * 18.5, sy * 13.5) for sx in (-1, 1) for sy in (-1, 1)]
POS = {}                                            # ref -> (x, y, rot), overriding the places below


def P(x, y):
    return pcbnew.VECTOR2I(mm(OX + x), mm(OY - y))


def xy(v):
    return (round(pcbnew.ToMM(v.x) - OX, 3), round(OY - pcbnew.ToMM(v.y), 3))


b = pcbnew.BOARD()
ds = b.GetDesignSettings()
ds.SetCopperLayerCount(2)
ds.SetBoardThickness(mm(1.6))
nc = ds.m_NetSettings.m_DefaultNetClass
nc.SetClearance(mm(0.15)); nc.SetTrackWidth(mm(0.2))   # 0.2 / 0.15 fits the CH334F's 0.5 pitch
nc.SetViaDiameter(mm(0.6)); nc.SetViaDrill(mm(0.3))

nets = {}
for n in ['GND', '5V', '3V3', 'HUB33', 'J2VB1', 'J2VB2', 'CC1P', 'CC2P', 'CC1D', 'CC2D', 'UDP', 'UDN', 'XI', 'XO',
          'FPDP', 'FPDM', 'SDP', 'SDN', 'FPTX', 'FPRX', 'LEDA']:
    ni = pcbnew.NETINFO_ITEM(b, n); b.Add(ni); nets[n] = ni

LIBS = {}


def load(lib, name, ref, value, x, y, rot=0):
    fp = pcbnew.FootprintLoad(FP + lib, name)
    nick = lib.removesuffix('.pretty'); LIBS[nick] = FP + lib
    fp.SetFPID(pcbnew.LIB_ID(nick, name))
    fp.SetReference(ref); fp.SetValue(value)
    b.Add(fp)
    x, y, rot = POS.get(ref, (x, y, rot))
    fp.SetPosition(P(x, y))
    fp.SetOrientationDegrees(rot)
    return fp


def wire(fp, table):
    for p in fp.Pads():
        n = table.get(p.GetNumber())
        if n:
            p.SetNet(nets[n])


def two(lib, name, ref, value, a, c, x, y, rot=0):
    fp = load(lib, name, ref, value, x, y, rot)
    wire(fp, {'1': a, '2': c})
    return fp


def R(ref, value, a, c, x, y, rot=0):
    return two('Resistor_SMD.pretty', 'R_0603_1608Metric', ref, value, a, c, x, y, rot)


def C(ref, value, a, c, x, y, rot=0):
    size = '0805_2012' if value in ('10uF', '22uF') else '0603_1608'
    return two('Capacitor_SMD.pretty', f'C_{size}Metric', ref, value, a, c, x, y, rot)


USB_GND = {'A1': 'GND', 'A12': 'GND', 'B1': 'GND', 'B12': 'GND', 'S1': 'GND'}

# ======== J2 data USB-C (-x) -> U2 ESD -> U3 hub ========
J2 = load('Connector_USB.pretty', 'USB_C_Receptacle_HRO_TYPE-C-31-M-12', 'J2', 'USB-C data (PC)', -10.0, Y0 + 3.05)
wire(J2, {**USB_GND, 'A5': 'CC1D', 'B5': 'CC2D',
          'A4': 'J2VB1', 'B9': 'J2VB1', 'A9': 'J2VB2', 'B4': 'J2VB2',   # VBUS left open (each stacked pair on its own
                                                                       # net only so DRC sees one pad, not a bridge)
          'A6': 'UDP', 'B6': 'UDP', 'A7': 'UDN', 'B7': 'UDN'})
R('R3', '5.1k', 'CC1D', 'GND', -15.5, -5.2, 90)
R('R4', '5.1k', 'CC2D', 'GND', -4.5, -5.2, 90)
U2 = load('Package_TO_SOT_SMD.pretty', 'SOT-23-6', 'U2', 'USBLC6-2SC6', -10.0, -5.4, 90)
wire(U2, {'1': 'UDP', '6': 'UDP', '3': 'UDN', '4': 'UDN', '2': 'GND', '5': '5V'})

U3 = load('Package_DFN_QFN.pretty', 'QFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm', 'U3', 'CH334F', -8.0, 1.0, 180)   # upstream (14 / 15) to -x over U2, ports 1 / 2 to +y, XI / XO to +x
wire(U3, {'25': 'GND', '3': 'XO', '4': 'XI', '9': 'SDN', '10': 'SDP', '11': 'FPDM', '12': 'FPDP',
          '14': 'UDN', '15': 'UDP', '19': '5V', '20': 'HUB33'})
XT = load('Crystal.pretty', 'Crystal_SMD_3225-4Pin_3.2x2.5mm', 'Y1', '12MHz', -3.5, 1.0, 270)
wire(XT, {'1': 'XI', '3': 'XO', '2': 'GND', '4': 'GND'})
C('C1', '1uF', '5V', 'GND', -10.0, -2.5, 0)               # V5 (pins 19 / 20 face -y)
C('C2', '10uF', 'HUB33', 'GND', -6.5, -2.7, 0)          # VDD33
C('C3', '100nF', 'HUB33', 'GND', -2.6, -2.6, 90)

# ======== U4 CH340C (USB-UART) on hub port 2 ========
U4 = load('Package_SO.pretty', 'SOIC-16_3.9x9.9mm_P1.27mm', 'U4', 'CH340C', 6.0, 3.5, 90)
wire(U4, {'1': 'GND', '2': 'FPRX', '3': 'FPTX', '4': '3V3', '5': 'SDP', '6': 'SDN', '16': '3V3'})
C('C4', '100nF', '3V3', 'GND', 6.0, 8.4, 0)

# ======== J1 power USB-C (+x) -> U1 AMS1117 ========
J1 = load('Connector_USB.pretty', 'USB_C_Receptacle_HRO_TYPE-C-31-M-12', 'J1', 'USB-C power (charger)', 10.0, Y0 + 3.05)
wire(J1, {**USB_GND, 'A4': '5V', 'A9': '5V', 'B4': '5V', 'B9': '5V', 'A5': 'CC1P', 'B5': 'CC2P'})
R('R1', '5.1k', 'CC1P', 'GND', 4.5, -5.2, 90)
R('R2', '5.1k', 'CC2P', 'GND', 15.5, -5.2, 90)
C('C5', '10uF', '5V', 'GND', 10.0, -5.6, 90)
U1 = load('Package_TO_SOT_SMD.pretty', 'SOT-223-3_TabPin2', 'U1', 'AMS1117-3.3', 15.5, 1.0, 90)
wire(U1, {'1': 'GND', '2': '3V3', '3': '5V'})
U1_HEAT = (12.0, 19.8, -0.6, 5.7)        # x0, x1, y0, y1 of the 3V3 heat area (tab at the +y side after the turn)
_tab = xy(max((p for p in U1.Pads() if p.GetNumber() == '2'), key=lambda p: p.GetSize().x * p.GetSize().y).GetPosition())
HEAT_VIAS = [(_tab[0] + dx, _tab[1] + dy) for dx in (-2.9, 2.9) for dy in (-1.2, 0.0, 1.2)]
C('C6', '22uF', '3V3', 'GND', 15.5, 7.2, 0)
C('C7', '100nF', '3V3', 'GND', 18.6, 7.2, 90)
two('LED_SMD.pretty', 'LED_0603_1608Metric', 'D1', 'PWR (3V3)', 'GND', 'LEDA', 12.0, 12.2, 0)   # 1 = K, 2 = A
R('R5', '1k', '3V3', 'LEDA', 8.8, 12.2, 0)

# ======== J3 FP001S (SH 1.0 6P, opening +y) ========
J3 = load('Connector_JST.pretty', 'JST_SH_SM06B-SRSS-TB_1x06-1MP_P1.00mm_Horizontal', 'J3', 'FP001S (SH1.0 6P)',
          0.0, Y1 - 3.4, 180)
FP_PINS = ['3V3', 'FPTX', 'FPRX', 'GND', 'FPDM', 'FPDP']           # the module's pins 1..6
jn = {str(i + 1): n for i, n in enumerate(reversed(FP_PINS) if SH_REVERSED else FP_PINS)}
wire(J3, {**jn, 'MP': 'GND'})
# J3's opening must face the +y edge: its signal pads sit behind (towards -y) its mounting pads
sig = [xy(p.GetPosition())[1] for p in J3.Pads() if p.GetNumber() != 'MP']
mp = [xy(p.GetPosition())[1] for p in J3.Pads() if p.GetNumber() == 'MP']
assert max(sig) < min(mp), 'J3 opening is not +y'

for i, (x, y) in enumerate(HOLES, 1):
    load('MountingHole.pretty', 'MountingHole_2.2mm_M2', f'H{i}', 'M2', x, y)

# ---- outline
EDGE = [(X0, Y0), (X1, Y0), (X1, Y1), (X0, Y1)]
for (a, c), (d, e) in zip(EDGE, EDGE[1:] + EDGE[:1]):
    s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(P(a, c)); s.SetEnd(P(d, e)); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.1)); b.Add(s)


def text(s, x, y, layer=pcbnew.F_SilkS, size=1.0, rot=0):
    t = pcbnew.PCB_TEXT(b); t.SetText(s); t.SetPosition(P(x, y)); t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size))); t.SetTextThickness(mm(0.15)); t.SetTextAngleDegrees(rot)
    if layer == pcbnew.B_SilkS:
        t.SetMirrored(True)
    b.Add(t)


# silk: 1 character ~ 0.8 x size wide, centred: keep both ends inside the outline
short = {'3V3': '3V3', 'FPTX': 'TX', 'FPRX': 'RX', 'GND': 'G', 'FPDM': 'D-', 'FPDP': 'D+'}
SILK = [('PC (DATA)', -10.0, -11.2, 0.8), ('5V POWER', 10.0, -11.2, 0.8),
        ('FP001S (SH1.0)', -12.0, 11.3, 0.8),
        ('J3 ' + ' '.join(f'{n}:{short[jn[n]]}' for n in '123'), -12.0, 10.0, 0.8),
        ('   ' + ' '.join(f'{n}:{short[jn[n]]}' for n in '456'), -12.0, 8.7, 0.8)]
for t, x, y, sz in SILK:
    assert X0 + 0.3 <= x - len(t) * 0.4 * sz and x + len(t) * 0.4 * sz <= X1 - 0.3, t
    text(t, x, y, size=sz)
text(f'FP001S test board {REV}', 0, 0, layer=pcbnew.B_SilkS)
text('CHECK THE SH CABLE: PIN 1 = 3V3', 0, -2.0, layer=pcbnew.B_SilkS, size=0.8)


def stitch(b, pitch=2.5, clr=0.25):
    """GND vias on a grid wherever nothing else is: they tie the F.Cu pour pieces between the tracks to B.Cu."""
    r = 0.3 + clr
    items = [t.GetEffectiveShape() for t in b.GetTracks()]
    items += [p.GetEffectiveShape() for fp in b.GetFootprints() for p in fp.Pads()]
    crt = [fp.GetCourtyard(pcbnew.F_CrtYd) for fp in b.GetFootprints()]
    n = 0
    y = Y0 + 1.5
    while y < Y1 - 1.0:
        x = X0 + 1.5
        while x < X1 - 1.0:
            q = P(x, y)
            ok = (all((x - hx) ** 2 + (y - hy) ** 2 > 3.0 ** 2 for hx, hy in HOLES)
                  and not (U1_HEAT[0] - 0.6 <= x <= U1_HEAT[1] + 0.6 and U1_HEAT[2] - 0.6 <= y <= U1_HEAT[3] + 0.6)
                  and not any(c.OutlineCount() and c.Contains(q) for c in crt)
                  and not any(s.Collide(q, mm(r)) for s in items))
            if ok:
                v = pcbnew.PCB_VIA(b); v.SetPosition(q); v.SetWidth(mm(0.6)); v.SetDrill(mm(0.3))
                v.SetNet(nets['GND']); b.Add(v); items.append(v.GetEffectiveShape()); n += 1
            x += pitch
        y += pitch
    print(f'stitching vias: {n}')


def tie_islands(b, r=0.35, step=0.2):
    """Put a GND via into each filled pour piece (either layer) that has none, where both layers' fill has room for
    it, preferring spots outside the courtyards. Returns the number of vias added."""
    fills = {z.GetLayer(): z.GetFilledPolysList(z.GetLayer()) for z in b.Zones()
             if not z.GetIsRuleArea() and z.GetNetname() == 'GND'}
    gvias = [v.GetPosition() for v in b.GetTracks() if v.GetClass() == 'PCB_VIA' and v.GetNetname() == 'GND']
    crt = [fp.GetCourtyard(pcbnew.F_CrtYd) for fp in b.GetFootprints()]
    ring = [(mm(r * math.cos(a)), mm(r * math.sin(a))) for a in [k * math.pi / 4 for k in range(8)]]

    def room(poly, q):
        return poly.Contains(q) and all(poly.Contains(pcbnew.VECTOR2I(q.x + dx, q.y + dy)) for dx, dy in ring)

    added = 0
    for lay, fill in fills.items():
        other = [f for l, f in fills.items() if l != lay][0]
        for i in range(fill.OutlineCount()):
            piece = pcbnew.SHAPE_POLY_SET(); piece.AddOutline(fill.Outline(i))
            for h in range(fill.HoleCount(i)):
                piece.AddHole(fill.Hole(i, h))
            if any(piece.Contains(g) for g in gvias):
                continue
            bb = fill.Outline(i).BBox()
            best = None
            y = bb.GetTop()
            while y <= bb.GetBottom() and best is None:
                x = bb.GetLeft()
                while x <= bb.GetRight():
                    q = pcbnew.VECTOR2I(x, y)
                    if room(piece, q) and room(other, q):
                        if not any(c.OutlineCount() and c.Contains(q) for c in crt):
                            best = q
                            break
                        best = best or q
                    x += mm(step)
                y += mm(step)
            if best is not None:
                v = pcbnew.PCB_VIA(b); v.SetPosition(best); v.SetWidth(mm(0.6)); v.SetDrill(mm(0.3))
                v.SetNet(b.FindNet('GND')); b.Add(v); gvias.append(best); added += 1
            else:
                print('no room for a via in the', pcbnew.LayerName(lay), 'piece at', xy(bb.Centre()))
    print(f'island vias: {added}')
    return added


os.chdir(HERE)
if 'dsn' in sys.argv[1:]:
    b.Save(f'{NAME}.kicad_pcb')
    b = pcbnew.LoadBoard(f'{NAME}.kicad_pcb')
    print('dsn', pcbnew.ExportSpecctraDSN(b, f'{NAME}.dsn'))
    # 5V / 3V3 routed 0.5 wide (the FP001S's 400 mA): a net class written into the DSN for freerouting
    d = open(f'{NAME}.dsn').read()
    i = d.index('    (class kicad_default'); j = d.index('(circuit', i)
    body = d[i:j]
    for n in ('5V', '3V3'):
        body = re.sub(rf'(?<=\s){n}(?=\s)', '', body)
    d = (d[:i] + '    (class PWR 5V 3V3\n      (circuit (use_via Via[0-1]_600:300_um))\n'
         '      (rule (width 500) (clearance 150))\n    )\n' + body + d[j:])
    open(f'{NAME}.dsn', 'w').write(d)
else:
    if os.path.exists(f'{NAME}.ses'):
        import_ses(b, nets, f'{NAME}.ses')
    stitch(b)
    b.Save(f'{NAME}.kicad_pcb')
    # GND pour on both layers, filled on a reloaded board; pieces with no way to GND are dropped
    b = pcbnew.LoadBoard(f'{NAME}.kicad_pcb')
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        z = pcbnew.ZONE(b); z.SetLayer(layer); z.SetNet(b.FindNet('GND'))
        ol = z.Outline(); ol.NewOutline()
        for x, y in ((X0 + 0.3, Y0 + 0.3), (X1 - 0.3, Y0 + 0.3), (X1 - 0.3, Y1 - 0.3), (X0 + 0.3, Y1 - 0.3)):
            ol.Append(mm(OX + x), mm(OY - y))
        z.SetLocalClearance(mm(0.25)); z.SetMinThickness(mm(0.25)); z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_NEVER)    # islands get a via first (below)
        b.Add(z)
    # U1's heat: a 3V3 area on both layers around its tab, over the GND pours, tied by vias beside the tab
    hx0, hx1, hy0, hy1 = U1_HEAT
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        z = pcbnew.ZONE(b); z.SetLayer(layer); z.SetNet(b.FindNet('3V3')); z.SetAssignedPriority(1)
        ol = z.Outline(); ol.NewOutline()
        for x, y in ((hx0, hy0), (hx1, hy0), (hx1, hy1), (hx0, hy1)):
            ol.Append(mm(OX + x), mm(OY - y))
        z.SetLocalClearance(mm(0.25)); z.SetMinThickness(mm(0.25)); z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        b.Add(z)
    for x, y in HEAT_VIAS:
        v = pcbnew.PCB_VIA(b); v.SetPosition(P(x, y)); v.SetWidth(mm(0.6)); v.SetDrill(mm(0.3))
        v.SetNet(b.FindNet('3V3')); b.Add(v)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    for _ in range(3):                                   # tie every pour piece left without a via to the other layer
        if not tie_islands(b):
            break
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    for z in b.Zones():                                  # then drop what is still floating
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    # a stitching via left in no pour on one layer does nothing
    fills = [z.GetFilledPolysList(z.GetLayer()) for z in b.Zones() if z.GetNetname() == 'GND']
    loose = [v for v in b.GetTracks() if v.GetClass() == 'PCB_VIA' and v.GetNetname() == 'GND'
             and not all(f.Contains(v.GetPosition()) for f in fills)
             and not any(t.GetClass() != 'PCB_VIA' and t.GetNetname() == 'GND' and t.HitTest(v.GetPosition())
                         for t in b.GetTracks())]
    for v in loose:
        b.Remove(v)
    print(f'removed {len(loose)} loose vias')
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    b.Save(f'{NAME}.kicad_pcb')
LIBS['MountingHole'] = FP + 'MountingHole.pretty'
with open('fp-lib-table', 'w') as f:
    f.write('(fp_lib_table\n  (version 7)\n')
    for nick, uri in sorted(LIBS.items()):
        f.write(f'  (lib (name "{nick}")(type "KiCad")(uri "{uri}")(options "")(descr ""))\n')
    f.write(')\n')
for fp in b.GetFootprints():
    cy = fp.GetCourtyard(pcbnew.F_CrtYd)
    bb = cy.BBox() if cy.OutlineCount() else fp.GetBoundingBox(False, False)
    print(f'{fp.GetReference():4s}', xy(fp.GetPosition()), 'crtyd x', round(pcbnew.ToMM(bb.GetLeft()) - OX, 2),
          round(pcbnew.ToMM(bb.GetRight()) - OX, 2), 'y', round(OY - pcbnew.ToMM(bb.GetBottom()), 2),
          round(OY - pcbnew.ToMM(bb.GetTop()), 2))
print('saved')
