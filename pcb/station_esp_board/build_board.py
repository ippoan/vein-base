"""Vein Station ESP board (e1): the station board with the Atom VoiceS3R's circuit on the board itself instead of the
Atom on the Ext.Pin, in two outlines of the same circuit:
  (default)  92 × 71 for the Takachi PF13-4-9 (the pf outline of pcb/station_board, same holes / DB9 / MAX3232 / DIP / J3)
  'sw'       52 × 76 for the Takachi SW-85B (station/build_station_sw.py): every part placed anew (POS), the vein module
             and the Unit NFC on M3 spacers from the board, the board on three Takachi ASL-12 stuck to the floor
The circuit follows M5Stack's schematics (Sch_M5_AtomS3R_v0.4.1 / Sch_M5_AtomEchoS3R_Audio_v1.0_20250716) with the
same GPIOs, so VoiceS3R firmware keeps working:
  - U2 ESP32-S3-WROOM-1-N8R8 (the VoiceS3R's ESP32-S3-PICO-1 has the same 8 MB flash + 8 MB octal PSRAM; the
        module brings its own antenna and radio certification). Antenna out over the -y edge (the open back), 1.0
        past it, its keep-out (the footprint's rule area) clear of copper.
  - J5 USB-C (native USB, G19 = D-, G20 = D+ through 22 Ω, CC1/CC2 5.1 k), U3 AMS1117-3.3 (5 V -> 3.3 V),
        SW2 = EN (reset, 10 k / 1 µF), SW3 = BOOT (G0 to GND)
  - U4 ES8311 codec on I2C (SDA G45, SCL G0, 4.7 k pull-ups, CE low = 0x18) and I2S (MCLK G11, BCLK G17, WS G3,
        G48 -> DSDIN, ASDOUT -> G4), MK1 analog MEMS mic (LinkMems LMA3729T381, top port; the VoiceS3R's
        MSM381A3729H9BPC is out of stock) into MIC1P, MIC1N to GND through 1 µF, mic supply through FB1
  - U5 NS4150B class-D amp on 3V3 (as the VoiceS3R), CTRL = G18 (10 k pull-down), inputs from OUTP / OUTN through
        100 nF + 150 k, SP1 13 × 13 SMD speaker (GSPK1304S 8 Ω 0.5 W) on the board
  - J6 Grove (HY2.0 4P RA) for the Unit NFC: 1 = G2 (SDA), 2 = G1 (SCL), 3 = 5V, 4 = GND (the VoiceS3R's PORT.A);
        J7 Grove beside it, spare: 1 = G38, 2 = G39, 3 = 5V, 4 = GND (the two GPIOs the VoiceS3R's Ext.Pin had)
  - no IR LED (G47 unused), no user button (G41 unused)
  - the rest as station_board r12 pf, in the same places: J3 vein (G5 -> RXD, G6 <- TXD), U1 MAX3232 (G7 -> T1IN,
        R1OUT -> G8), SW1 DIP (1+2 pass / 3+4 cross), J4 DB9 male RA on the -y edge, H1..H8 M3 module spacers,
        B1..B4 M2.3 over the case's PCB bosses
GPIO45 is the VDD_SPI strap and the SDA pull-up holds it high at reset: burn the flash voltage eFuse once before the
first boot (hold BOOT, tap EN, then `espefuse.py --port <port> set_flash_voltage 3.3V`), as the WROOM-1's flash is 3.3 V.
M5Unified detects the VoiceS3R by the PICO-1 package, so set cfg.fallback_board = board_M5AtomVoiceS3R (or configure
the codec yourself).

Board coords are the station board's (origin = where the VoiceS3R stood, +y = away from the back edge, F up).
The speaker and the mic sit under the PF case's old VoiceS3R window (|x|, |y| <= 10.8 in these coords).
In 'sw' the coords are the SW-85B case's instead (origin = case centre, the DB9 / USB-C end = -y); the speaker and
the mic sit in front of the NFC under holes in the cover, the WROOM's antenna on the front edge.
Routing comes from freerouting and is kept in station_esp_board[_sw].ses (the board file itself is always generated):
    python3 build_board.py [sw] dsn   # placement only -> .dsn (freerouting 2.4.1 -> .ses)
    python3 build_board.py [sw]       # placement + tracks/vias from the .ses -> station_esp_board[_sw].kicad_pcb
Run with KiCad's python from pcb/station_esp_board/.
"""
import math, os, re, sys
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from kicad_ses import import_ses  # noqa: E402

