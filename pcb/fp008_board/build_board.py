"""FP008 USB board (f6): the Grow FP008 face / palm vein module (Hangzhou Grow, user manual V1.01) on a PC through one
USB-C cable: the PC sees the module's camera (UVC) and an RP2354A (USB CDC), both behind one hub. The RP2354A talks to
the module's UART (the same commands as the FP001S, EF AA), holds the keys, does the face-check exchange and takes
signed firmware over its serial port (A / B with fallback): the firmware is alc-app-s3's crates/fp001s-rp2354
(2026-11-21, user: the MCU does the serial OTA and the face-check exchange; f1..f5 had a CH340C and
the keys on the PC's TPM, 2026-11-19). Sound comes from the PC's own speakers (no audio on the board).
  - J1  USB-C (to the PC): VBUS -> 5V, CC1 / CC2 5.1 k (R1 / R2), D+ / D- through U2 (USBLC6-2SC6) to U3's upstream.
  - U3  CH334F (QFN-24 4x4) USB 2.0 hub, self-powered from 5V (V5 -> internal LDO -> VDD33 = HUB33), Y1 12 MHz (load
        caps inside the CH334). Pins (WCH CH334/CH335 datasheet V2.4, table 1-3, column 4F): DMU 14 / DPU 15,
        DM1 11 / DP1 12 -> the FP008's USB (camera), DM2 9 / DP2 10 -> U6, DM3 7 / DP3 8 -> J2, port 4 unused.
  - J2  USB-C receptacle (a device, e.g. a USB speaker; at the +x end, f5) on hub port 3: VBUS = 5V straight (no switch,
        no fuse), CC1 / CC2 56 k to 5V (R3 / R4, Rp: default USB power), D+ / D- through U5 (USBLC6-2SC6).
        The PC port feeds everything: on a 500 mA USB 2.0 port leave the device ~250 mA.
  - U6  RP2354A (QFN-60 7x7, RP2350 with 2 MB flash inside, no radio) on hub port 2 (R107 / R108 27 R): UART0 GPIO0 TX
        -> FP008 RXD, GPIO1 RX <- FP008 TXD (115200 8N1), GPIO2 <- the FP008's IRQ (its infrared presence sensor;
        high = someone is there; f5 had it on the CH340C's CTS#). Its core (regulator L106 / C106 / C107 / C109 /
        R103, crystal Y106 with C103 / C104 / R102, the 100 nF decoupling) is Raspberry Pi's "RP2350A Minimal"
        layout as they drew it (rp_core.py, the data rp2350_core.json and the MIT licence, all here), their
        0.25 drills opened to 0.3. BOOTSEL (TP1: QSPI_SS through R110 1 k, short to TP2 GND at power-up), RUN (TP3,
        R111 10 k pull-up), SWD (TP4 SWDIO / TP5 SWCLK) are test pads on B, the outside, for the factory only.
  - U1  XC6206P332MR (SOT-23, 3.3 V LDO, 200 mA) 5V -> 3V3 for U6 (~50 mA at most: RP2350 at 150 MHz with USB ~30,
        the flash inside while writing ~15) and the FP008's sensor supply (pin 6, 60 uA): a quarter of its 200 mA,
        ~0.1 W in the SOT-23, and 3.3 V still out at VBUS 4.4 V (dropout ~0.1 V at 50 mA). No buck: that is for a module
        drawing its own ~400 mA from 3V3 (the FP001S); the FP008 runs on 5V.
  - J3  Molex PicoBlade 53398-0871 (MX1.25 8P, vertical SMD, LCSC C471413; f7) for the FP008 cable, the module's pins
        (manual 1.3.2): 1 VCC 4.5-15 V (5V), 2 GND, 3 TXD (module out), 4 RXD (module in), 5 IRQ, 6 sensor VCC (3V3),
        7 D+, 8 D-. CHECK THE CABLE BEFORE ORDERING (pin 1 on pin 1).
  - D1 + R5: 3V3 power LED.
  f3 (2026-11-19, user): the board is the FP008's back lid. Its outline is the module's rear body (manual 1.3.1:
  55.45 x 34.45, drawn as a rounded rectangle, corners R12 -- the real corner shape is to be checked), screwed to the
  module's four rear screw holes H1..H4 (read off the manual's rear drawing then; f8 below).
  f5 (2026-11-20, user: no tongue): the outline is the rear body only. J1 (-x end) and J2 (+x end) face a window
  each (WIN), the L adapters' bodies go up through them and their elbows sit in the module's rear recess (~5.1 deep
  needed). The parts moved around the two (U4 at the bottom, J3 at the top centre); U3's exposed pad has vias.
  f4 (2026-11-20, user): the parts face the module (F = inside; one side, so still JLC Economic), only the cables come
  out. The outline gets a tongue on -x (to XT, |y| <= TY) past the module's rear body; J1 / J2 sit side by side under
  it (13.5 apart for two plugs), openings -x, wholly outside the body (asserted), and the cables take an L-shaped
  (90 deg) adapter at the plug. The parts keep KEEP clear of the screw bosses (asserted); J3 sits inside at the top
  centre and its cable goes straight to the module's own 8P socket (no slot). The module's rear recess has to take the
  parts (up to 3.3; J3 from f7 higher, below): measure it before ordering.
  5V load: FP008 200 mA + hub ~30 mA + RP2354A ~50 mA + whatever is on J2.
Board coords (KiCad's, seen from the F side = from inside the module, so mirrored from behind): origin = the FP008's
centre, its UP up, J1 (USB-C, PC) at the -x end and J2 (USB-C, device) at the +x end, J3 at the top centre, U6 (the
RP2354A and its core) in the middle under J3, the hub above J1, the LDO below J2, the test pads on B at the bottom left.
f6 (2026-11-21): the outline, holes, windows, J1 / J2 / J3 and the parts' height as f5; the CH340C (U4, C4) gone.
f7 (2026-11-21, user: "まず縦して"): J3 is the vertical PicoBlade 53398-0871 (was f6's horizontal PicoBlade 8P at (0, 12.6),
  opening +y), turned 0 at (0, 9.85): the pad row up, the MP pads down, pin 1 at -x; pins and nets unchanged,
  rerouted. The plug goes in straight from the module's side. The module's own 8P socket is at the top edge by the wall
  (user: "端じゃなければ関係ない"), so J3 sits just under its place (taken as f6's J3 housing SOCK, x +-7.58, y 11.0..15.2):
  J3's housing x +-7.58, y 7.25..10.95, 0.05 under it (asserted). The footprint is KiCad's with the courtyard
  tightened to 0.1 (vein_base.pretty) to fit between SOCK and the RP2354A core; C8 moved under J3's pin 1 (-5.0, 4.6).
  Heights over the board: the housing 4.7 (JLC's Z height for C471413), the mated 51021 plug ~5.7 (as the 4P
  53398-0471 on the station boards), the wires' bend over it ~1.8: J3 is now the tallest part (the rest up to 3.3), so
  the module's rear recess has to take ~7.5 there -- not known, measure it before ordering.
f8 (2026-11-23, the maker on the real module): the screw holes H1..H4 are M3 (MountingHole_3.2mm_M3; the module takes
  M3 x 6 through its bracket's inner holes), at (+-18.15, +-12.5): y 25 apart from the maker's answer (the bracket's
  inner two holes); x 36.3 measured on the manual's rear drawing (1.3.1, scanned at 300 dpi, the scale set so that
  the holes' y comes to 25; +-0.2), f7's 36.7 was too wide. The holes are drilled 3.4 (M3 loose) for that +-0.2:
  KiCad's MountingHole_3.2mm_M3 (NPTH, no copper) with its drill and hole size set to 3.4. Parts, pads (the test pads on B too) and
  windows 3.5 from a hole's centre (KEEP, asserted), the holes 3.0 inside the outline (the M3 head 5.5). No part moved,
  f7's routing kept (DRC clean).
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
sys.path.insert(0, HERE)
from rp_core import Core  # noqa: E402

REV = 'f8'
NAME = 'fp008_board'
FP = '/usr/share/kicad/footprints/'
OX, OY = 100.0, 100.0
mm = pcbnew.FromMM

X0, X1, Y0, Y1 = -27.5, 27.5, -17.0, 17.0          # the FP008's rear body 55.45 x 34.45, a hair inside
RC = 12.0                                           # corner radius (guess from the drawing)
HOLES = [(sx * 18.15, sy * 12.5) for sx in (-1, 1) for sy in (-1, 1)]    # the module's rear screw holes, M3 (f8)
HOLE_D = 3.4                                        # M3, loose: the x read off the drawing is +-0.2 (f8)
# f5 (2026-11-20, user: no tongue, the cables' plugs inside): J1 / J2 sit inside the rear body's outline, J1 opening -x
# and J2 opening +x, each facing a window WIN through the board between it and the edge. An L adapter (USB-C plug ->
# female turned 90 deg, ~AD_W x AD_D across, the female end up, sizes from a product photo: check the real one) goes in
# the window and its elbow under the board sits in the module's rear recess (needs ~5 deep: measure it). The windows
# keep EDGE of board to the outline and keep clear of the screw holes; the plugs go in with the board off the module.
AD_W, AD_D = 12.4, 7.5                              # adapter across (y) and deep (x, from the receptacle's face)
NW, ND = AD_W + 1.0, AD_D + 1.0 + 0.3               # window across, deep from XF (the receptacle's face is 0.3 past XF)
EDGE = 1.5                                          # board left between a window and the outline
XF = -X0 - EDGE - ND                                # J1's opening at x = -XF, J2's at +XF (|x| of the window's inner side)
WIN = [(-XF - ND, -XF, -NW / 2, NW / 2), (XF, XF + ND, -NW / 2, NW / 2)]   # (x0, x1, y0, y1)
KEEP = 3.5                                          # clear of each screw hole's centre (M3 head 5.5, its boss; f4, f8)


def outline(n=10):
    """The rear body's rounded rectangle, as a closed list of points (anticlockwise)."""
    pts = []
    for cx, cy, a0 in ((X1 - RC, Y0 + RC, -90), (X1 - RC, Y1 - RC, 0), (X0 + RC, Y1 - RC, 90), (X0 + RC, Y0 + RC, 180)):
        for k in range(n + 1):
            t = math.radians(a0 + 90 * k / n)
            pts.append((cx + RC * math.cos(t), cy + RC * math.sin(t)))
    return pts


