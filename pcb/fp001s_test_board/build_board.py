"""FP001S USB board (t3): the Grow FP001S face / palm vein module (Hangzhou Grow, user manual V1.01) on a PC through
one USB-C cable, like a USB camera: the PC sees the module's camera (UVC) and the RP2354A (a USB CDC device that talks
to the module's UART and holds the keys), and the board takes its power from the same cable. 54 x 34.
  - J1  USB-C (to the PC): VBUS -> 5V, CC1 / CC2 5.1 k (R1 / R2, so a USB-C port or charger turns VBUS on),
        D+ / D- through U2 (USBLC6-2SC6, clamp reference on 5V) to U3's upstream port.
  - U3  CH334F (QFN-24 4x4) USB 2.0 hub, self-powered from 5V (V5 -> internal LDO -> VDD33 = HUB33), Y1 12 MHz
        (load caps inside the CH334). Port 1 -> the FP001S's USB (UVC / MJPEG up to 960x480 15 fps),
        port 2 -> U6. Ports 3 / 4 unused. RESET# / PSELF (self-powered) / LED / OVCUR# / PWREN# left open.
  - U6  RP2354A (QFN-60 7x7, RP2350 with 2 MB flash inside, no radio: no Giteki question, Economic PCBA): USB device
        on the hub's port 2 (R107 / R108 27 R), UART0 GPIO0 TX -> the module's RXD, GPIO1 RX <- its TXD (115200 8N1,
        plain: the UART is not encrypted, the user's choice 2026-11-18). Its core (regulator: L106 3.3 uH Abracon
        AOTA-B201610S3R3-101-T, the right way round, C106 / C107 / C109 4.7 uF, R103 33 R; crystal Y106 ABM8-272-T3
        with C103 / C104 15 pF and R102 1 k; the 100 nF decoupling) is Raspberry Pi's "RP2350A Minimal" design
        (MIT, rp2350_core_LICENSE.txt) as they laid it out, footprints, tracks, vias and zones (rp_core_extract.py ->
        rp2350_core.json; "Hardware design with RP2350" 2.1: use this layout, at your own risk otherwise). Their
        0.25 drills are opened to 0.3 (JLC's standard). The firmware (ours) takes signed images over USB CDC, checks
        them before writing and falls back to the old one if the new does not start; Secure Boot keys in OTP.
        BOOTSEL (TP1: QSPI_SS through R110 1 k, short to TP2 GND at power-up for the ROM's USB boot), RUN (TP3, R111
        10 k pull-up), SWD (TP4 SWDIO / TP5 SWCLK) are test pads, for the factory only.
  - U5  SY8089AAAC (SOT-23-5, 2 A, 1 MHz buck): 5V -> 3V3 for the FP001S, U6 and the rest, L2 2.2 uH (SWPA4020S), FB
        R6 100 k / R7 22 k (0.6 V x (1 + 100 / 22) = 3.33 V), EN tied to VIN. A buck, not an LDO (t1's AMS1117): the
        FP001S's 3.3 V 400 mA then takes ~290 mA from VBUS (90 %), not 400, so the whole board (+ hub ~30 mA,
        RP2354A ~30 mA) stays inside a USB 2.0 port's 500 mA, and it keeps 3.3 V when VBUS sags to 4.4 V (an
        AMS1117 drops out there: on the bench, 2026-11-18, the FP001S rebooted on a PC port behind an AMS1117
        as soon as it saw a face). C5 10 uF on 5V is the only bulk on VBUS (with C1 1 uF: 11 uF, USB's 10 uF
        inrush limit in spirit); C6 / C8 22 uF + C9 220 uF tantalum on 3V3 take the module's current peaks.
  - J3  JST SH 1.0 6P (SM06B-SRSS-TB, horizontal, opening +y) for the FP001S cable: pins as the module's
        (manual 1.3.2): 1 VCC (3V3), 2 TXD (module out), 3 RXD (module in), 4 GND, 5 D-, 6 D+. The module's own
        cable (SH on the module end, loose wires: red 1, black 2, yellow 3, green 4 = GND, blue 5, white 6; found
        2026-11-18) does not fit: use an SH 1.0 6P cable with both ends (1 -> 1).
        SH_REVERSED: if the cable is crossed (its pin 1 on the other end's pin 6, as Pimoroni / Adafruit SH
        cables are), set it True so the board's pin 6 takes VCC. CHECK THE CABLE BEFORE ORDERING: swapped, the
        module gets 3.3 V on GND.
  - D1 + R5: 3V3 power LED. H1..H4: M2 holes in the corners.
  The module's lens must stand upright (the round lens above the square window, manual 1.1): upside down it sees
  no face at all (2026-11-18).
Board coords: origin = board centre. J1 (USB-C) on the -y edge at -x with the hub above it, U6 (RP2354A) in the middle
(RP), the buck at +x, J3 on the +y edge at -x, the test pads on the -y edge at +x.
Routing comes from freerouting and is kept in fp001s_test_board.ses (the board file itself is always generated):
    python3 build_board.py dsn   # placement only -> .dsn (freerouting 2.4.1 -> .ses)
    python3 build_board.py       # placement + tracks / vias from the .ses -> fp001s_test_board.kicad_pcb
Run with KiCad's python from pcb/fp001s_test_board/.
"""
import json, math, os, re, sys
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from kicad_ses import import_ses  # noqa: E402

