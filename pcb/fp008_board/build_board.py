"""FP008 USB board (f1): the Grow FP008 face / palm vein module (Hangzhou Grow, user manual V1.01) on a PC through one
USB-C cable, with no MCU and no firmware: the PC sees the module's camera (UVC) and a COM port (its UART, commands),
both behind one hub. Keys stay on the PC (its TPM); the board holds none. Sound comes from the PC's own speakers (no
audio on the board). (2026-11-19, user decisions.)
  - J1  USB-C (to the PC): VBUS -> 5V, CC1 / CC2 5.1 k (R1 / R2), D+ / D- through U2 (USBLC6-2SC6) to U3's upstream.
  - U3  CH334F (QFN-24 4x4) USB 2.0 hub, self-powered from 5V (V5 -> internal LDO -> VDD33 = HUB33), Y1 12 MHz (load
        caps inside the CH334). Pins (WCH CH334/CH335 datasheet V2.4, table 1-3, column 4F): DMU 14 / DPU 15,
        DM1 11 / DP1 12 -> the FP008's USB (camera), DM2 9 / DP2 10 -> U4, DM3 7 / DP3 8 -> J2, port 4 unused.
  - J2  USB-C receptacle (a device, e.g. a USB speaker; beside J1 on the tongue, f4) on hub port 3: VBUS = 5V straight (no switch,
        no fuse), CC1 / CC2 56 k to 5V (R3 / R4, Rp: default USB power), D+ / D- through U5 (USBLC6-2SC6).
        The PC port feeds everything: on a 500 mA USB 2.0 port leave the device ~250 mA.
  - U4  CH340C (SOP-16, clock inside) at 3.3 V: TXD -> FP008 RXD, RXD <- FP008 TXD (115200 8N1), CTS# <- the FP008's
        IRQ (its infrared presence sensor; high = someone is there), read on the PC as the CTS modem line
        (Web Serial getSignals().clearToSend, inverted: CTS asserted = IRQ low).
  - U1  XC6206P332MR (SOT-23, 3.3 V LDO, 200 mA) 5V -> 3V3 for U4 and the FP008's sensor supply (pin 6, 60 uA).
  - J3  Molex PicoBlade 53261-0871 (MX1.25 8P, horizontal, opening +y) for the FP008 cable, the module's pins
        (manual 1.3.2): 1 VCC 4.5-15 V (5V), 2 GND, 3 TXD (module out), 4 RXD (module in), 5 IRQ, 6 sensor VCC (3V3),
        7 D+, 8 D-. CHECK THE CABLE BEFORE ORDERING (pin 1 on pin 1).
  - D1 + R5: 3V3 power LED.
  f3 (2026-11-19, user): the board is the FP008's back lid. Its outline is the module's rear body (manual 1.3.1:
  55.45 x 34.45, drawn as a rounded rectangle, corners R12 -- the real corner shape is to be checked), screwed to the
  module's four rear screw holes H1..H4 at (+-18.35, +-11.95) (read off the manual's rear drawing, ~36.7 x 23.9 apart;
  measure before ordering).
  f5 (2026-11-20, user): the L adapters sit in notches in the tongue (NW x ND from the receptacles' faces, open on
  -x), inside the outline; J1 / J2 15.4 apart for the rib between the notches.
  f4 (2026-11-20, user): the parts face the module (F = inside; one side, so still JLC Economic), only the cables come
  out. The outline gets a tongue on -x (to XT, |y| <= TY) past the module's rear body; J1 / J2 sit side by side under
  it (13.5 apart for two plugs), openings -x, wholly outside the body (asserted), and the cables take an L-shaped
  (90 deg) adapter at the plug. The parts keep KEEP clear of the screw bosses (asserted); J3 sits inside at the top
  centre and its cable goes straight to the module's own 8P socket (no slot). The module's rear recess has to take the
  parts (up to 3.3): measure it before ordering.
  5V load: FP008 200 mA + hub / CH340 ~45 mA + whatever is on J2.
Board coords (KiCad's, seen from the F side = from inside the module, so mirrored from behind): origin = the FP008's
centre, its UP up, J1 (USB-C, PC, -y) and J2 (USB-C, device, +y) on the -x tongue, J3 at the top centre, U4 at +x.
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

REV = 'f5'
NAME = 'fp008_board'
FP = '/usr/share/kicad/footprints/'
OX, OY = 100.0, 100.0
mm = pcbnew.FromMM

X0, X1, Y0, Y1 = -27.5, 27.5, -17.0, 17.0          # the FP008's rear body 55.45 x 34.45, a hair inside
RC = 12.0                                           # corner radius (guess from the drawing)
HOLES = [(sx * 18.35, sy * 11.95) for sx in (-1, 1) for sy in (-1, 1)]   # the module's rear screw holes (manual 1.3.1)
XT = -37.0                                          # J1 / J2's openings (the board edge under them) past the body's -x end
# f5 (2026-11-20, user): the L adapters (USB-C plug -> female turned 90 deg, ~AD_W x AD_D across, the female end up)
# sit in notches in the tongue, inside the outline: one notch per USB-C from XT out to the tongue's end XE, rails
# RAIL wide on the outside and a rib RIB wide between the two (adapter sizes from a product photo; check the real one)
AD_W, AD_D = 12.4, 7.5                              # adapter across (y) and deep (x, from the receptacle's face)
NW, ND = AD_W + 1.0, AD_D + 1.0 + 0.3               # notch width, depth from XT (the receptacle's face is 0.3 past XT)
RIB, RAIL = 2.0, 2.5
JY = (NW + RIB) / 2                                 # J1 at -JY, J2 at +JY
XE = XT - ND                                        # the tongue's end
TY = JY + NW / 2 + RAIL                             # the tongue's half height (|y| <= TY)
assert TY < Y1, 'tongue taller than the board'
KEEP = 3.5                                          # clear of each screw boss (parts face the module, f4)


def outline(n=10):
    """The rear body's rounded rectangle with the tongue on -x, as a closed list of points (anticlockwise)."""
    a = math.degrees(math.asin((TY - (Y1 - RC)) / RC))    # where |y| = TY meets the -x corner arcs
    pts = []
    for cx, cy, a0, a1 in ((X1 - RC, Y0 + RC, -90, 0), (X1 - RC, Y1 - RC, 0, 90), (X0 + RC, Y1 - RC, 90, 180 - a),
                           (X0 + RC, Y0 + RC, 180 + a, 270)):
        for k in range(n + 1):
            t = math.radians(a0 + (a1 - a0) * k / n)
            pts.append((cx + RC * math.cos(t), cy + RC * math.sin(t)))
        if a0 == 90:
            pts.append((XE, TY))
            for jy in (JY, -JY):                    # the notches, open on -x
                pts += [(XE, jy + NW / 2), (XT, jy + NW / 2), (XT, jy - NW / 2), (XE, jy - NW / 2)]
            pts.append((XE, -TY))
    return pts