SW = 'sw' in sys.argv[1:]
REV = 'e1'
NAME = 'station_esp_board_sw' if SW else 'station_esp_board'
FP = '/usr/share/kicad/footprints/'
LOCAL = os.path.join(HERE, '..') + '/'         # pcb/vein_base.pretty (the project's own footprints)
OX, OY = 100.0, 100.0
mm = pcbnew.FromMM

# the pf outline and holes of pcb/station_board (keep them together, station/build_station_pf.py has them too)
X0, X1, Y0, Y1 = -52.0, 40.0, -11.0, 60.0
J3_EDGE = 24.0
DB9_BX = -27.9
HOLES = [(27.0, 17.5), (14.9, 17.5), (27.0, 55.5), (14.9, 55.5),
         (5.2, 27.5), (-43.8, 27.5), (5.2, 42.5), (-43.8, 42.5)]
BOSSES = [(37.5, 3.2), (-49.5, 3.2), (37.5, 50.2), (-49.5, 50.2)]
WX, WY = 24.0, 0.5             # WROOM centre: antenna end at y = -12.25 (1.25 past the edge; its courtyard stays
                               # clear of the H1 / H2 spacers)
UX = -5.5                      # USB-C centre, clear of the antenna keep-out (x >= WX - 24)
ASL = []                       # sw: Takachi ASL-12 stick-on snap spacers under the board (3.0 holes)
POS = {}                       # sw: ref -> (x, y, rot), overriding the pf places below
if SW:
    # Takachi SW-85B (60 x 40 x 85, inside 52.8 x 77.8 x 32.7): board coords = case coords seen from above, origin =
    # case centre, the DB9 / USB-C end = -y. The same lists are in station/build_station_sw.py (keep them together).
    X0, X1, Y0, Y1 = -26.0, 26.0, -38.0, 38.0
    DB9_BX = -10.0
    UX = 12.5
    WX, WY = -14.0, 25.25      # WROOM, antenna to the +y edge (front, flush), under the front of the vein module
    HOLES = [(-22.5, -8.0), (-3.3, -8.0), (-22.5, 6.0), (-3.3, 6.0),         # H1..H4 vein module spacers (clear of
                                                                            # the J3 plug's run at y -18..-12)
             (6.5, -24.5), (22.5, -24.5), (21.2, 16.0)]                     # H5..H7 Unit NFC spacers (under it,
                                                                            # it only rests on them and is taped to
                                                                            # the cover; three, the codec's caps
                                                                            # take the fourth corner)
    BOSSES = []
    ASL = [(-8.0, -13.5), (-10.0, 8.5), (0.5, 12.5)]                        # between the floor ribs (|x| <= 10.5)
    POS = {'J3': (-20.0, -21.0, 180), 'U1': (-7.5, -21.0, 90),
           'C1': (-12.0, -26.6, 0), 'C2': (-8.5, -26.6, 0), 'C3': (-5.0, -26.6, 0), 'C4': (-1.5, -26.6, 0),
           'C5': (0.8, -24.6, 0), 'SW1': (-12.9, -3.0, 0),
           'U2': (WX, WY, 0), 'C9': (-2.9, 17.0, 90), 'C10': (-25.0, 27.0, 90), 'R5': (-25.0, 23.5, 90),
           'C11': (-25.0, 20.0, 90), 'SW2': (23.2, 4.8, 90), 'SW3': (23.2, -4.4, 90),
           'R1': (19.8, -35.2, 0), 'R2': (23.2, -35.2, 0), 'R3': (19.8, -32.0, 0), 'R4': (23.2, -32.0, 0),
           'U3': (4.5, -15.0, 90), 'C6': (2.5, -7.8, 0), 'C7': (4.3, -4.9, 0), 'C8': (1.0, -4.9, 0),
           'MK1': (7.8, 29.6, 0), 'FB1': (2.5, 28.5, 90), 'C20': (10.3, 28.5, 90), 'C21': (0.5, 28.5, 90),
           # ES8311 turned 270: I2S (6..9) to -x (the WROOM), OUTP / OUTN (12, 13) to -y (the amp), mic pins to +x
           'U4': (4.0, 21.5, 270), 'C12': (3.5, 25.3, 0), 'C13': (6.9, 25.2, 90), 'C14': (2.4, 17.4, 90),
           'C15': (8.2, 21.0, 0), 'C16': (7.1, 17.2, 90), 'C17': (5.4, 17.2, 90), 'C18': (8.2, 22.8, 0),
           'C19': (0.2, 21.5, 90), 'R6': (-3.3, 27.5, 90), 'R7': (-1.6, 30.3, 90),
           'U5': (15.2, 16.0, 90), 'C22': (11.2, 20.6, 0), 'C23': (14.3, 20.6, 0), 'C24': (17.4, 20.6, 0),
           'C25': (20.6, 20.6, 0), 'C26': (23.8, 20.6, 0), 'R8': (11.2, 22.6, 0), 'R9': (14.4, 22.6, 0),
           'R10': (17.6, 22.6, 0), 'SP1': (18.5, 30.5, 0), 'J6': (15.5, -13.3, 180), 'J7': (12.8, 2.5, 180)}   # plugs out to +y