OUTLINE = outline()


def in_win(x, y, m=0.0):
    """(x, y) within m of a window."""
    return any(x0 - m < x < x1 + m and y0 - m < y < y1 + m for x0, x1, y0, y1 in WIN)


def inside(x, y, m=0.0):
    """(x, y) on the board (inside the outline, out of the windows) and at least m from its edges."""
    if in_win(x, y, m):
        return False
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


for x0, x1, y0, y1 in WIN:                          # the windows clear of the screw holes (M3, f8)
    for hx, hy in HOLES:
        assert math.hypot(max(x0 - hx, 0, hx - x1), max(y0 - hy, 0, hy - y1)) >= KEEP, ('window on a hole', hx, hy)


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
for n in ['GND', '5V', '3V3', 'HUB33', 'CC1', 'CC2', 'UDP', 'UDN', 'XI', 'XO', 'FPDP', 'FPDM', 'SDP', 'SDN',
          'FPTX', 'FPRX', 'IRQ', 'LEDA', 'DCC1', 'DCC2', 'D3P', 'D3N', 'J2P', 'J2N',
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
J1 = load('Connector_USB.pretty', 'USB_C_Receptacle_HRO_TYPE-C-31-M-12', 'J1', 'USB-C (PC)', -XF + 3.05, 0.0, 270)
wire(J1, {**USB_GND, 'A5': 'CC1', 'B5': 'CC2', 'A4': '5V', 'A9': '5V', 'B4': '5V', 'B9': '5V',
          'A6': 'UDP', 'B6': 'UDP', 'A7': 'UDN', 'B7': 'UDN'})
R('R1', '5.1k', 'CC1', 'GND', -11.6, -10.0, 0)
R('R2', '5.1k', 'CC2', 'GND', -11.6, -11.6, 0)
U2 = load('Package_TO_SOT_SMD.pretty', 'SOT-23-6', 'U2', 'USBLC6-2SC6', -11.6, -7.5, 0)
wire(U2, {'1': 'UDP', '6': 'UDP', '3': 'UDN', '4': 'UDN', '2': 'GND', '5': '5V'})
C('C5', '10uF', '5V', 'GND', -11.6, -13.4, 0)             # VBUS bulk at J1

U3 = load('Package_DFN_QFN.pretty', 'QFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm', 'U3', 'CH334F', -11.8, 9.0, 180)
wire(U3, {'25': 'GND', '3': 'XO', '4': 'XI', '9': 'SDN', '10': 'SDP', '11': 'FPDM', '12': 'FPDP',
          '7': 'D3N', '8': 'D3P', '14': 'UDN', '15': 'UDP', '19': '5V', '20': 'HUB33'})
ux, uy = xy(U3.GetPosition())
for dx in ((-0.7, 0.7) if 'dsn' in sys.argv[1:] else ()):   # U3's exposed pad (its only GND) to the B.Cu pour:
    for dy in (-0.7, 0.7):                                   # vias in the pad, kept in the .ses with the routing
        v = pcbnew.PCB_VIA(b); v.SetPosition(P(ux + dx, uy + dy)); v.SetWidth(mm(0.6)); v.SetDrill(mm(0.3))
        v.SetNet(nets['GND']); b.Add(v)
XTAL = load('Crystal.pretty', 'Crystal_SMD_3225-4Pin_3.2x2.5mm', 'Y1', '12MHz', -11.8, 14.0, 0)
wire(XTAL, {'1': 'XI', '3': 'XO', '2': 'GND', '4': 'GND'})
C('C1', '1uF', '5V', 'GND', -7.7, 3.6, 90)        # V5 (pins 19 / 20): the strip between J1 and the core
C('C2', '10uF', 'HUB33', 'GND', -7.7, -2.9, 90)            # VDD33
C('C3', '100nF', 'HUB33', 'GND', -7.7, 0.5, 90)

# ======== U6 RP2354A on hub port 2 (f6): UART0 to the FP008, its IRQ on GPIO2; U1 3.3 V LDO ========
# The chip with its core regulator, crystal, decoupling and USB series resistors is Raspberry Pi's "RP2350A Minimal"
# layout, footprints, tracks, vias and zones (rp_core.py here, the data in
# rp2350_core.json here, MIT: rp2350_core_LICENSE.txt here). Refs: U1 -> U6, L1 -> L106,
# X1 -> Y106, Cn / Rn -> C1nn / R1nn.
RP = (0.5, -1.4)                                    # U6's origin
core = Core(b, nets, RP, {'/USB_D+': 'SDP', '/USB_D-': 'SDN',           # R7 / R8's outer pads: the hub's port 2
                          '/GPIO0': 'FPRX', '/GPIO1': 'FPTX',          # UART0 TX -> the FP008's RXD, RX <- its TXD
                          '/GPIO2': 'IRQ',                             # the FP008's IRQ (high = someone is there)
                          '/RUN': 'RUN', '/SWD': 'SWDIO', '/SWCLK': 'SWCLK', '/QSPI_SS': 'QSS'})
U6 = core.place()
U6.SetValue('RP2354A')
# BOOTSEL / RUN / SWD on test pads on B (the outside: reached with the board on the module), for the factory only:
# BOOT = QSPI_SS through R110 1 k (the minimal design's R6), shorted to GND at power-up for the ROM's USB boot; RUN
# pulled up by R111 10 k
R('R110', '1k', 'QSS', 'BOOT', -11.6, -15.6, 0)
R('R111', '10k', '3V3', 'RUN', 6.5, -9.0, 90)
TP = [('TP1', 'BOOT'), ('TP2', 'GND'), ('TP3', 'RUN'), ('TP4', 'SWDIO'), ('TP5', 'SWCLK')]
TPX, TPY, TPP = -14.0, -14.6, 2.6                   # the row on B (seen from the F side, as everything here)
for i, (ref, n) in enumerate(TP):
    t = load('TestPoint.pretty', 'TestPoint_Pad_D1.5mm', ref, n, TPX + TPP * i, TPY)
    t.Flip(t.GetPosition(), False)                  # B: the outside
    wire(t, {'1': n})
    t.SetAttributes(t.GetAttributes() | pcbnew.FP_EXCLUDE_FROM_POS_FILES | pcbnew.FP_EXCLUDE_FROM_BOM)   # copper only
    t.Reference().SetVisible(False)                 # the row is labelled by the silk beside it
U1 = load('Package_TO_SOT_SMD.pretty', 'SOT-23', 'U1', 'XC6206P332MR', 11.6, -8.0, 0)
wire(U1, {'1': 'GND', '2': '3V3', '3': '5V'})                              # 1 VSS, 2 VOUT, 3 VIN
C('C6', '1uF', '5V', 'GND', 11.6, -11.0, 0)
C('C7', '1uF', '3V3', 'GND', 11.6, -12.6, 0)
two('LED_SMD.pretty', 'LED_0603_1608Metric', 'D1', 'PWR (3V3)', 'GND', 'LEDA', 11.6, -14.4, 0)   # 1 = K, 2 = A
R('R5', '1k', '3V3', 'LEDA', 8.6, -14.4, 0)

# ======== J2 USB-C (a device on hub port 3; opening -y beside J1) ========
J2 = load('Connector_USB.pretty', 'USB_C_Receptacle_HRO_TYPE-C-31-M-12', 'J2', 'USB-C (device)', XF - 3.05, 0.0, 90)
wire(J2, {**USB_GND, 'A5': 'DCC1', 'B5': 'DCC2', 'A4': '5V', 'A9': '5V', 'B4': '5V', 'B9': '5V',
          'A6': 'J2P', 'B6': 'J2P', 'A7': 'J2N', 'B7': 'J2N'})
R('R3', '56k', '5V', 'DCC1', 11.6, 11.0, 0)
R('R4', '56k', '5V', 'DCC2', 11.6, 12.6, 0)
U5 = load('Package_TO_SOT_SMD.pretty', 'SOT-23-6', 'U5', 'USBLC6-2SC6', 11.6, 8.0, 0)
wire(U5, {'1': 'D3P', '6': 'J2P', '3': 'D3N', '4': 'J2N', '2': 'GND', '5': '5V'})
C('C9', '10uF', '5V', 'GND', 11.6, 14.6, 0)                # VBUS at J2
for j, sx in ((J1, 1), (J2, -1)):                   # each USB-C's two 5V pad pairs (A4 / B9, A9 / B4) tied by a via
    # beside each and B.Cu between them, as f6's routing had them at J2 (f7's freerouting left them apart): locked, so
    # written into the DSN as fixed wiring (freerouting does not give fixed wiring back in the .ses: added here in both
    # runs). 1.18 from the pad centre: the via 0.15 clear of the pad's inner end
    (xa, ya), (xb, yb) = (xy(q.GetPosition()) for q in j.Pads() if q.GetNumber() in ('A4', 'A9'))
    xv = xa + sx * 1.18
    for (x0, y0), (x1, y1), lay in (((xa, ya), (xv, ya), pcbnew.F_Cu), ((xb, yb), (xv, yb), pcbnew.F_Cu),
                                    ((xv, ya), (xv, yb), pcbnew.B_Cu)):
        t = pcbnew.PCB_TRACK(b); t.SetStart(P(x0, y0)); t.SetEnd(P(x1, y1)); t.SetWidth(mm(0.5))
        t.SetLayer(lay); t.SetNet(nets['5V']); t.SetLocked(True); b.Add(t)
    for yv in (ya, yb):
        v = pcbnew.PCB_VIA(b); v.SetPosition(P(xv, yv)); v.SetWidth(mm(0.6)); v.SetDrill(mm(0.3))
        v.SetNet(nets['5V']); v.SetLocked(True); b.Add(v)

# ======== J3 FP008 (PicoBlade 8P vertical, f7: the plug goes in straight from the module's side) ========
# The module's own 8P socket sits at the top edge, by the wall (user, from the manual's rear photo): J3's housing (the
# tall part, the mated plug inside the same outline) stays off the socket's place, taken as f6's horizontal J3's housing
# SOCK. Turned 0: the pad row up (towards the socket), the MP pads down, pin 1 at -x. The space between SOCK and the
# RP2354A core (R107 / R108 / L106 up to y 6.7, not moved) is 4.3: the footprint is KiCad's with the courtyard 0.1
# round the copper and the body (vein_base.pretty, ..._Crt0.1; KiCad's is 0.5 and would hit the core's courtyards).
SOCK = (-7.58, 7.58, 11.0, 15.2)                    # x0, x1, y0, y1: f6's horizontal J3 (at (0, 12.6), 180), its F.Fab body
J3Y = SOCK[2] - 0.05 - 1.1                          # the housing's top (local -1.1, turned 0) 0.05 under SOCK
J3 = load('vein_base.pretty', 'Molex_PicoBlade_53398-0871_1x08-1MP_P1.25mm_Vertical_Crt0.1', 'J3', 'FP008 (MX1.25 8P)',
          0.0, J3Y, 0)
FP_PINS = ['5V', 'GND', 'FPTX', 'FPRX', 'IRQ', '3V3', 'FPDP', 'FPDM']    # the module's pins 1..8
wire(J3, {**{str(i + 1): n for i, n in enumerate(FP_PINS)}, 'MP': 'GND'})
C('C8', '10uF', '5V', 'GND', -5.0, 4.6, 0)             # the module's 200 mA: under J3's pin 1 (5V, -x), right of C1
for p in J3.Pads():                                 # every pad on the board (not in a window, off the edge) and clear
    bb_ = p.GetBoundingBox()                        # of the screw bosses
    for qx in (bb_.GetLeft(), bb_.GetRight()):
        for qy in (bb_.GetTop(), bb_.GetBottom()):
            x_, y_ = xy(pcbnew.VECTOR2I(qx, qy))
            assert inside(x_, y_, 0.5), ('J3 pad off the board', p.GetNumber(), x_, y_)
            assert all(math.hypot(x_ - hx, y_ - hy) >= KEEP for hx, hy in HOLES), ('J3 pad on a boss', p.GetNumber())
sig = sorted((xy(p.GetPosition())[0], int(p.GetNumber())) for p in J3.Pads() if p.GetNumber() != 'MP')
assert [n for _, n in sig] == list(range(1, 9)), 'J3 pin 1 is not at -x'
fab = [xy(q) for g in J3.GraphicalItems() if g.GetLayer() == pcbnew.F_Fab and g.GetClass() in ('MGRAPHIC', 'FP_SHAPE', 'PCB_SHAPE')
       for q in (g.GetStart(), g.GetEnd())]       # the body's lines (F.Fab), their ends
hx0, hx1 = min(q[0] for q in fab), max(q[0] for q in fab)
hy0, hy1 = min(q[1] for q in fab), max(q[1] for q in fab)
assert hx1 <= SOCK[0] or hx0 >= SOCK[1] or hy1 <= SOCK[2] or hy0 >= SOCK[3], ('J3 housing on the socket', hy1)
print(f'J3 housing x {hx0:.2f}..{hx1:.2f} y {hy0:.2f}..{hy1:.2f}, {SOCK[2] - hy1:.2f} under the socket')

for i, (x, y) in enumerate(HOLES, 1):
    assert inside(x, y, 3.0), ('hole too near the edge', x, y)   # the M3 head (5.5) on the board
    h = load('MountingHole.pretty', 'MountingHole_3.2mm_M3', f'H{i}', 'M3', x, y)
    for p in h.Pads():                              # NPTH: the hole is the pad, both 3.4
        p.SetDrillSize(pcbnew.VECTOR2I(mm(HOLE_D), mm(HOLE_D))); p.SetSize(pcbnew.VECTOR2I(mm(HOLE_D), mm(HOLE_D)))

# ---- outline
def edge_loop(pts):
    for (a, c), (d, e) in zip(pts, pts[1:] + pts[:1]):
        sh = pcbnew.PCB_SHAPE(b); sh.SetShape(pcbnew.SHAPE_T_SEGMENT)
        sh.SetStart(P(a, c)); sh.SetEnd(P(d, e)); sh.SetLayer(pcbnew.Edge_Cuts); sh.SetWidth(mm(0.1)); b.Add(sh)


edge_loop(OUTLINE)
for x0, x1, y0, y1 in WIN:
    edge_loop([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
for fp in b.GetFootprints():                        # every part inside the outline (courtyard corners)
    cy_ = fp.GetCourtyard(pcbnew.F_CrtYd)
    if cy_.OutlineCount() and not fp.GetReference().startswith('H'):
        bb_ = cy_.BBox()
        for q in (bb_.GetOrigin(), bb_.GetEnd()):
            for qx in (bb_.GetLeft(), bb_.GetRight()):
                for qy in (bb_.GetTop(), bb_.GetBottom()):
                    x_, y_ = xy(pcbnew.VECTOR2I(qx, qy))
                    if fp.GetReference() in ('J1', 'J2'):   # its front over the window, as over an edge: check the rest
                        x_ = math.copysign(min(abs(x_), XF - 0.3), x_)
                    assert inside(x_, y_, 0.2), (fp.GetReference(), x_, y_)
        L, Rr = pcbnew.ToMM(bb_.GetLeft()) - OX, pcbnew.ToMM(bb_.GetRight()) - OX
        T_, B_ = OY - pcbnew.ToMM(bb_.GetBottom()), OY - pcbnew.ToMM(bb_.GetTop())
        for hx, hy in HOLES:                        # clear of the screw bosses (the parts face the module)
            dx = max(L - hx, 0, hx - Rr); dy = max(T_ - hy, 0, hy - B_)
            assert math.hypot(dx, dy) >= KEEP, (fp.GetReference(), 'on the boss at', hx, hy)
for fp in b.GetFootprints():                        # every pad (F and B, the test pads too) KEEP from a hole's centre (f8)
    if fp.GetReference().startswith('H'):
        continue
    for p in fp.Pads():
        bb_ = p.GetBoundingBox()
        L, Rr = pcbnew.ToMM(bb_.GetLeft()) - OX, pcbnew.ToMM(bb_.GetRight()) - OX
        T_, B_ = OY - pcbnew.ToMM(bb_.GetBottom()), OY - pcbnew.ToMM(bb_.GetTop())
        for hx, hy in HOLES:
            assert math.hypot(max(L - hx, 0, hx - Rr), max(T_ - hy, 0, hy - B_)) >= KEEP, (fp.GetReference(), p.GetNumber())
for j, sx in ((J1, -1), (J2, 1)):                   # each USB-C's opening at its window (J1 -x, J2 +x)
    bb_ = j.GetCourtyard(pcbnew.F_CrtYd).BBox()
    front = pcbnew.ToMM(bb_.GetLeft() if sx < 0 else bb_.GetRight()) - OX
    assert sx * front > XF, (j.GetReference(), 'opening not at its window')


def text(s, x, y, layer=pcbnew.F_SilkS, size=1.0, rot=0):
    t = pcbnew.PCB_TEXT(b); t.SetText(s); t.SetPosition(P(x, y)); t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size))); t.SetTextThickness(mm(0.15)); t.SetTextAngleDegrees(rot)
    if layer == pcbnew.B_SilkS:
        t.SetMirrored(True)
    b.Add(t)