OUTLINE = outline()


def inside(x, y, m=0.0):
    """(x, y) inside the outline and at least m from its edges."""
    pts = OUTLINE
    c = False
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            c = not c
        dx, dy = x1 - x0, y1 - y0
        t = max(0.0, min(1.0, ((x - x0) * dx + (y - y0) * dy) / (dx * dx + dy * dy)))
        if math.hypot(x - x0 - t * dx, y - y0 - t * dy) < m:
            return False
    return c


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
          'FPTX', 'FPRX', 'IRQ', 'LEDA', 'DCC1', 'DCC2', 'D3P', 'D3N', 'J2P', 'J2N']:
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
J1 = load('Connector_USB.pretty', 'USB_C_Receptacle_HRO_TYPE-C-31-M-12', 'J1', 'USB-C (PC)', XT + 3.05, -JY, 270)
wire(J1, {**USB_GND, 'A5': 'CC1', 'B5': 'CC2', 'A4': '5V', 'A9': '5V', 'B4': '5V', 'B9': '5V',
          'A6': 'UDP', 'B6': 'UDP', 'A7': 'UDN', 'B7': 'UDN'})
R('R1', '5.1k', 'CC1', 'GND', -23.5, -7.0, 0)
R('R2', '5.1k', 'CC2', 'GND', -23.5, -8.6, 0)
U2 = load('Package_TO_SOT_SMD.pretty', 'SOT-23-6', 'U2', 'USBLC6-2SC6', -23.5, -4.0, 0)
wire(U2, {'1': 'UDP', '6': 'UDP', '3': 'UDN', '4': 'UDN', '2': 'GND', '5': '5V'})
C('C5', '10uF', '5V', 'GND', -19.6, -6.0, 0)              # VBUS bulk at J1

U3 = load('Package_DFN_QFN.pretty', 'QFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm', 'U3', 'CH334F', -14.0, 0.0, 180)
wire(U3, {'25': 'GND', '3': 'XO', '4': 'XI', '9': 'SDN', '10': 'SDP', '11': 'FPDM', '12': 'FPDP',
          '7': 'D3N', '8': 'D3P', '14': 'UDN', '15': 'UDP', '19': '5V', '20': 'HUB33'})