def P(x, y):
    return pcbnew.VECTOR2I(mm(OX + x), mm(OY - y))


def xy(v):
    return (round(pcbnew.ToMM(v.x) - OX, 3), round(OY - pcbnew.ToMM(v.y), 3))


b = pcbnew.BOARD()
ds = b.GetDesignSettings()
ds.SetCopperLayerCount(2)
ds.SetBoardThickness(mm(1.6))
nc = ds.m_NetSettings.m_DefaultNetClass
nc.SetClearance(mm(0.15)); nc.SetTrackWidth(mm(0.2));  # 0.2 / 0.15 fits the ES8311's 0.4 pitch
nc.SetViaDiameter(mm(0.6)); nc.SetViaDrill(mm(0.3))

nets = {}
for n in ['GND', '5V', '3V3', 'G5', 'G6', 'G7', 'G8', 'C1P', 'C1N', 'C2P', 'C2N', 'VP', 'VN', 'TXO', 'RXI', 'D2', 'D3',
          'CC1', 'CC2', 'UDP', 'UDN', 'G19', 'G20', 'EN', 'G0', 'G45', 'G11', 'G17', 'G3', 'G48', 'G4', 'G18',
          'G1', 'G2', 'G38', 'G39', 'MICV', 'MICO', 'MIC1P', 'MIC1N', 'VMID', 'ADCREF', 'DACREF', 'OUTP', 'OUTN',
          'AIP', 'AIN', 'INP', 'INN', 'BYP', 'SPKP', 'SPKN']:
    ni = pcbnew.NETINFO_ITEM(b, n); b.Add(ni); nets[n] = ni

LIBS = {}


def load(lib, name, ref, value, x, y, rot=0, local=False):
    fp = pcbnew.FootprintLoad((LOCAL if local else FP) + lib, name)
    nick = lib.removesuffix('.pretty'); LIBS[nick] = ('${KIPRJMOD}/../' if local else FP) + lib
    fp.SetFPID(pcbnew.LIB_ID(nick, name))
    fp.SetReference(ref); fp.SetValue(value)
    b.Add(fp)
    if ref in POS:
        x, y, rot = POS[ref]
    fp.SetPosition(P(x, y))
    fp.SetOrientationDegrees(rot)
    return fp