REV = 't3'
NAME = 'fp001s_test_board'
SH_REVERSED = False            # see the docstring: True if the module's SH cable crosses 1 <-> 6
FP = '/usr/share/kicad/footprints/'
OX, OY = 100.0, 100.0
mm = pcbnew.FromMM

X0, X1, Y0, Y1 = -27.0, 27.0, -17.0, 17.0          # 54 x 34 (t3: room for the RP2354A's core; t2 was 42 x 32)
HOLES = [(sx * 24.5, sy * 14.5) for sx in (-1, 1) for sy in (-1, 1)]
RP = (2.0, 3.0)                                     # U6's (the RP2354A's) origin: the minimal design's core around it
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
nc.SetClearance(mm(0.12)); nc.SetTrackWidth(mm(0.2))   # 0.2 / 0.12: the CH334F's 0.5 pitch, the minimal design's core (0.127)
nc.SetViaDiameter(mm(0.6)); nc.SetViaDrill(mm(0.3))

nets = {}
for n in ['GND', '5V', '3V3', 'HUB33', 'CC1', 'CC2', 'UDP', 'UDN', 'XI', 'XO', 'LX', 'FB',
          'FPDP', 'FPDM', 'SDP', 'SDN', 'FPTX', 'FPRX', 'LEDA',
          '1V1', 'VAVDD', 'VLX', 'RXI', 'RXO', 'RXO2', 'RDP', 'RDM', 'RUN', 'SWDIO', 'SWCLK', 'QSS', 'BOOT']:
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
J1 = load('Connector_USB.pretty', 'USB_C_Receptacle_HRO_TYPE-C-31-M-12', 'J1', 'USB-C (PC)', -16.5, Y0 + 3.05)
wire(J1, {**USB_GND, 'A5': 'CC1', 'B5': 'CC2', 'A4': '5V', 'A9': '5V', 'B4': '5V', 'B9': '5V',
          'A6': 'UDP', 'B6': 'UDP', 'A7': 'UDN', 'B7': 'UDN'})
R('R1', '5.1k', 'CC1', 'GND', -22.5, -6.2, 90)
R('R2', '5.1k', 'CC2', 'GND', -11.5, -6.2, 90)
U2 = load('Package_TO_SOT_SMD.pretty', 'SOT-23-6', 'U2', 'USBLC6-2SC6', -17.0, -6.4, 90)
wire(U2, {'1': 'UDP', '6': 'UDP', '3': 'UDN', '4': 'UDN', '2': 'GND', '5': '5V'})

U3 = load('Package_DFN_QFN.pretty', 'QFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm', 'U3', 'CH334F', -15.0, 0.0, 180)   # upstream (14 / 15) to -x over U2, ports 1 / 2 to +y, XI / XO to +x
wire(U3, {'25': 'GND', '3': 'XO', '4': 'XI', '9': 'SDN', '10': 'SDP', '11': 'FPDM', '12': 'FPDP',
          '14': 'UDN', '15': 'UDP', '19': '5V', '20': 'HUB33'})
