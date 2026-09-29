"""Vein Station board (r12): one PCB under the VoiceS3R that carries everything the station needs.
  - J1/J2: VoiceS3R Ext.Pin (same positions as vein-base v0.6)
  - J3: finger vein module, MX1.25 4P (G5 -> module RXD, G6 <- module TXD, 3V3, GND; same pin order as vein-base)
  - U1 MAX3232 (3.3 V) + C1..C5: G7 -> T1IN, R1OUT -> G8 (UART to the FC-1200 alcohol checker, 9600 8N1)
  - SW1 4-way DIP: straight / cross of DB9 pins 2 and 3
        SW1-1 TX -> DB9-3, SW1-2 RX <- DB9-2   (passthrough: 1+2 ON, the same as a PC. The FC-1200 works
                                                 with the RS232M Module 13.2 switch on passthrough, so ship 1+2 ON)
        SW1-3 TX -> DB9-2, SW1-4 RX <- DB9-3   (cross:    3+4 ON)
  - J4: DB9 male, right angle (the same gender as the RS232M Module 13.2), on the -y edge next to the VoiceS3R, so
        the DB9 and the VoiceS3R's USB-C both leave through the station's back wall (pin 5 = GND, shell = GND).
        r12 moved it 4.0 towards the VoiceS3R (flange 0.5 / body 0.9 from it) and re-routed with freerouting 1.9.0.
Board coords are vein-base's: origin = Atom centre, +y = away from the USB-C / PORT.A edge, F faces the Atom.
The station turns the board 180° (USB-C side to the back): x_st = VX - x, ys_st = VYS + y (station/build_station.py).

Two outlines of the same circuit (same parts, same routing), both r12:
  printed        60 × 35, for the printed enclosure (station/build_station.py) -> station_board.kicad_pcb
  'pf'           92 × 71, for the Takachi PF13-4-9 off-the-shelf case -> station_board_pf.kicad_pcb.
                 The outline grows around the 60 × 35 area only, so its parts and tracks stay as they are.
                 The board stands on the case's own PCB bosses (87 × 47) on Takachi TPS-M2.3-7 tapping spacers and
                 M2.3 screws (B1..B4, 2.6 cut-outs drawn on Edge.Cuts: a footprint's courtyard would overlap SW1's).
                 The modules stand on stock M3 male-female hex spacers, male end down through the board with a nut
                 under it: NFC 12 mm (H1..H4), vein 6 mm (H5..H8).

  'sw75'         the same circuit and parts placed anew for the Takachi SW-75B (station/build_station_sw75.py), with
                 the VoiceS3R outside the case: the board fills the case and a tongue (26 wide) runs out through the
                 +y end wall; the VoiceS3R stands on the tongue on J1 / J2, its USB-C / PORT.A edge to +y (outwards),
                 its top level with the cover. The vein module stands on M3 × 6 spacers on the board (H1..H4, H1 / H4
                 into Takachi ASR-7 stuck to the floor), MAX3232 and J3 under it; SW1 above the DB9 (reached by taking
                 the cover off); the DB9 on the +x edge; H5 on the tongue takes a foot down to the desk. Board coords =
                 case coords there (origin = case centre, x across the 50 side, y along the 75 side). Parts, holes and
                 the -y notch are also in station/build_station_sw75.py: keep the two together.
                 -> station_board_sw75.kicad_pcb, routed on its own (station_board_sw75.ses)
  'sw130'        the same circuit and parts placed anew for the Takachi SW-130B (station/build_station_sw130.py), all
                 inside the case in a row along it: the DB9 on the -y edge (through the -y end wall), the vein module
                 on M3 × 5 spacers (VHB, y -30..29) over MAX3232 / C1..C5, J3 and SW1 between it and the DB9 (SW1 on
                 the +x side, reached with the cover off; the vein cable's slack lies on the -x side), and the VoiceS3R on
                 J1 / J2 at the +y end, centred, its USB-C / PORT.A edge to +y (through the +y end wall). The Unit NFC
                 plugs into J6 on the -x edge by the DB9 instead of the VoiceS3R's PORT.A (NFC and USB on different
                 faces): J6 = G38 (SDA) / G39 (SCL) / 5V / GND from the Ext.Pin, 4.7 k pull-ups R1 / R2, so the
                 firmware opens that I2C on G38 / G39. J6 is the genuine JST S4B-PH-SM4-TB (C265102; JLC found the
                 HY2.0 C722729's pins off the pads), its front 2.3 inside the edge. Its own BOM (jlc_bom_sw130.csv). The board
                 stands 3.0 off the floor on M3 × 3 spacers (H1..H7). Board coords = case coords (origin = case
                 centre, x across the 40 side, y along the 130 side); keep the numbers together with that script.
                 -> station_board_sw130.kicad_pcb, routed on its own (station_board_sw130.ses)

Routing comes from freerouting and is kept in station_board[_sw75].ses (the board file itself is always generated):
    python3 build_board.py [sw75] dsn   # placement only -> .dsn (feed it to freerouting -> .ses)
    python3 build_board.py [pf|sw75]    # placement + tracks/vias from the .ses -> station_board[_pf|_sw75].kicad_pcb
Run with KiCad's python from pcb/station_board/.
"""
import os, sys
import pcbnew

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from kicad_ses import import_ses  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PF = 'pf' in sys.argv[1:]
SW75 = 'sw75' in sys.argv[1:]
SW130 = 'sw130' in sys.argv[1:]
REV = 'r12'
NAME = ('station_board_pf' if PF else 'station_board_sw75' if SW75 else 'station_board_sw130' if SW130
        else 'station_board')