def wire(fp, table):
    for p in fp.Pads():
        n = table.get(p.GetNumber())
        if n:
            p.SetNet(nets[n])


def two(lib, name, ref, value, a, c, x, y, rot=0):
    """A two-pad part (R / C / FB): pad 1 -> net a, pad 2 -> net c."""
    fp = load(lib, name, ref, value, x, y, rot)
    wire(fp, {'1': a, '2': c})
    return fp


def R(ref, value, a, c, x, y, rot=0):
    return two('Resistor_SMD.pretty', 'R_0603_1608Metric', ref, value, a, c, x, y, rot)


def C(ref, value, a, c, x, y, rot=0):
    size = '0805_2012' if value in ('10uF', '22uF') else '0603_1608'
    return two('Capacitor_SMD.pretty', f'C_{size}Metric', ref, value, a, c, x, y, rot)


# ======== kept from station_board r12 pf (same places) ========
J3 = load('Connector_Molex.pretty', 'Molex_PicoBlade_53261-0471_1x04-1MP_P1.25mm_Horizontal', 'J3',
          'MX1.25-4P RA (Molex 53261-0471)', -30.0, J3_EDGE - 3.1, rot=180)
wire(J3, {'1': 'G5', '2': 'G6', '3': '3V3', '4': 'GND', 'MP': 'GND'})
U1 = load('Package_SO.pretty', 'SOIC-16_3.9x9.9mm_P1.27mm', 'U1', 'MAX3232', -26.0, 5.0, rot=90)
wire(U1, {'1': 'C1P', '2': 'VP', '3': 'C1N', '4': 'C2P', '5': 'C2N', '6': 'VN', '10': 'GND',
          '11': 'G7', '12': 'G8', '13': 'RXI', '14': 'TXO', '15': 'GND', '16': '3V3'})
for ref, a, c, x, y, r in [('C1', 'C1P', 'C1N', -20.0, 11.0, 0), ('C2', 'C2P', 'C2N', -23.5, 11.0, 0),
                           ('C3', 'VP', 'GND', -27.0, 11.0, 0), ('C4', 'VN', 'GND', -30.5, 11.0, 0),
                           ('C5', '3V3', 'GND', -18.5, 5.0, 90)]:
    C(ref, '100nF', a, c, x, y, r)
SW1 = load('Button_Switch_SMD.pretty', 'SW_DIP_SPSTx04_Slide_6.7x11.72mm_W8.61mm_P2.54mm_LowProfile', 'SW1',
           'DIP4 (1+2 straight / 3+4 cross)', -41.2, 6.3)
wire(SW1, {'1': 'TXO', '8': 'D3', '2': 'RXI', '7': 'D2', '3': 'TXO', '6': 'D2', '4': 'RXI', '5': 'D3'})
J4 = load('Connector_Dsub.pretty', 'DSUB-9_Male_Horizontal_P2.77x2.84mm_EdgePinOffset7.70mm_Housed_MountingHolesOffset9.12mm',
          'J4', 'DB9 male RA (to FC-1200)', 0, 0)
p1 = [p for p in J4.Pads() if p.GetNumber() == '1'][0]
px, py = xy(p1.GetPosition())
J4.Move(pcbnew.VECTOR2I(mm((DB9_BX - 5.54) - px), -mm((Y0 + 7.70) - py)))
wire(J4, {'2': 'D2', '3': 'D3', '5': 'GND', '0': 'GND'})
for i, (x, y) in enumerate(HOLES, 1):
    load('MountingHole.pretty', 'MountingHole_3.2mm_M3', f'H{i}', 'M3 spacer', x, y)
for i, (x, y) in enumerate(ASL, 1):
    load('MountingHole.pretty', 'MountingHole_3mm', f'A{i}', 'ASL-12', x, y)