XT = load('Crystal.pretty', 'Crystal_SMD_3225-4Pin_3.2x2.5mm', 'Y1', '12MHz', -10.5, 0.0, 270)
wire(XT, {'1': 'XI', '3': 'XO', '2': 'GND', '4': 'GND'})
C('C1', '1uF', '5V', 'GND', -17.0, -3.5, 0)               # V5 (pins 19 / 20 face -y)
C('C2', '10uF', 'HUB33', 'GND', -13.5, -3.7, 0)         # VDD33
C('C3', '100nF', 'HUB33', 'GND', -9.6, -3.6, 90)

# ======== U6 RP2354A (USB device on hub port 2; UART0 to the FP001S) ========
# The chip with its core regulator (L1 -> L106 here, the inductor the right way round), crystal, decoupling and USB
# series resistors is the minimal design's (rp2350_core.json from rp_core_extract.py, MIT, see
# rp2350_core_LICENSE.txt): footprints, tracks, vias and zones as Raspberry Pi laid them out, moved to RP, refs
# renumbered (U1 -> U6, L1 -> L106, X1 -> Y106, Cn / Rn -> C1nn / R1nn).
CORE = json.load(open(os.path.join(HERE, 'rp2350_core.json')))
CORE_NET = {'+3V3': '3V3', 'GND': 'GND', '+1V1': '1V1', '/VREG_AVDD': 'VAVDD', '/VREG_LX': 'VLX', '/XIN': 'RXI',
            '/XOUT': 'RXO', 'Net-(C4-Pad1)': 'RXO2', 'Net-(U1-USB_DP)': 'RDP', 'Net-(U1-USB_DM)': 'RDM',
            '/USB_D+': 'SDP', '/USB_D-': 'SDN',                  # R7 / R8's outer pads: the hub's port 2
            '/GPIO0': 'FPRX', '/GPIO1': 'FPTX',                  # UART0 TX -> the module's RXD, RX <- its TXD
            '/RUN': 'RUN', '/SWD': 'SWDIO', '/SWCLK': 'SWCLK', '/QSPI_SS': 'QSS'}
CORE_REF = lambda r: {'U1': 'U6', 'L1': 'L106', 'X1': 'Y106'}.get(r, r[0] + str(100 + int(r[1:])))


def cxy(dx, dy):
    """The core's coordinates (mm from U1, KiCad's y down) to ours."""
    return P(RP[0] + dx, RP[1] - dy)


SHAPE = {'rect': pcbnew.PAD_SHAPE_RECT, 'circle': pcbnew.PAD_SHAPE_CIRCLE, 'oval': pcbnew.PAD_SHAPE_OVAL}
for f in CORE['footprints']:
    fp = pcbnew.FOOTPRINT(b)
    ref = CORE_REF(f['ref'])
    fp.SetFPID(pcbnew.LIB_ID('rpi_minimal', f['fp'])); fp.SetReference(ref); fp.SetValue(f['value'])
    fp.Reference().SetVisible(False); fp.Value().SetLayer(pcbnew.F_Fab)
    b.Add(fp)
    for q in f['pads']:
        pd = pcbnew.PAD(fp)
        pd.SetNumber(q['num']); pd.SetShape(SHAPE[q['shape']])
        pd.SetSize(pcbnew.VECTOR2I(mm(q['w']), mm(q['h'])))
        if q['type'] == 'thru_hole':
            dr = max(q['drill'], 0.3)                    # the EP's vias 0.25 -> 0.3 (JLC's standard drill)
            pd.SetAttribute(pcbnew.PAD_ATTRIB_PTH); pd.SetDrillSize(pcbnew.VECTOR2I(mm(dr), mm(dr)))
            pd.SetLayerSet(pcbnew.PAD.PTHMask())
        else:
            pd.SetAttribute(pcbnew.PAD_ATTRIB_SMD); pd.SetLayerSet(pcbnew.PAD.SMDMask())
            if 'F.Paste' not in q['layers']:
                ls = pd.GetLayerSet(); ls.RemoveLayer(pcbnew.F_Paste); pd.SetLayerSet(ls)
        loc = pcbnew.VECTOR2I(mm(q['x']), mm(q['y']))       # the footprint is still at the origin, unturned
        pd.SetPos0(loc); pd.SetPosition(loc)
        pd.SetOrientation(pcbnew.EDA_ANGLE(q['rot'] - f['rot'], pcbnew.DEGREES_T))
        n = CORE_NET.get(q['net'])
        if n:
            pd.SetNet(nets[n])
        fp.Add(pd)
    for kind, x0, y0, x1, y1 in f['courtyard']:
        g = pcbnew.FP_SHAPE(fp); g.SetShape(pcbnew.SHAPE_T_RECT if kind == 'fp_rect' else pcbnew.SHAPE_T_SEGMENT)
        g.SetStart0(pcbnew.VECTOR2I(mm(x0), mm(y0))); g.SetEnd0(pcbnew.VECTOR2I(mm(x1), mm(y1)))
        g.SetLayer(pcbnew.F_CrtYd); g.SetWidth(mm(0.05)); g.SetDrawCoord(); fp.Add(g)
    fp.SetPosition(cxy(f['x'], f['y']))
    fp.SetOrientationDegrees(f['rot'])
