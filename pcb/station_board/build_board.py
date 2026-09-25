"""Vein Station board (r10): one PCB under the VoiceS3R that carries everything the station needs.
  - J1/J2: VoiceS3R Ext.Pin (same positions as vein-base v0.6)
  - J3: finger vein module, MX1.25 4P (G5 -> module RXD, G6 <- module TXD, 3V3, GND; same pin order as vein-base)
  - U1 MAX3232 (3.3 V) + C1..C5: G7 -> T1IN, R1OUT -> G8 (UART to the FC-1200 alcohol checker, 9600 8N1)
  - SW1 4-way DIP: straight / cross of DB9 pins 2 and 3
        SW1-1 TX -> DB9-3, SW1-2 RX <- DB9-2   (passthrough: 1+2 ON, the same as a PC. The FC-1200 works
                                                 with the RS232M Module 13.2 switch on passthrough, so ship 1+2 ON)
        SW1-3 TX -> DB9-2, SW1-4 RX <- DB9-3   (cross:    3+4 ON)
  - J4: DB9 male, right angle (the same gender as the RS232M Module 13.2), on the -y edge next to the VoiceS3R, so
        the DB9 and the VoiceS3R's USB-C both leave through the station's back wall (pin 5 = GND, shell = GND)
Board coords are vein-base's: origin = Atom centre, +y = away from the USB-C / PORT.A edge, F faces the Atom.
The station turns the board 180° (USB-C side to the back): x_st = VX - x, ys_st = VYS + y (station/build_station.py).

Two outlines of the same circuit (same parts, same routing):
  r10            60 × 35, for the printed enclosure (station/build_station.py) -> station_board.kicad_pcb
  r11 ('pf')     86 × 63.8, for the Takachi PF13-4-9 off-the-shelf case -> station_board_pf.kicad_pcb.
                 The outline grows under the Unit NFC (+x) and the vein module (+y) only, so the r10 area and its
                 tracks stay as they are. Nine M3 holes (H1..H9) carry stock hex spacers instead of printed parts:
                 floor -> board 12 mm (H1 H3 H7 H8 H9), board -> NFC 7 mm (H1..H4), board -> vein 6 mm (H5..H8).
                 A floor spacer and a module spacer share a hole where both are listed (male-female through it).

Routing comes from freerouting and is kept in station_board.ses (the board file itself is always generated):
    python3 build_board.py dsn     # placement only -> station_board.dsn (feed it to freerouting -> .ses)
    python3 build_board.py [pf]    # placement + tracks/vias from station_board.ses -> station_board[_pf].kicad_pcb
Run with KiCad's python from pcb/station_board/.
"""
import os, re, sys
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
PF = 'pf' in sys.argv[1:]
REV = 'r11' if PF else 'r10'
NAME = 'station_board_pf' if PF else 'station_board'
FP = '/usr/share/kicad/footprints/'
OX, OY = 100.0, 100.0
mm = pcbnew.FromMM

# outline (board coords): the VoiceS3R and, beside it on -x, the DB9 on the -y edge (the station's back wall)
X0, X1, Y0, Y1 = -48.0, 12.0, -11.0, 24.0
J3_EDGE = Y1                 # J3 stays on the r10 front edge in both outlines
# r11: M3 holes in board coords, all outside the r10 area (>= 5.5 from its tracks). The same list is in
# station/build_station_pf.py (case coords there: x = -6.0 - x_board, y = -26.7 + y_board), keep the two together.
HOLES = []
if PF:
    X1, Y1 = 38.0, 52.8
    HOLES = [(32.5, -6.3), (16.5, -6.3), (32.5, 31.7), (16.5, 31.7),    # H1..H4 under the Unit NFC's corners
             (8.0, 32.1), (-43.0, 32.1), (8.0, 48.1), (-43.0, 48.1),    # H5..H8 under the vein module's corners
             (-44.5, 16.5)]                                            # H9 beside the DB9


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
# local +y (towards the mating face) points to board -y; put the pin-1 row 7.70 inside the edge, centre at x=-31.9
p1 = [p for p in J4.Pads() if p.GetNumber() == '1'][0]
px, py = xy(p1.GetPosition())
J4.Move(pcbnew.VECTOR2I(mm((-31.9 - 5.54) - px), -mm((Y0 + 7.70) - py)))
wire(J4, {'2': 'D2', '3': 'D3', '5': 'GND', '0': 'GND'})
print('J4 pin1', xy(p1.GetPosition()), 'pin5', xy([p for p in J4.Pads() if p.GetNumber() == '5'][0].GetPosition()))

# ---- r11: M3 holes for the hex spacers (non-plated, no pad)
for i, (x, y) in enumerate(HOLES, 1):
    load('MountingHole.pretty', 'MountingHole_3.2mm_M3', f'H{i}', 'M3 spacer', x, y)