# ======== ESP32-S3 (WROOM-1: pins 1..14 on the +x side after the turn, 15..26 along +y, 27..40 on -x) ========
U2 = load('RF_Module.pretty', 'ESP32-S3-WROOM-1', 'U2', 'ESP32-S3-WROOM-1-N8R8', WX, WY, rot=180)
# the module's thermal vias (0.2 drill) are below JLC's 2-layer minimum: drop them for 0.3 vias placed below
for p in [p for p in U2.Pads() if p.GetNumber() == '41' and p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH]:
    U2.Remove(p)
wire(U2, {'1': 'GND', '40': 'GND', '41': 'GND', '2': '3V3', '3': 'EN', '13': 'G19', '14': 'G20',
          '27': 'G0', '26': 'G45', '19': 'G11', '10': 'G17', '15': 'G3', '25': 'G48', '4': 'G4', '11': 'G18',
          '39': 'G1', '38': 'G2', '31': 'G38', '32': 'G39', '5': 'G5', '6': 'G6', '7': 'G7', '12': 'G8'})
EPX, EPY = xy([p for p in U2.Pads() if p.GetNumber() == '41'][0].GetPosition())
for dx, dy in ((-1.0, -1.0), (1.0, -1.0), (-1.0, 1.0), (1.0, 1.0), (0.0, 0.0)):
    v = pcbnew.PCB_VIA(b); v.SetPosition(P(EPX + dx, EPY + dy)); v.SetWidth(mm(0.6)); v.SetDrill(mm(0.3))
    v.SetNet(nets['GND']); v.SetLocked(True); b.Add(v)
C('C9', '10uF', '3V3', 'GND', 13.0, 2.0, 90)
C('C10', '100nF', '3V3', 'GND', 35.0, -3.0, 90)             # at pin 2
R('R5', '10k', '3V3', 'EN', 36.9, -3.0, 90)
C('C11', '1uF', 'EN', 'GND', 38.8, -3.0, 90)
SW2 = load('Button_Switch_SMD.pretty', 'SW_Push_1P1T_XKB_TS-1187A', 'SW2', 'EN (reset)', 37.2, 11.5, rot=90)
wire(SW2, {'1': 'EN', '2': 'GND'})
SW3 = load('Button_Switch_SMD.pretty', 'SW_Push_1P1T_XKB_TS-1187A', 'SW3', 'BOOT (G0)', 37.2, 19.5, rot=90)
wire(SW3, {'1': 'G0', '2': 'GND'})

# ======== USB-C + 3.3 V ========
J5 = load('Connector_USB.pretty', 'USB_C_Receptacle_HRO_TYPE-C-31-M-12', 'J5', 'USB-C (TYPE-C-31-M-12)', UX, Y0 + 3.65 - 0.6)
wire(J5, {'A4': '5V', 'A9': '5V', 'B4': '5V', 'B9': '5V', 'A1': 'GND', 'A12': 'GND', 'B1': 'GND', 'B12': 'GND',
          'S1': 'GND', 'A5': 'CC1', 'B5': 'CC2', 'A6': 'UDP', 'B6': 'UDP', 'A7': 'UDN', 'B7': 'UDN'})
R('R1', '5.1k', 'CC1', 'GND', 1.5, -4.3)
R('R2', '5.1k', 'CC2', 'GND', 4.5, -4.3)
R('R3', '22', 'UDN', 'G19', 7.5, -4.3)
R('R4', '22', 'UDP', 'G20', 10.5, -4.3)
U3 = load('Package_TO_SOT_SMD.pretty', 'SOT-223-3_TabPin2', 'U3', 'AMS1117-3.3', -8.5, 3.0)
wire(U3, {'1': 'GND', '2': '3V3', '3': '5V'})
C('C6', '10uF', '5V', 'GND', -11.8, 7.9)
C('C7', '22uF', '3V3', 'GND', -15.2, 3.0, 90)
C('C8', '100nF', '3V3', 'GND', -15.2, 6.8, 90)