U6 = next(fp for fp in b.GetFootprints() if fp.GetReference() == 'U6')
U6.SetValue('RP2354A')
# BOOTSEL / RUN / SWD on test pads (the factory's only): BOOT = QSPI_SS through R110 1 k (the minimal design's R6),
# pulled to GND at power-up for USB boot; RUN pulled up by R111 10 k
R('R110', '1k', 'QSS', 'BOOT', -4.0, 9.5, 0)
R('R111', '10k', '3V3', 'RUN', 7.5, -7.0, 0)
TP = [('TP1', 'BOOT'), ('TP2', 'GND'), ('TP3', 'RUN'), ('TP4', 'SWDIO'), ('TP5', 'SWCLK')]
for i, (ref, n) in enumerate(TP):
    t = load('TestPoint.pretty', 'TestPoint_Pad_D1.5mm', ref, n, 9.6 + 2.6 * i, -14.0)
    wire(t, {'1': n})
    t.SetAttributes(t.GetAttributes() | pcbnew.FP_EXCLUDE_FROM_POS_FILES | pcbnew.FP_EXCLUDE_FROM_BOM)   # copper only
    t.Reference().SetVisible(False)                          # the row is labelled by the silk under it

# ======== U5 SY8089 buck: 5V -> 3V3 (t2's U1) ========
U5 = load('Package_TO_SOT_SMD.pretty', 'SOT-23-5', 'U5', 'SY8089AAAC', 18.5, -3.5, 0)
wire(U5, {'1': '5V', '2': 'GND', '3': 'LX', '4': '5V', '5': 'FB'})        # 1 EN (tied to IN), 2 GND, 3 LX, 4 IN, 5 FB
C('C5', '10uF', '5V', 'GND', 18.5, -7.0, 0)                                # VIN, beside pin 4
L2 = load('vein_base.pretty', 'L_Sunlord_SWPA4020S', 'L2', '2.2uH', 23.5, -3.0, 90)
wire(L2, {'1': 'LX', '2': '3V3'})
R('R6', '100k', '3V3', 'FB', 14.0, -4.0, 0)
R('R7', '22k', 'FB', 'GND', 14.0, -6.0, 0)
C('C6', '22uF', '3V3', 'GND', 24.0, 2.0, 0)
C('C8', '22uF', '3V3', 'GND', 20.0, 2.0, 0)
C9 = load('Capacitor_Tantalum_SMD.pretty', 'CP_EIA-3528-21_Kemet-B', 'C9', '220uF 6.3V', 22.0, 6.0, 0)
wire(C9, {'1': '3V3', '2': 'GND'})                                          # 1 = + (the band)
C('C7', '100nF', '3V3', 'GND', 25.5, 9.5, 90)
two('LED_SMD.pretty', 'LED_0603_1608Metric', 'D1', 'PWR (3V3)', 'GND', 'LEDA', 16.0, 12.2, 0)   # 1 = K, 2 = A
R('R5', '1k', '3V3', 'LEDA', 12.8, 12.2, 0)

