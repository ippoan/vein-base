"""FP008 USB board (f1): the Grow FP008 face / palm vein module (Hangzhou Grow, user manual V1.01) on a PC through one
USB-C cable, with no MCU and no firmware: the PC sees the module's camera (UVC) and a COM port (its UART, commands),
both behind one hub. Keys stay on the PC (its TPM); the board holds none. Sound comes from the PC's own speakers (no
audio on the board). (2026-11-19, user decisions.)
  - J1  USB-C (to the PC): VBUS -> 5V, CC1 / CC2 5.1 k (R1 / R2), D+ / D- through U2 (USBLC6-2SC6) to U3's upstream.
  - U3  CH334F (QFN-24 4x4) USB 2.0 hub, self-powered from 5V (V5 -> internal LDO -> VDD33 = HUB33), Y1 12 MHz (load
        caps inside the CH334). Pins (WCH CH334/CH335 datasheet V2.4, table 1-3, column 4F): DMU 14 / DPU 15,
        DM1 11 / DP1 12 -> the FP008's USB (camera), DM2 9 / DP2 10 -> U4, ports 3 / 4 unused.
  - U4  CH340C (SOP-16, clock inside) at 3.3 V: TXD -> FP008 RXD, RXD <- FP008 TXD (115200 8N1), CTS# <- the FP008's
        IRQ (its infrared presence sensor; high = someone is there), read on the PC as the CTS modem line
        (Web Serial getSignals().clearToSend, inverted: CTS asserted = IRQ low).
  - U1  XC6206P332MR (SOT-23, 3.3 V LDO, 200 mA) 5V -> 3V3 for U4 and the FP008's sensor supply (pin 6, 60 uA).
  - J3  Molex PicoBlade 53261-0871 (MX1.25 8P, horizontal, opening +y) for the FP008 cable, the module's pins
        (manual 1.3.2): 1 VCC 4.5-15 V (5V), 2 GND, 3 TXD (module out), 4 RXD (module in), 5 IRQ, 6 sensor VCC (3V3),
        7 D+, 8 D-. CHECK THE CABLE BEFORE ORDERING (pin 1 on pin 1).
  - D1 + R5: 3V3 power LED. H1..H4: M2 holes in the corners (placeholders: the board is to sit behind the FP008 on the
        module's own screws once their spacing is measured).
  5V load: FP008 200 mA + hub / CH340 ~45 mA.
Board coords: origin = board centre, J1 (USB-C) on the -y edge at -x, J3 on the +y edge at -x, U4 at +x.
Routing comes from freerouting and is kept in fp008_board.ses (the board file itself is always generated):
    python3 build_board.py dsn   # placement only -> .dsn (freerouting 2.4.1 -> .ses)
    python3 build_board.py       # placement + tracks / vias from the .ses -> fp008_board.kicad_pcb
Run with KiCad's python from pcb/fp008_board/.
"""
import math, os, re, sys
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from kicad_ses import import_ses  # noqa: E402

REV = 'f1'
NAME = 'fp008_board'
FP = '/usr/share/kicad/footprints/'
OX, OY = 100.0, 100.0
mm = pcbnew.FromMM

X0, X1, Y0, Y1 = -22.0, 22.0, -14.0, 14.0          # 44 x 28
HOLES = [(sx * 19.5, sy * 11.5) for sx in (-1, 1) for sy in (-1, 1)]
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
for n in ['GND', '5V', '3V3', 'HUB33', 'CC1', 'CC2', 'UDP', 'UDN', 'XI', 'XO', 'FPDP', 'FPDM', 'SDP', 'SDN',
          'FPTX', 'FPRX', 'IRQ', 'LEDA']:
    ni = pcbnew.NETINFO_ITEM(b, n); b.Add(ni); nets[n] = ni

LIBS = {}
LOCAL = os.path.join(HERE, '..', 'vein_base.pretty')     # the repo's own footprints (nickname vein_base)


def load(lib, name, ref, value, x, y, rot=0):
    path = LOCAL if lib == 'vein_base.pretty' else FP + lib
    fp = pcbnew.FootprintLoad(path, name)
    nick = lib.removesuffix('.pretty')
    LIBS[nick] = '${KIPRJMOD}/../vein_base.pretty' if lib == 'vein_base.pretty' else FP + lib
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

# ======== J1 USB-C (the PC; power and data) -> U2 ESD -> U3 hub ========
J1 = load('Connector_USB.pretty', 'USB_C_Receptacle_HRO_TYPE-C-31-M-12', 'J1', 'USB-C (PC)', -10.0, Y0 + 3.05)
wire(J1, {**USB_GND, 'A5': 'CC1', 'B5': 'CC2', 'A4': '5V', 'A9': '5V', 'B4': '5V', 'B9': '5V',
          'A6': 'UDP', 'B6': 'UDP', 'A7': 'UDN', 'B7': 'UDN'})