SES = f'{NAME}.ses' if SW75 or SW130 else 'station_board.ses'
FP = '/usr/share/kicad/footprints/'
OX, OY = 100.0, 100.0
mm = pcbnew.FromMM

# outline (board coords): the VoiceS3R and, beside it on -x, the DB9 on the -y edge (the station's back wall)
X0, X1, Y0, Y1 = -48.0, 12.0, -11.0, 24.0
J3_EDGE = Y1                 # J3 stays on the 60 × 35 front edge in both outlines
DB9_BX = -27.9               # DB9 centre (r10: -31.9)
# pf: holes in board coords, all outside the 60 × 35 area's tracks. The same lists are in station/build_station_pf.py
# (case coords there: x = -6.0 - x_board, y = -26.7 + y_board), keep the two together.
HOLES = []                   # M3, module spacers
BOSSES = []                  # M2.3 screw into a TPS-M2.3-7 on the case's PCB boss (±43.5, ±23.5 in case coords)
if PF:
    X0, X1, Y1 = -52.0, 40.0, 60.0          # case x -46..46: clear of the corner screw bosses (|x| >= 46.3)
    HOLES = [(27.0, 17.5), (14.9, 17.5), (27.0, 55.5), (14.9, 55.5),    # H1..H4 under the Unit NFC's corners
             (5.2, 27.5), (-43.8, 27.5), (5.2, 42.5), (-43.8, 42.5)]    # H5..H8 under the vein module's corners
    BOSSES = [(37.5, 3.2), (-49.5, 3.2), (37.5, 50.2), (-49.5, 50.2)]
POS = {}                     # sw75: ref -> (x, y, rot), overriding the places below
DB9_ROT, DB9_BY = 0, 0.0     # sw75: the DB9 turned to the +x edge at y = DB9_BY
EDGE = None                  # sw75: the outline as a polygon
NOTCH = None                 # sw75: (x0, x1, depth) cut into the -y edge for the vein cable (not in the DSN)
if SW75:
    X0, X1, Y0, Y1 = -20.4, 20.4, -33.8, 34.3
    AX, AY = 0.0, 50.0                         # VoiceS3R centre: out past the +y end wall (outside 37.5), 0.5 clear
    TX, TY = 13.0, 62.0                        # the tongue: |x| <= TX, out to y = TY
    NOTCH = (-12.0, -6.0, 2.5)
    DB9_ROT, DB9_BY = 90, 0.0
    HOLES = [(-6.3, -15.0), (1.2, -19.5), (-10.9, 20.5), (1.3, 20.5),     # H1..H4 vein spacers (as the ESP sw75)
             (0.0, 55.0)]                                                  # H5 the tongue's foot, under the VoiceS3R
    # turned half a turn (USB-C / PORT.A to +y): case x = AX - x_vb, y = AY - y_vb; J1 / J2 pin 1 at y_vb = 2.54 / 0
    POS = {'J1': (AX - 7.62, AY - 2.54, 180), 'J2': (AX + 7.62, AY, 180),
           'J3': (-8.35, -22.5, 0),              # under the vein socket, opening -y like it (one C loop of cable)
           'U1': (-12.5, 2.0, 0), 'C1': (-8.0, 6.5, 90), 'C2': (-8.0, 3.0, 90), 'C3': (-8.0, -0.5, 90),
           'C4': (-8.0, -4.0, 90), 'C5': (-16.5, 8.5, 0),
           'SW1': (13.0, 25.5, 90)}             # above the DB9, under the cover (not under the vein module)
    EDGE = [(X0, Y0), (X1, Y0), (X1, Y1), (TX, Y1), (TX, TY), (-TX, TY), (-TX, Y1), (X0, Y1)]