# ======== audio ========
MK1 = load('vein_base.pretty', 'MEMS_Mic_LinkMems_LMA3729T381_3.76x2.95mm', 'MK1', 'LMA3729T381-OAC03', -6.5, 9.8,
           local=True)
wire(MK1, {'1': 'MICV', '2': 'MICO', '3': 'GND', '4': 'GND'})
two('Inductor_SMD.pretty', 'L_0805_2012Metric', 'FB1', '100R@100MHz', '3V3', 'MICV', -10.2, 11.2, 90)
C('C20', '100nF', 'MICV', 'GND', -9.3, 13.8)
C('C21', '1uF', 'MICV', 'GND', -12.2, 11.5, 90)
U4 = load('Package_DFN_QFN.pretty', 'QFN-20-1EP_3x3mm_P0.4mm_EP1.65x1.65mm', 'U4', 'ES8311', -5.0, 19.0, rot=90)   # I2S pins (6..9) towards the WROOM
wire(U4, {'1': 'G0', '2': 'G11', '3': '3V3', '4': '3V3', '5': 'GND', '6': 'G17', '7': 'G4', '8': 'G3', '9': 'G48',
          '10': 'GND', '11': '3V3', '12': 'OUTP', '13': 'OUTN', '14': 'DACREF', '15': 'ADCREF', '16': 'VMID',
          '17': 'MIC1N', '18': 'MIC1P', '19': 'G45', '20': 'GND', '21': 'GND'})
# GND pins 5 / 10 / 20 run straight in to the exposed pad (0.12 wide: 0.165 clear of the next pins' inner ends),
# which drops to the B.Cu pour through two vias (locked, so freerouting keeps clear of them)
ep = [p for p in U4.Pads() if p.GetNumber() == '21'][0].GetPosition()
for n in ('5', '10', '20'):
    q = [p for p in U4.Pads() if p.GetNumber() == n][0].GetPosition()
    side = abs(q.x - ep.x) > abs(q.y - ep.y)                     # a pad on a side along y: run along x
    t = pcbnew.PCB_TRACK(b); t.SetStart(q)
    t.SetEnd(pcbnew.VECTOR2I(ep.x, q.y) if side else pcbnew.VECTOR2I(q.x, ep.y))
    t.SetWidth(mm(0.12)); t.SetLayer(pcbnew.F_Cu); t.SetNet(nets['GND']); t.SetLocked(True); b.Add(t)
for dx in (-0.4, 0.4):
    v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(ep.x + mm(dx), ep.y)); v.SetWidth(mm(0.6)); v.SetDrill(mm(0.3))
    v.SetNet(nets['GND']); v.SetLocked(True); b.Add(v)
C('C12', '10uF', '3V3', 'GND', -5.8, 13.4)                 # PVDD / DVDD (pins 3, 4 face -y)
C('C13', '100nF', '3V3', 'GND', -5.0, 15.3)
C('C14', '1uF', '3V3', 'GND', -1.9, 21.8, 90)              # AVDD (pins 11..15 face +y)
C('C15', '1uF', 'VMID', 'GND', -9.8, 21.8, 90)            # pins 16..20 face -x
C('C16', '1uF', 'ADCREF', 'GND', -8.0, 23.6, 90)
C('C17', '1uF', 'DACREF', 'GND', -6.2, 23.6, 90)
C('C18', '1uF', 'MIC1P', 'MICO', -9.3, 17.2, 90)
C('C19', '1uF', 'MIC1N', 'GND', -11.1, 17.2, 90)
R('R6', '4.7k', '3V3', 'G0', -14.5, 17.2, 90)
R('R7', '4.7k', '3V3', 'G45', -12.9, 17.2, 90)
U5 = load('Package_SO.pretty', 'MSOP-8_3x3mm_P0.65mm', 'U5', 'NS4150B', 7.0, 17.5)
wire(U5, {'1': 'G18', '2': 'BYP', '3': 'INP', '4': 'INN', '5': 'SPKN', '6': '3V3', '7': 'GND', '8': 'SPKP'})
C('C22', '100nF', 'OUTP', 'AIP', 3.5, 21.0)
C('C23', '100nF', 'OUTN', 'AIN', 6.5, 21.0)
R('R8', '150k', 'AIP', 'INP', 3.5, 23.2)
R('R9', '150k', 'AIN', 'INN', 6.5, 23.2)
C('C24', '1uF', 'BYP', 'GND', 10.5, 21.8)
R('R10', '10k', 'G18', 'GND', 8.0, 13.5)
C('C25', '100nF', '3V3', 'GND', 11.2, 13.2, 90)
C('C26', '10uF', '3V3', 'GND', 13.0, 11.0, 90)
SP1 = load('vein_base.pretty', 'Speaker_SMD_GSPK1304S_13x13mm', 'SP1', 'GSPK1304S-8R0.5W', 3.0, 5.5, local=True)
wire(SP1, {'1': 'SPKN', '2': 'SPKP'})