# silk: 1 character ~ 0.8 x size wide, centred: keep both ends inside the outline
# the outside is B (the parts face the module, f4): labels on B.SilkS, beside each USB-C on the board's inner side
SILK = [('PC', -XF - ND / 2, NW / 2 + 1.5, 1.0), ('DEVICE', XF + ND / 2, NW / 2 + 1.5, 1.0)]
for t, x, y, sz in SILK:
    assert inside(x - len(t) * 0.4 * sz, y, 0.3) and inside(x + len(t) * 0.4 * sz, y, 0.3), t
    text(t, x, y, layer=pcbnew.B_SilkS, size=sz)
VERSION = open(os.path.join(HERE, '..', '..', 'VERSION')).read().strip()
text(f'FP008 USB {REV} v{VERSION}', 0, 2.0, layer=pcbnew.B_SilkS)
text('CHECK THE CABLE: PIN 1 = 5V', 0, 0.0, layer=pcbnew.B_SilkS, size=0.8)
text('J3 1:5V 2:G 3:TX 4:RX 5:IRQ 6:3V3 7:D+ 8:D-', 0, -1.6, layer=pcbnew.B_SilkS, size=0.7)
TPS = 'BOOT GND RUN DIO CLK'                        # over the test pads on B (f6)
text(TPS, TPX + TPP * 2, TPY + 1.6, layer=pcbnew.B_SilkS, size=0.8)
assert inside(TPX + TPP * 2 - len(TPS) * 0.32, TPY + 1.6, 0.3) and inside(TPX + TPP * 2 + len(TPS) * 0.32, TPY + 1.6, 0.3)


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
            ok = (inside(x, y, 1.0) and all((x - hx) ** 2 + (y - hy) ** 2 > KEEP ** 2 for hx, hy in HOLES)
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
    crt = [fp.GetCourtyard(pcbnew.F_CrtYd) for fp in b.GetFootprints()]
    ring = [(mm(r * math.cos(a)), mm(r * math.sin(a))) for a in [k * math.pi / 4 for k in range(8)]]
    holes = [P(hx, hy) for hx, hy in HOLES]
    pth = [p.GetPosition() for f in b.GetFootprints() for p in f.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH]

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
                    if (room(piece, q) and room(other, q) and all((q - h).EuclideanNorm() > mm(KEEP) for h in holes)
                            and not any((q - h).EuclideanNorm() < mm(0.9) for h in pth)):
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
    core.keepouts()
else:
    core.zones()
if 'dsn' in sys.argv[1:]:
    b.Save(f'{NAME}.kicad_pcb')
    b = pcbnew.LoadBoard(f'{NAME}.kicad_pcb')
    print('dsn', pcbnew.ExportSpecctraDSN(b, f'{NAME}.dsn'))
    # 5V routed 0.5 wide (the FP008's 200 mA), 3V3 0.3 (0.3 still meets the RP2354A's 0.4 pitch pins with 0.12
    # clearance; the core's 3V3 is ~50 mA): net classes written into the DSN for freerouting
    d = open(f'{NAME}.dsn').read()
    i = d.index('    (class kicad_default'); j = d.index('(circuit', i)
    body = d[i:j]
    for n in ('5V', '3V3'):
        body = re.sub(rf'(?<=\s){n}(?=\s)', '', body)
    d = (d[:i] + '    (class PWR 5V\n      (circuit (use_via Via[0-1]_600:300_um))\n'
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
    fills = [z.GetFilledPolysList(z.GetLayer()) for z in b.Zones() if z.GetNetname() == 'GND' and z.GetAssignedPriority() == 0]
    loose = [v for v in b.GetTracks() if v.GetClass() == 'PCB_VIA' and v.GetNetname() == 'GND'
             and not all(f.Contains(v.GetPosition()) for f in fills)
             and not any(t.GetClass() != 'PCB_VIA' and t.GetNetname() == 'GND' and t.HitTest(v.GetPosition())
                         for t in b.GetTracks())]
    for v in loose:
        b.Remove(v)
    print(f'removed {len(loose)} loose vias')
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    # a via joining two pour pieces that hold no GND pad or track end only ties floating copper together: drop it
    # (its pieces then go as islands)
    def anchored(poly, i):
        piece = pcbnew.SHAPE_POLY_SET(); piece.AddOutline(poly.Outline(i))
        for h in range(poly.HoleCount(i)):
            piece.AddHole(poly.Hole(i, h))
        pads = [p_.GetPosition() for fp in b.GetFootprints() for p_ in fp.Pads() if p_.GetNetname() == 'GND']
        ends = [q for t in b.GetTracks() if t.GetClass() != 'PCB_VIA' and t.GetNetname() == 'GND'
                for q in (t.GetStart(), t.GetEnd())]
        return any(piece.Contains(q) for q in pads + ends)
    for _ in range(3):
        fl = {z.GetLayer(): z.GetFilledPolysList(z.GetLayer()) for z in b.Zones()
              if z.GetNetname() == 'GND' and z.GetAssignedPriority() == 0}
        idle = []
        for v in [t for t in b.GetTracks() if t.GetClass() == 'PCB_VIA' and t.GetNetname() == 'GND']:
            q = v.GetPosition()
            ok = False
            for f in fl.values():
                for i in range(f.OutlineCount()):
                    pc = pcbnew.SHAPE_POLY_SET(); pc.AddOutline(f.Outline(i))
                    if pc.Contains(q) and anchored(f, i):
                        ok = True
            if not ok and not any(t.GetClass() != 'PCB_VIA' and t.GetNetname() == 'GND' and t.HitTest(q)
                                  for t in b.GetTracks()):
                idle.append(v)
        for v in idle:
            b.Remove(v)
        print(f'removed {len(idle)} vias between floating pieces')
        if not idle:
            break
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