if SW130:
    X0, X1, Y0, Y1 = -17.4, 17.4, -61.7, 61.0     # inside 35.5 × 125.5 at the floor; DB9 flange on Y0, 0.05 off the wall
    DB9_BX = 0.0
    AX, AY = 0.0, 49.2                          # VoiceS3R centre (its +y face 61.2, 0.2 inside the cover's skirt)
    HOLES = [(-9.0, -26.0), (9.0, -26.0), (-9.0, 9.0), (9.0, 9.0),      # H1..H4 under the vein module (y -30..29)
             (0.0, 54.2), (-13.8, -18.0), (14.0, -34.0)]                # H5 under the VoiceS3R, H6 / H7 to the edges
    POS = {'J1': (AX - 7.62, AY - 2.54, 180), 'J2': (AX + 7.62, AY, 180),   # half a turn: USB-C / PORT.A to +y
           'J3': (-0.15, -34.5, 0),             # in front of the vein socket, opening -y (the spare cable beside it)
           'J6': (X0 + 4.45 + 2.3, -45.0, 270),   # Grove for the Unit NFC, opening -x, between the DB9 and the vein
           'R1': (-3.5, -48.5, 90), 'R2': (-1.7, -48.5, 90),
           'U1': (-8.0, 26.0, 90), 'C1': (-12.5, 20.3, 0), 'C2': (-9.5, 20.3, 0), 'C3': (-6.5, 20.3, 0),
           'C4': (-3.5, 20.3, 0), 'C5': (-8.0, 31.8, 0),
           'SW1': (11.3, -44.3, 0)}             # between the vein module and the DB9, clear of it: cover off to set


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
for n in ['3V3', 'GND', '5V', 'G5', 'G6', 'G7', 'G8', 'G38', 'G39',
          'C1P', 'C1N', 'C2P', 'C2N', 'VP', 'VN', 'TXO', 'RXI', 'D2', 'D3']:
    ni = pcbnew.NETINFO_ITEM(b, n); b.Add(ni); nets[n] = ni

LIBS = {}


def load(lib, name, ref, value, x, y, rot=0, flip=False):
    fp = pcbnew.FootprintLoad(FP + lib, name)
    nick = lib.removesuffix('.pretty'); LIBS[nick] = FP + lib
    fp.SetFPID(pcbnew.LIB_ID(nick, name))
    fp.SetReference(ref); fp.SetValue(value)
    b.Add(fp)
    if ref in POS:
        x, y, rot = POS[ref]
    fp.SetPosition(P(x, y))
    if flip:
        fp.Flip(fp.GetPosition(), False)
    fp.SetOrientationDegrees(rot)
    return fp


def wire(fp, table):
    for p in fp.Pads():
        n = table.get(p.GetNumber())
        if n:
            p.SetNet(nets[n])


# ---- VoiceS3R Ext.Pin (J1 x=+7.62: 3V3,G5,G6,G7,G8 from y=+2.54 down / J2 x=-7.62: G39,G38,5V,GND from y=0 down)
J1 = load('Connector_PinHeader_2.54mm.pretty', 'PinHeader_1x05_P2.54mm_Vertical', 'J1', 'Hdr 1x5 (3V3,G5,G6,G7,G8)', 7.62, 2.54)
wire(J1, {'1': '3V3', '2': 'G5', '3': 'G6', '4': 'G7', '5': 'G8'})
J2 = load('Connector_PinHeader_2.54mm.pretty', 'PinHeader_1x04_P2.54mm_Vertical', 'J2', 'Hdr 1x4 (G39,G38,5V,GND)', -7.62, 0)
wire(J2, {'1': 'G39', '2': 'G38', '3': '5V', '4': 'GND'})

# ---- J3 finger vein, on the +y edge (the station's front), opening towards the vein module
J3 = load('Connector_Molex.pretty', 'Molex_PicoBlade_53261-0471_1x04-1MP_P1.25mm_Horizontal', 'J3',
          'MX1.25-4P RA (Molex 53261-0471)', -30.0, J3_EDGE - 3.1, rot=180)
wire(J3, {'1': 'G5', '2': 'G6', '3': '3V3', '4': 'GND', 'MP': 'GND'})

# ---- MAX3232 + charge pump caps (0.1 uF at 3.3 V)
U1 = load('Package_SO.pretty', 'SOIC-16_3.9x9.9mm_P1.27mm', 'U1', 'MAX3232', -26.0, 5.0, rot=90)
wire(U1, {'1': 'C1P', '2': 'VP', '3': 'C1N', '4': 'C2P', '5': 'C2N', '6': 'VN', '10': 'GND',
          '11': 'G7', '12': 'G8', '13': 'RXI', '14': 'TXO', '15': 'GND', '16': '3V3'})