XTAL = load('Crystal.pretty', 'Crystal_SMD_3225-4Pin_3.2x2.5mm', 'Y1', '12MHz', -8.5, 2.0, 270)
wire(XTAL, {'1': 'XI', '3': 'XO', '2': 'GND', '4': 'GND'})
C('C1', '1uF', '5V', 'GND', -16.2, -4.0, 0)                # V5 (pins 19 / 20 face -y)
C('C2', '10uF', 'HUB33', 'GND', -12.0, -4.2, 0)            # VDD33
C('C3', '100nF', 'HUB33', 'GND', -9.0, -3.0, 90)

# ======== U4 CH340C (USB-UART) on hub port 2, U1 3.3 V LDO ========
U4 = load('Package_SO.pretty', 'SOIC-16_3.9x9.9mm_P1.27mm', 'U4', 'CH340C', 8.0, 1.5, 90)
wire(U4, {'1': 'GND', '2': 'FPRX', '3': 'FPTX', '4': '3V3', '5': 'SDP', '6': 'SDN', '9': 'IRQ', '16': '3V3'})
C('C4', '100nF', '3V3', 'GND', 14.0, 3.5, 90)
U1 = load('Package_TO_SOT_SMD.pretty', 'SOT-23', 'U1', 'XC6206P332MR', 18.5, -1.0, 0)
wire(U1, {'1': 'GND', '2': '3V3', '3': '5V'})                              # 1 VSS, 2 VOUT, 3 VIN
C('C6', '1uF', '5V', 'GND', 15.6, -1.5, 90)
C('C7', '1uF', '3V3', 'GND', 21.5, -1.0, 90)
two('LED_SMD.pretty', 'LED_0603_1608Metric', 'D1', 'PWR (3V3)', 'GND', 'LEDA', 21.0, 5.5, 0)   # 1 = K, 2 = A
R('R5', '1k', '3V3', 'LEDA', 17.5, 5.5, 0)

# ======== J2 USB-C (a device on hub port 3; opening -y beside J1) ========
J2 = load('Connector_USB.pretty', 'USB_C_Receptacle_HRO_TYPE-C-31-M-12', 'J2', 'USB-C (device)', XT + 3.05, JY, 270)
wire(J2, {**USB_GND, 'A5': 'DCC1', 'B5': 'DCC2', 'A4': '5V', 'A9': '5V', 'B4': '5V', 'B9': '5V',
          'A6': 'J2P', 'B6': 'J2P', 'A7': 'J2N', 'B7': 'J2N'})
assert J2.GetOrientationDegrees() == J1.GetOrientationDegrees(), 'J1 / J2 not on the same edge'
R('R3', '56k', '5V', 'DCC1', -23.5, 7.0, 0)
R('R4', '56k', '5V', 'DCC2', -23.5, 8.6, 0)
U5 = load('Package_TO_SOT_SMD.pretty', 'SOT-23-6', 'U5', 'USBLC6-2SC6', -23.5, 4.0, 0)
wire(U5, {'1': 'D3P', '6': 'J2P', '3': 'D3N', '4': 'J2N', '2': 'GND', '5': '5V'})
C('C9', '10uF', '5V', 'GND', -19.6, 6.0, 0)                # VBUS at J2

# ======== J3 FP008 (PicoBlade 8P, opening +y) ========
J3 = load('Connector_Molex.pretty', 'Molex_PicoBlade_53261-0871_1x08-1MP_P1.25mm_Horizontal', 'J3', 'FP008 (MX1.25 8P)',
          0.0, 9.0, 180)
FP_PINS = ['5V', 'GND', 'FPTX', 'FPRX', 'IRQ', '3V3', 'FPDP', 'FPDM']    # the module's pins 1..8
wire(J3, {**{str(i + 1): n for i, n in enumerate(FP_PINS)}, 'MP': 'GND'})
C('C8', '10uF', '5V', 'GND', 11.5, 9.5, 90)               # at J3: the module's 200 mA
sig = [xy(p.GetPosition())[1] for p in J3.Pads() if p.GetNumber() != 'MP']
mp = [xy(p.GetPosition())[1] for p in J3.Pads() if p.GetNumber() == 'MP']
assert max(sig) < min(mp), 'J3 opening is not +y'

for i, (x, y) in enumerate(HOLES, 1):
    assert inside(x, y, 2.4), ('hole too near the edge', x, y)
    load('MountingHole.pretty', 'MountingHole_2.2mm_M2', f'H{i}', 'M2', x, y)