# ======== Grove: J6 for the Unit NFC (the VoiceS3R's PORT.A), J7 spare on G38 / G39 (the Ext.Pin's two) ========
for ref, x, value, s1, s2 in (('J6', 32.0, 'Grove HY2.0-4P RA (NFC, I2C)', 'G2', 'G1'),
                              ('J7', 18.5, 'Grove HY2.0-4P RA (G38 / G39)', 'G38', 'G39')):
    j = load('Connector_JST.pretty', 'JST_PH_S4B-PH-SM4-TB_1x04-1MP_P2.00mm_Horizontal', ref, value, x, 29.0, rot=180)
    wire(j, {'1': s1, '2': s2, '3': '5V', '4': 'GND', 'MP': 'GND'})

# ---- M2.3 holes over the case's PCB bosses, outline
for x, y in BOSSES:
    c = pcbnew.PCB_SHAPE(b); c.SetShape(pcbnew.SHAPE_T_CIRCLE)
    c.SetCenter(P(x, y)); c.SetEnd(P(x + 1.3, y)); c.SetLayer(pcbnew.Edge_Cuts); c.SetWidth(mm(0.1)); b.Add(c)
    # no tracks / vias under the M2.3 screw head (r 2.0) and within the 0.5 edge clearance of the hole
    k = pcbnew.ZONE(b); k.SetIsRuleArea(True); k.SetDoNotAllowTracks(True); k.SetDoNotAllowVias(True)
    k.SetDoNotAllowPads(False); k.SetDoNotAllowFootprints(False); k.SetDoNotAllowCopperPour(False)
    ls = pcbnew.LSET(); ls.AddLayer(pcbnew.F_Cu); ls.AddLayer(pcbnew.B_Cu); k.SetLayerSet(ls)
    ol = k.Outline(); ol.NewOutline()
    for i in range(16):
        ol.Append(mm(OX + x + 2.2 * math.cos(i * math.pi / 8)), mm(OY - y - 2.2 * math.sin(i * math.pi / 8)))
    b.Add(k)
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


# silk: (text, x, y) per outline; the Grove labels list pin 1 first
SILK = ([('1+2 PASS / 3+4 CROSS', -12.9, 4.6), ('J3 1RX 2TX 3V3 G', -20.0, -16.6), ('NFC: G2 G1 5V G', 15.5, -19.8),
         ('G38 G39 5V G', 12.8, 9.0), ('BOOT', 23.2, -9.4), ('EN', 23.2, 9.8)] if SW else
        [('SW1 1+2 PASS(FC-1200) / 3+4 CROSS', -41.2, 14.0), ('J3 vein: 1RX 2TX 3V3 4G', -30.0, 16.2),
         ('NFC: G2 G1 5V G', 32.0, 35.5), ('G38 G39 5V G', 18.5, 35.5), ('EN', 37.2, 7.0), ('BOOT', 37.2, 24.0)])
for t, x, y in SILK:
    text(t, x, y, size=0.8)