CAPS = [('C1', 'C1P', 'C1N', -20.0, 11.0, 0), ('C2', 'C2P', 'C2N', -23.5, 11.0, 0),
        ('C3', 'VP', 'GND', -27.0, 11.0, 0), ('C4', 'VN', 'GND', -30.5, 11.0, 0), ('C5', '3V3', 'GND', -18.5, 5.0, 90)]
for ref, a, c, x, y, r in CAPS:
    cp = load('Capacitor_SMD.pretty', 'C_0603_1608Metric', ref, '100nF', x, y, rot=r)
    wire(cp, {'1': a, '2': c})

# ---- straight / cross DIP
SW1 = load('Button_Switch_SMD.pretty', 'SW_DIP_SPSTx04_Slide_6.7x11.72mm_W8.61mm_P2.54mm_LowProfile', 'SW1',
           'DIP4 (1+2 straight / 3+4 cross)', -41.2, 6.3, rot=0)
wire(SW1, {'1': 'TXO', '8': 'D3', '2': 'RXI', '7': 'D2', '3': 'TXO', '6': 'D2', '4': 'RXI', '5': 'D3'})

# ---- DB9 male right angle on the -y edge; its flange sits on the board edge
J4 = load('Connector_Dsub.pretty', 'DSUB-9_Male_Horizontal_P2.77x2.84mm_EdgePinOffset7.70mm_Housed_MountingHolesOffset9.12mm',
          'J4', 'DB9 male RA (to FC-1200)', 0, 0, rot=0)
# local +y (towards the mating face) points to board -y; put the pin-1 row 7.70 inside the edge, centre at DB9_BX
p1 = [p for p in J4.Pads() if p.GetNumber() == '1'][0]
px, py = xy(p1.GetPosition())
if DB9_ROT == 90:      # sw75: mating face to +x, the pin row along +y, pin 1 7.70 in from the +x edge
    J4.SetOrientationDegrees(90); px, py = xy(p1.GetPosition())
    J4.Move(pcbnew.VECTOR2I(mm((X1 - 7.70) - px), -mm((DB9_BY - 5.54) - py)))
else:
    J4.Move(pcbnew.VECTOR2I(mm((DB9_BX - 5.54) - px), -mm((Y0 + 7.70) - py)))
wire(J4, {'2': 'D2', '3': 'D3', '5': 'GND', '0': 'GND'})
print('J4 pin1', xy(p1.GetPosition()), 'pin5', xy([p for p in J4.Pads() if p.GetNumber() == '5'][0].GetPosition()))

# ---- sw130: Grove for the Unit NFC on G38 (SDA) / G39 (SCL), with pull-ups
if SW130:
    J6 = load('Connector_JST.pretty', 'JST_PH_S4B-PH-SM4-TB_1x04-1MP_P2.00mm_Horizontal', 'J6',
              'Grove HY2.0-4P RA (NFC: G38 SDA, G39 SCL)', 0, 0)
    wire(J6, {'1': 'G38', '2': 'G39', '3': '5V', '4': 'GND', 'MP': 'GND'})
    for ref, n in (('R1', 'G38'), ('R2', 'G39')):
        wire(load('Resistor_SMD.pretty', 'R_0603_1608Metric', ref, '4.7k', 0, 0), {'1': '3V3', '2': n})

# ---- pf: M3 holes for the hex spacers (non-plated, no pad) and the M2.3 holes over the case's bosses
for i, (x, y) in enumerate(HOLES, 1):
    load('MountingHole.pretty', 'MountingHole_3.2mm_M3', f'H{i}', 'M3 spacer', x, y)
for x, y in BOSSES:
    c = pcbnew.PCB_SHAPE(b); c.SetShape(pcbnew.SHAPE_T_CIRCLE)
    c.SetCenter(P(x, y)); c.SetEnd(P(x + 1.3, y)); c.SetLayer(pcbnew.Edge_Cuts); c.SetWidth(mm(0.1)); b.Add(c)

# ---- outline (sw75: with the tongue, and the -y notch except in the DSN, where it kept the routing from passing)
EDGE = EDGE or [(X0, Y0), (X1, Y0), (X1, Y1), (X0, Y1)]
if NOTCH and 'dsn' not in sys.argv[1:]:
    nx0, nx1, nd = NOTCH
    EDGE = [(X0, Y0), (nx0, Y0), (nx0, Y0 + nd), (nx1, Y0 + nd), (nx1, Y0)] + EDGE[1:]