# ---- outline
for (a, c), (d, e) in [((X0, Y0), (X1, Y0)), ((X1, Y0), (X1, Y1)), ((X1, Y1), (X0, Y1)), ((X0, Y1), (X0, Y0))]:
    s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(P(a, c)); s.SetEnd(P(d, e)); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.1)); b.Add(s)


def text(s, x, y, layer=pcbnew.F_SilkS, size=1.0, rot=0):
    t = pcbnew.PCB_TEXT(b); t.SetText(s); t.SetPosition(P(x, y)); t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size))); t.SetTextThickness(mm(0.15))
    t.SetTextAngleDegrees(rot)
    if layer == pcbnew.B_SilkS:
        t.SetMirrored(True)
    b.Add(t)


text('USB-C / PORT.A side', 0, -13.2, size=0.8)
text('SW1 1+2 PASS(FC-1200) / 3+4 CROSS', -41.2, 14.0, size=0.8)
text('J3 vein: 1RX 2TX 3V3 4G', -30.0, 16.2, size=0.8)
text(f'vein-station board {REV}' + (' (PF13-4-9)' if PF else ''), -20.0, 18.0, layer=pcbnew.B_SilkS)

# ---- routing (freerouting session file)
LAY = {'F.Cu': pcbnew.F_Cu, 'B.Cu': pcbnew.B_Cu}


def sexp(text):
    """Parse an s-expression into nested lists of strings (quoted strings lose their quotes)."""
    stack, cur = [], []
    for tok in re.findall(r'"[^"]*"|\(|\)|[^\s()]+', text):
        if tok == '(':
            stack.append(cur); cur = []
        elif tok == ')':
            done = cur; cur = stack.pop(); cur.append(done)
        else:
            cur.append(tok.strip('"'))
    return cur[0]


def find(node, key):
    for c in node:
        if isinstance(c, list) and c and c[0] == key:
            yield c


def import_ses(path):
    """Add the wires and vias of a Specctra session file (freerouting output) to the board."""
    ses = sexp(open(path).read())
    route = next(find(ses, 'routes'))
    unit, res = next(find(route, 'resolution'))[1:3]
    k = {'um': 0.001, 'mm': 1.0, 'mil': 0.0254, 'inch': 25.4}[unit] / int(res)
    n_w = n_v = 0
    for net in find(next(find(route, 'network_out')), 'net'):
        ni = nets[net[1]]
        for w in find(net, 'wire'):
            path = next(find(w, 'path'))
            lay, width, c = path[1], float(path[2]) * k, [float(v) * k for v in path[3:]]
            pts = list(zip(c[0::2], c[1::2]))
            for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
                t = pcbnew.PCB_TRACK(b)
                t.SetStart(pcbnew.VECTOR2I(mm(x1), mm(-y1))); t.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(-y2)))
                t.SetWidth(mm(width)); t.SetLayer(LAY[lay]); t.SetNet(ni); b.Add(t); n_w += 1
        for v in find(net, 'via'):
            x, y = float(v[2]) * k, float(v[3]) * k
            via = pcbnew.PCB_VIA(b); via.SetPosition(pcbnew.VECTOR2I(mm(x), mm(-y)))
            via.SetWidth(mm(0.6)); via.SetDrill(mm(0.3)); via.SetNet(ni); b.Add(via); n_v += 1
    print(f'ses: {n_w} track segments, {n_v} vias')


os.chdir(HERE)
if len(sys.argv) > 1 and sys.argv[1] == 'dsn':
    b.Save(f'{NAME}.kicad_pcb')
    print('dsn', pcbnew.ExportSpecctraDSN(b, f'{NAME}.dsn'))
else:
    import_ses('station_board.ses')
    b.Save(f'{NAME}.kicad_pcb')
    # GND pour on B.Cu over the whole board (stitches the GND tracks, shields the RS232 lines).
    # Filled on a reloaded board: the filler crashes on a board built in memory without a connectivity graph.
    b = pcbnew.LoadBoard(f'{NAME}.kicad_pcb')
    z = pcbnew.ZONE(b); z.SetLayer(pcbnew.B_Cu); z.SetNet(b.FindNet('GND'))
    ol = z.Outline(); ol.NewOutline()
    for x, y in ((X0 + 0.3, Y0 + 0.3), (X1 - 0.3, Y0 + 0.3), (X1 - 0.3, Y1 - 0.3), (X0 + 0.3, Y1 - 0.3)):
        ol.Append(mm(OX + x), mm(OY - y))
    z.SetLocalClearance(mm(0.3)); z.SetMinThickness(mm(0.25))
    b.Add(z)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    b.Save(f'{NAME}.kicad_pcb')
LIBS['MountingHole'] = FP + 'MountingHole.pretty'   # the table is shared by both outlines
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