# ---- outline
def edge_loop(pts):
    for (a, c), (d, e) in zip(pts, pts[1:] + pts[:1]):
        sh = pcbnew.PCB_SHAPE(b); sh.SetShape(pcbnew.SHAPE_T_SEGMENT)
        sh.SetStart(P(a, c)); sh.SetEnd(P(d, e)); sh.SetLayer(pcbnew.Edge_Cuts); sh.SetWidth(mm(0.1)); b.Add(sh)


edge_loop(OUTLINE)
BODY_X = -55.45 / 2                                 # the module's rear body ends here on -x: J1 / J2 wholly past it
for fp in b.GetFootprints():                        # every part inside the outline (courtyard corners)
    cy_ = fp.GetCourtyard(pcbnew.F_CrtYd)
    if cy_.OutlineCount() and not fp.GetReference().startswith(('J1', 'J2', 'H')):
        bb_ = cy_.BBox()
        for q in (bb_.GetOrigin(), bb_.GetEnd()):
            for qx in (bb_.GetLeft(), bb_.GetRight()):
                for qy in (bb_.GetTop(), bb_.GetBottom()):
                    x_, y_ = xy(pcbnew.VECTOR2I(qx, qy))
                    assert inside(x_, y_, 0.2), (fp.GetReference(), x_, y_)
        L, Rr = pcbnew.ToMM(bb_.GetLeft()) - OX, pcbnew.ToMM(bb_.GetRight()) - OX
        T_, B_ = OY - pcbnew.ToMM(bb_.GetBottom()), OY - pcbnew.ToMM(bb_.GetTop())
        for hx, hy in HOLES:                        # clear of the screw bosses (the parts face the module)
            dx = max(L - hx, 0, hx - Rr); dy = max(T_ - hy, 0, hy - B_)
            assert math.hypot(dx, dy) >= KEEP, (fp.GetReference(), 'on the boss at', hx, hy)
for j in (J1, J2):                                  # the USB-C wholly outside the module's body, opening -x
    bb_ = j.GetCourtyard(pcbnew.F_CrtYd).BBox()
    assert pcbnew.ToMM(bb_.GetRight()) - OX < BODY_X - 0.3, (j.GetReference(), 'reaches into the module body')
    assert pcbnew.ToMM(bb_.GetLeft()) - OX < XT, (j.GetReference(), 'opening not at the -x edge')


def text(s, x, y, layer=pcbnew.F_SilkS, size=1.0, rot=0):
    t = pcbnew.PCB_TEXT(b); t.SetText(s); t.SetPosition(P(x, y)); t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size))); t.SetTextThickness(mm(0.15)); t.SetTextAngleDegrees(rot)
    if layer == pcbnew.B_SilkS:
        t.SetMirrored(True)
    b.Add(t)


# silk: 1 character ~ 0.8 x size wide, centred: keep both ends inside the outline
# the outside is B (the parts face the module, f4): labels on B.SilkS, beside each USB-C on the board's inner side
SILK = [('PC', -21.0, -JY, 1.0), ('DEVICE', -19.5, JY, 1.0)]
for t, x, y, sz in SILK:
    assert inside(x - len(t) * 0.4 * sz, y, 0.3) and inside(x + len(t) * 0.4 * sz, y, 0.3), t
    text(t, x, y, layer=pcbnew.B_SilkS, size=sz)
VERSION = open(os.path.join(HERE, '..', '..', 'VERSION')).read().strip()
text(f'FP008 USB {REV} v{VERSION}', 0, 2.0, layer=pcbnew.B_SilkS)
text('CHECK THE CABLE: PIN 1 = 5V', 0, 0.0, layer=pcbnew.B_SilkS, size=0.8)
text('J3 1:5V 2:G 3:TX 4:RX 5:IRQ 6:3V3 7:D+ 8:D-', 0, -1.6, layer=pcbnew.B_SilkS, size=0.7)


def stitch(b, pitch=2.5, clr=0.25):
    """GND vias on a grid wherever nothing else is: they tie the F.Cu pour pieces between the tracks to B.Cu."""
    r = 0.3 + clr
    items = [t.GetEffectiveShape() for t in b.GetTracks()]
    items += [p.GetEffectiveShape() for fp in b.GetFootprints() for p in fp.Pads()]
    crt = [fp.GetCourtyard(pcbnew.F_CrtYd) for fp in b.GetFootprints()]
    n = 0
    y = Y0 + 1.5
    while y < Y1 - 1.0:
        x = XE + 1.5
        while x < X1 - 1.0:
            q = P(x, y)
            ok = (inside(x, y, 1.0) and all((x - hx) ** 2 + (y - hy) ** 2 > 3.0 ** 2 for hx, hy in HOLES)
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
        for x, y in OUTLINE:
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