text(f'vein-station ESP board {REV} ' + ('(SW-85B)' if SW else '(PF13-4-9)'), -12.0 if SW else -20.0,
     -32.0 if SW else 18.0, layer=pcbnew.B_SilkS)



def stitch(b, pitch=2.5, clr=0.25):
    """GND vias on a grid wherever nothing else is: they tie the F.Cu pour pieces between the tracks to B.Cu."""
    r = 0.3 + clr
    items = [t.GetEffectiveShape() for t in b.GetTracks()]
    items += [p.GetEffectiveShape() for fp in b.GetFootprints() for p in fp.Pads()]
    crt = [fp.GetCourtyard(pcbnew.F_CrtYd) for fp in b.GetFootprints()]   # the WROOM's takes in its antenna keep-out
    holes = HOLES + BOSSES + ASL
    n = 0
    y = Y0 + 1.5
    while y < Y1 - 1.0:
        x = X0 + 1.5
        while x < X1 - 1.0:
            q = P(x, y)
            ok = (all((x - hx) ** 2 + (y - hy) ** 2 > 4.5 ** 2 for hx, hy in holes)
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
    fills = {z.GetLayer(): z.GetFilledPolysList(z.GetLayer()) for z in b.Zones() if not z.GetIsRuleArea()}
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
    print('dsn', pcbnew.ExportSpecctraDSN(b, f'{NAME}.dsn'))
    # 5V (USB -> LDO / Grove) routed 0.5 wide: a net class written into the DSN for freerouting (the .ses keeps it)
    d = open(f'{NAME}.dsn').read()
    i = d.index('    (class kicad_default'); j = d.index('(circuit', i)
    d = (d[:i] + '    (class PWR 5V\n      (circuit (use_via Via[0-1]_600:300_um))\n'
         '      (rule (width 500) (clearance 150))\n    )\n' + re.sub(r'(?<=\s)5V(?=\s)', '', d[i:j]) + d[j:])
    open(f'{NAME}.dsn', 'w').write(d)
else:
    if os.path.exists(f'{NAME}.ses'):
        import_ses(b, nets, f'{NAME}.ses')
    stitch(b)
    b.Save(f'{NAME}.kicad_pcb')
    # GND pour on both layers (the WROOM's rule area keeps it off the antenna), filled on a reloaded board
    b = pcbnew.LoadBoard(f'{NAME}.kicad_pcb')
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        z = pcbnew.ZONE(b); z.SetLayer(layer); z.SetNet(b.FindNet('GND'))
        ol = z.Outline(); ol.NewOutline()
        for x, y in ((X0 + 0.3, Y0 + 0.3), (X1 - 0.3, Y0 + 0.3), (X1 - 0.3, Y1 - 0.3), (X0 + 0.3, Y1 - 0.3)):
            ol.Append(mm(OX + x), mm(OY - y))
        z.SetLocalClearance(mm(0.3)); z.SetMinThickness(mm(0.25)); z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_NEVER)    # islands get a via first (below)
        b.Add(z)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    for _ in range(3):                                   # tie every pour piece left without a via to the other layer
        if not tie_islands(b):
            break
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    # then drop what is still floating (pieces too small for a via)
    for z in b.Zones():
        if not z.GetIsRuleArea():
            z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    # a stitching via that ended up in no pour on one layer (its piece was dropped as an island) does nothing
    fills = [z.GetFilledPolysList(z.GetLayer()) for z in b.Zones() if not z.GetIsRuleArea()]
    loose = [v for v in b.GetTracks() if v.GetClass() == 'PCB_VIA' and v.GetNetname() == 'GND' and not v.IsLocked()
             and not all(f.Contains(v.GetPosition()) for f in fills)
             and not any(t.GetClass() != 'PCB_VIA' and t.GetNetname() == 'GND' and t.HitTest(v.GetPosition())
                         for t in b.GetTracks())]
    for v in loose:
        b.Remove(v)
    print(f'removed {len(loose)} loose vias')
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    b.Save(f'{NAME}.kicad_pcb')
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