for (a, c), (d, e) in zip(EDGE, EDGE[1:] + EDGE[:1]):
    s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(P(a, c)); s.SetEnd(P(d, e)); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.1)); b.Add(s)


def text(s, x, y, layer=pcbnew.F_SilkS, size=1.0, rot=0):
    t = pcbnew.PCB_TEXT(b); t.SetText(s); t.SetPosition(P(x, y)); t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size))); t.SetTextThickness(mm(0.15))
    t.SetTextAngleDegrees(rot)
    if layer == pcbnew.B_SilkS:
        t.SetMirrored(True)
    b.Add(t)


if SW75:
    text('VoiceS3R: USB-C / PORT.A this way', 0.0, TY - 1.2, size=0.8)
    text('SW1 1+2 PASS / 3+4 CROSS', 13.0, 31.5, size=0.8)
    text('J3 vein: 1RX 2TX 3V3 4G', -8.35, -17.6, size=0.8)
    text(f'vein-station board {REV} (SW-75B)', -6.0, 0.0, layer=pcbnew.B_SilkS)
elif SW130:
    text('VoiceS3R: USB-C / PORT.A this way', 0.0, Y1 - 1.2, size=0.8)
    text('SW1 12=PASS 34=CROSS', 3.0, -44.3, size=0.8, rot=90)
    text('J3 vein: 1RX 2TX 3V3 4G', -0.15, -29.8, size=0.8)
    text('NFC: G38 G39 5V G', -9.0, -52.0, size=0.8)
    text(f'vein-station board {REV}b (SW-130B)', 0.0, 0.0, layer=pcbnew.B_SilkS)
else:
    text('USB-C / PORT.A side', 0, -13.2, size=0.8)
    text('SW1 1+2 PASS(FC-1200) / 3+4 CROSS', -41.2, 14.0, size=0.8)
    text('J3 vein: 1RX 2TX 3V3 4G', -30.0, 16.2, size=0.8)
    text(f'vein-station board {REV}' + (' (PF13-4-9)' if PF else ''), -20.0, 18.0, layer=pcbnew.B_SilkS)

os.chdir(HERE)
if 'dsn' in sys.argv[1:]:
    b.Save(f'{NAME}.kicad_pcb')
    print('dsn', pcbnew.ExportSpecctraDSN(b, f'{NAME}.dsn'))
else:
    import_ses(b, nets, SES)
    b.Save(f'{NAME}.kicad_pcb')
    # GND pour on B.Cu over the whole board (stitches the GND tracks, shields the RS232 lines).
    # Filled on a reloaded board: the filler crashes on a board built in memory without a connectivity graph.
    b = pcbnew.LoadBoard(f'{NAME}.kicad_pcb')
    z = pcbnew.ZONE(b); z.SetLayer(pcbnew.B_Cu); z.SetNet(b.FindNet('GND'))
    ol = z.Outline(); ol.NewOutline()
    YT = TY if SW75 else Y1      # the fill is clipped to the outline (the sw75 tongue and notch)
    for x, y in ((X0 + 0.3, Y0 + 0.3), (X1 - 0.3, Y0 + 0.3), (X1 - 0.3, YT - 0.3), (X0 + 0.3, YT - 0.3)):
        ol.Append(mm(OX + x), mm(OY - y))
    z.SetLocalClearance(mm(0.3)); z.SetMinThickness(mm(0.25))
    b.Add(z)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    b.Save(f'{NAME}.kicad_pcb')
LIBS['MountingHole'] = FP + 'MountingHole.pretty'   # the table is shared by all outlines
for lib in ('Connector_JST', 'Resistor_SMD'):         # sw130's J6 / R1 / R2
    LIBS[lib] = FP + lib + '.pretty'
with open('fp-lib-table', 'w') as f:
    f.write('(fp_lib_table\n  (version 7)\n')
    for nick, uri in sorted(LIBS.items()):
        f.write(f'  (lib (name "{nick}")(type "KiCad")(uri "{uri}")(options "")(descr ""))\n')
    f.write(')\n')
for fp in b.GetFootprints():
    bb = fp.GetBoundingBox(False, False)
    print(f'{fp.GetReference():4s}', xy(fp.GetPosition()), 'bbox x', round(pcbnew.ToMM(bb.GetLeft()) - OX, 2),
          round(pcbnew.ToMM(bb.GetRight()) - OX, 2), 'y', round(OY - pcbnew.ToMM(bb.GetBottom()), 2),
          round(OY - pcbnew.ToMM(bb.GetTop()), 2))
print('saved')