R('R1', '5.1k', 'CC1', 'GND', -15.5, -3.2, 90)
R('R2', '5.1k', 'CC2', 'GND', -4.5, -3.2, 90)
U2 = load('Package_TO_SOT_SMD.pretty', 'SOT-23-6', 'U2', 'USBLC6-2SC6', -10.0, -3.4, 90)
wire(U2, {'1': 'UDP', '6': 'UDP', '3': 'UDN', '4': 'UDN', '2': 'GND', '5': '5V'})
C('C5', '10uF', '5V', 'GND', -1.5, -9.0, 90)              # VBUS bulk at J1

U3 = load('Package_DFN_QFN.pretty', 'QFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm', 'U3', 'CH334F', -8.0, 4.0, 180)
wire(U3, {'25': 'GND', '3': 'XO', '4': 'XI', '9': 'SDN', '10': 'SDP', '11': 'FPDM', '12': 'FPDP',
          '14': 'UDN', '15': 'UDP', '19': '5V', '20': 'HUB33'})
XT = load('Crystal.pretty', 'Crystal_SMD_3225-4Pin_3.2x2.5mm', 'Y1', '12MHz', -3.5, 4.0, 270)
wire(XT, {'1': 'XI', '3': 'XO', '2': 'GND', '4': 'GND'})
C('C1', '1uF', '5V', 'GND', -10.0, 0.5, 0)                # V5 (pins 19 / 20 face -y)
C('C2', '10uF', 'HUB33', 'GND', -6.5, 0.3, 0)            # VDD33
C('C3', '100nF', 'HUB33', 'GND', -2.6, 0.4, 90)

# ======== U4 CH340C (USB-UART) on hub port 2, U1 3.3 V LDO ========
U4 = load('Package_SO.pretty', 'SOIC-16_3.9x9.9mm_P1.27mm', 'U4', 'CH340C', 9.5, 5.0, 90)
wire(U4, {'1': 'GND', '2': 'FPRX', '3': 'FPTX', '4': '3V3', '5': 'SDP', '6': 'SDN', '9': 'IRQ', '16': '3V3'})
C('C4', '100nF', '3V3', 'GND', 9.5, 10.2, 0)
U1 = load('Package_TO_SOT_SMD.pretty', 'SOT-23', 'U1', 'XC6206P332MR', 9.0, -5.0, 0)
wire(U1, {'1': 'GND', '2': '3V3', '3': '5V'})                              # 1 VSS, 2 VOUT, 3 VIN
C('C6', '1uF', '5V', 'GND', 6.0, -5.0, 90)
C('C7', '1uF', '3V3', 'GND', 12.0, -5.0, 90)
two('LED_SMD.pretty', 'LED_0603_1608Metric', 'D1', 'PWR (3V3)', 'GND', 'LEDA', 14.0, -10.0, 0)   # 1 = K, 2 = A
R('R5', '1k', '3V3', 'LEDA', 10.8, -10.0, 0)

# ======== J3 FP008 (PicoBlade 8P, opening +y) ========
J3 = load('Connector_Molex.pretty', 'Molex_PicoBlade_53261-0871_1x08-1MP_P1.25mm_Horizontal', 'J3', 'FP008 (MX1.25 8P)',
          -8.0, Y1 - 3.0, 180)
FP_PINS = ['5V', 'GND', 'FPTX', 'FPRX', 'IRQ', '3V3', 'FPDP', 'FPDM']    # the module's pins 1..8
wire(J3, {**{str(i + 1): n for i, n in enumerate(FP_PINS)}, 'MP': 'GND'})
C('C8', '10uF', '5V', 'GND', 2.0, 11.0, 90)               # at J3: the module's 200 mA
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
SILK = [('USB-C (PC)', 4.5, -12.6, 0.8), ('J3 FP008 MX1.25 8P', 4.0, -7.6, 0.7),
        ('1:5V 2:G 3:TX 4:RX', 4.0, -8.7, 0.7), ('5:IRQ 6:3V3 7:D+ 8:D-', 4.0, -9.8, 0.7)]
for t, x, y, sz in SILK:
    assert X0 + 0.3 <= x - len(t) * 0.4 * sz and x + len(t) * 0.4 * sz <= X1 - 0.3, t
    text(t, x, y, size=sz)
VERSION = open(os.path.join(HERE, '..', '..', 'VERSION')).read().strip()
text(f'FP008 USB {REV} v{VERSION}', 0, 0, layer=pcbnew.B_SilkS)
text('CHECK THE CABLE: PIN 1 = 5V', 0, -2.0, layer=pcbnew.B_SilkS, size=0.8)


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
    holes = [P(hx, hy) for hx, hy in HOLES]

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
                    if room(piece, q) and room(other, q) and all((q - h).EuclideanNorm() > mm(2.0) for h in holes):
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
    # 5V / 3V3 routed 0.5 wide (the FP008's 200 mA): a net class written into the DSN for freerouting
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