# ======== J3 FP001S (SH 1.0 6P, opening +y) ========
J3 = load('Connector_JST.pretty', 'JST_SH_SM06B-SRSS-TB_1x06-1MP_P1.00mm_Horizontal', 'J3', 'FP001S (SH1.0 6P)',
          -16.0, Y1 - 3.4, 180)
FP_PINS = ['3V3', 'FPTX', 'FPRX', 'GND', 'FPDM', 'FPDP']           # the module's pins 1..6
jn = {str(i + 1): n for i, n in enumerate(reversed(FP_PINS) if SH_REVERSED else FP_PINS)}
wire(J3, {**jn, 'MP': 'GND'})
# J3's opening must face the +y edge: its signal pads sit behind (towards -y) its mounting pads
sig = [xy(p.GetPosition())[1] for p in J3.Pads() if p.GetNumber() != 'MP']
mp = [xy(p.GetPosition())[1] for p in J3.Pads() if p.GetNumber() == 'MP']
assert max(sig) < min(mp), 'J3 opening is not +y'

# the core's copper, locked (freerouting routes round it and leaves it out of the .ses)
for t in CORE['segments']:
    tr = pcbnew.PCB_TRACK(b); tr.SetStart(cxy(t['x0'], t['y0'])); tr.SetEnd(cxy(t['x1'], t['y1']))
    tr.SetWidth(mm(t['w'])); tr.SetLayer(pcbnew.F_Cu if t['layer'] == 'F.Cu' else pcbnew.B_Cu)
    tr.SetNet(nets[CORE_NET[t['net']]]); tr.SetLocked(True); b.Add(tr)
for v in CORE['vias']:
    vi = pcbnew.PCB_VIA(b); vi.SetPosition(cxy(v['x'], v['y'])); vi.SetWidth(mm(v['size']))
    vi.SetDrill(mm(max(v['drill'], 0.3)))                   # 0.25 -> 0.3 (JLC's standard drill)
    vi.SetNet(nets[CORE_NET[v['net']]]); vi.SetLocked(True); b.Add(vi)
# the core's zones (all on F.Cu) are kept free of other copper: a keepout for the routing (tracks / vias of other
# nets) round each, 0.3 out; under the regulator also on B.Cu (the minimal design's B.Cu there is solid GND)
CORE_KEEP = []
for z in CORE['zones']:
    xs = [p[0] for p in z['pts']]; ys = [p[1] for p in z['pts']]
    CORE_KEEP.append((min(xs) - 0.3, max(xs) + 0.3, min(ys) - 0.3, max(ys) + 0.3))

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
SILK = [('USB-C (PC)', -17.0, -12.2, 0.8),
        ('FP001S (SH1.0)', -16.0, 9.3, 0.8),
        ('J3 ' + ' '.join(f'{n}:{short[jn[n]]}' for n in '123'), -16.0, 8.0, 0.8),
        ('   ' + ' '.join(f'{n}:{short[jn[n]]}' for n in '456'), -16.0, 6.7, 0.8),
        ('BOOT GND RUN DIO CLK', 14.8, -11.6, 0.8)]
for t, x, y, sz in SILK:
    assert X0 + 0.3 <= x - len(t) * 0.4 * sz and x + len(t) * 0.4 * sz <= X1 - 0.3, t
    text(t, x, y, size=sz)
VERSION = open(os.path.join(HERE, '..', '..', 'VERSION')).read().strip()
text(f'FP001S USB {REV} v{VERSION}', 0, 0, layer=pcbnew.B_SilkS)
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
    fills = {z.GetLayer(): z.GetFilledPolysList(z.GetLayer()) for z in b.Zones()     # the board-wide GND pours only
             if not z.GetIsRuleArea() and z.GetNetname() == 'GND' and z.GetAssignedPriority() == 0}
    gvias = [v.GetPosition() for v in b.GetTracks() if v.GetClass() == 'PCB_VIA' and v.GetNetname() == 'GND']
    holes = [p.GetPosition() for f in b.GetFootprints() for p in f.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH]
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
                    if room(piece, q) and room(other, q) and not any((q - h).EuclideanNorm() < mm(0.9) for h in holes):
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


def core_zones(b, area=True):
    """The minimal design's zones (priorities one up, over our pours) and a 3V3 area on F.Cu over the core (the
    minimal design's F.Cu is a 3V3 pour, which several of its decoupling caps reach their supply through)."""
    def zone(net, layer, pts, prio, clr, mint, solid, gap=0.5, width=0.5):
        z = pcbnew.ZONE(b); z.SetLayer(layer); z.SetNet(b.FindNet(net)); z.SetAssignedPriority(prio)
        ol = z.Outline(); ol.NewOutline()
        for q in pts:
            ol.Append(q.x, q.y)
        z.SetLocalClearance(mm(clr)); z.SetMinThickness(mm(mint))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL if solid else pcbnew.ZONE_CONNECTION_THERMAL)
        z.SetThermalReliefGap(mm(gap)); z.SetThermalReliefSpokeWidth(mm(width))
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        b.Add(z)
    x0, x1, y0, y1 = -7.6, 8.2, -8.6, 14.8                     # rp_core_extract.py's BOX
    if area:                                                   # not in the DSN: the signals into the core cross it
        zone('3V3', pcbnew.F_Cu, [cxy(x0, y0), cxy(x1, y0), cxy(x1, y1), cxy(x0, y1)], 1, 0.2, 0.2, False)
    for z in CORE['zones']:
        zone(CORE_NET[z['net']], pcbnew.F_Cu if z['layer'] == 'F.Cu' else pcbnew.B_Cu,
             [cxy(px, py) for px, py in z['pts']], z['priority'] + 1, z['clearance'], z['min_thickness'],
             z['connect'] == 'yes', z['thermal_gap'], z['thermal_width'])


def core_keepouts(b):
    """For freerouting only: the core's zones as keepouts (no tracks / vias), so nothing else is routed through the
    regulator's and the crystal's copper. As planes in the DSN they would cover the other nets' pads under them."""
    for z in CORE['zones']:
        if z['net'] == '+3V3':            # 3V3 is routed to the core's pins through these (VREG_VIN, pin 49)
            continue
        k = pcbnew.ZONE(b); k.SetIsRuleArea(True); k.SetDoNotAllowTracks(True); k.SetDoNotAllowVias(True)
        k.SetDoNotAllowCopperPour(False); k.SetDoNotAllowPads(False); k.SetDoNotAllowFootprints(False)
        k.SetLayer(pcbnew.F_Cu if z['layer'] == 'F.Cu' else pcbnew.B_Cu)
        ol = k.Outline(); ol.NewOutline()
        for px, py in z['pts']:
            q = cxy(px, py); ol.Append(q.x, q.y)
        b.Add(k)


os.chdir(HERE)
if 'dsn' in sys.argv[1:]:
    core_keepouts(b)
else:
    core_zones(b)
if 'dsn' in sys.argv[1:]:
    b.Save(f'{NAME}.kicad_pcb')
    b = pcbnew.LoadBoard(f'{NAME}.kicad_pcb')
    print('dsn', pcbnew.ExportSpecctraDSN(b, f'{NAME}.dsn'))
    # 5V / LX routed 0.5 wide, 3V3 0.3 (the FP001S's 400 mA; 0.3 still meets the RP2354A's 0.4 pitch pins with 0.12
    # clearance): net classes written into the DSN for freerouting
    d = open(f'{NAME}.dsn').read()
    i = d.index('    (class kicad_default'); j = d.index('(circuit', i)
    body = d[i:j]
    for n in ('5V', '3V3', 'LX'):
        body = re.sub(rf'(?<=\s){n}(?=\s)', '', body)
    d = (d[:i] + '    (class PWR 5V LX\n      (circuit (use_via Via[0-1]_600:300_um))\n'
         '      (rule (width 500) (clearance 150))\n    )\n'
         '    (class P3V3 3V3\n      (circuit (use_via Via[0-1]_600:300_um))\n'
         '      (rule (width 300) (clearance 120))\n    )\n' + body + d[j:])
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
    fills = [z.GetFilledPolysList(z.GetLayer()) for z in b.Zones() if z.GetNetname() == 'GND' and z.GetAssignedPriority() == 0]
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
