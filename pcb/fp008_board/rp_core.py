"""The RP2350A core of Raspberry Pi's "RP2350A Minimal" design (MIT, rp2350_core_LICENSE.txt here)
put on one of our boards around an RP2354A: the chip, its regulator, crystal, decoupling and USB series resistors with
their footprints, tracks, vias and zones as Raspberry Pi laid them out ("Hardware design with RP2350" 2.1: use this
layout). The data is rp2350_core.json here (from rp_core_extract.py here); this module is how a board script takes it in,
written so that any board can import it (pcb/fp008_board f6 does). Run with KiCad's python.

    core = Core(b, nets, at, net_map, ref_map, rot=0, moved={}, drop_nets=(), drop_boxes=(), box=BOX)
                            # at(x, y) -> VECTOR2I: our board's coordinates (mm, y up)
    core.place()            # footprints + the locked tracks / vias; returns the chip's footprint
    core.zones()            # the minimal design's zones (+ a 3V3 area over the core): the board file
    core.keepouts()         # the zones as routing keepouts: the DSN for freerouting

Core coordinates are the JSON's: mm from U1's origin, KiCad's axes (y down). `origin` is where U1 goes on our board,
`rot` (deg, anticlockwise as seen from F) turns the whole core about it.
A board short of room can re-place some of the core's parts (`moved`: JSON ref -> (x, y, rot) in core coordinates) and
leave out the copper that went to them: the tracks of `drop_nets` (JSON net names), every track with an end / via
inside one of `drop_boxes` ((x0, x1, y0, y1) in core coordinates) and the zones wholly inside one; `box` is then the BOX
the 3V3 area over the core takes (FP008 f8 moves the crystal's parts close under the chip and the left side's
decoupling next to its pins, and routes them itself).
"""
import json, math, os
import pcbnew

mm = pcbnew.FromMM
HERE = os.path.dirname(os.path.abspath(__file__))
JSON = os.path.join(HERE, 'rp2350_core.json')
BOX = (-7.6, 8.2, -8.6, 14.8)            # rp_core_extract.py's BOX (U1-relative x0, x1, y0, y1, y down)
SHAPE = {'rect': pcbnew.PAD_SHAPE_RECT, 'circle': pcbnew.PAD_SHAPE_CIRCLE, 'oval': pcbnew.PAD_SHAPE_OVAL}
DRILL = 0.3                              # their 0.25 drills -> 0.3 (JLC's standard)
# the core's own nets -> names on our boards (the GPIOs / USB / RUN / SWD / QSPI_SS each board maps itself)
BASE_NET = {'+3V3': '3V3', 'GND': 'GND', '+1V1': '1V1', '/VREG_AVDD': 'VAVDD', '/VREG_LX': 'VLX', '/XIN': 'RXI',
            '/XOUT': 'RXO', 'Net-(C4-Pad1)': 'RXO2', 'Net-(U1-USB_DP)': 'RDP', 'Net-(U1-USB_DM)': 'RDM'}
BASE_REF = lambda r: {'U1': 'U6', 'L1': 'L106', 'X1': 'Y106'}.get(r, r[0] + str(100 + int(r[1:])))


class Core:
    def __init__(self, b, nets, origin, net_map, ref_map=BASE_REF, rot=0, moved=None, drop_nets=(), drop_boxes=(), box=BOX):
        self.b, self.nets, self.origin, self.rot = b, nets, origin, rot
        self.moved, self.drop_nets, self.drop_boxes, self.BOX = moved or {}, set(drop_nets), list(drop_boxes), box
        self.net = {**BASE_NET, **net_map}
        self.ref = ref_map
        self.data = json.load(open(JSON))

    def dropped(self, *pts):
        """Any of the points (core coordinates) inside one of drop_boxes."""
        return any(x0 < x < x1 and y0 < y < y1 for x, y in pts for x0, x1, y0, y1 in self.drop_boxes)

    def to_board(self, dx, dy):
        """Core (mm from U1, y down) -> our board (mm, y up)."""
        t = math.radians(self.rot)
        x, y = dx, -dy                                   # y up
        return (self.origin[0] + x * math.cos(t) - y * math.sin(t),
                self.origin[1] + x * math.sin(t) + y * math.cos(t))

    def P(self, dx, dy, OX=100.0, OY=100.0):
        x, y = self.to_board(dx, dy)
        return pcbnew.VECTOR2I(mm(OX + x), mm(OY - y))

    def box(self):
        """The core's BOX on our board: (x0, x1, y0, y1), y up."""
        pts = [self.to_board(x, y) for x in self.BOX[:2] for y in self.BOX[2:]]
        return (min(p[0] for p in pts), max(p[0] for p in pts), min(p[1] for p in pts), max(p[1] for p in pts))

    def place(self):
        b, nets = self.b, self.nets
        for f in self.data['footprints']:
            fp = pcbnew.FOOTPRINT(b)
            fp.SetFPID(pcbnew.LIB_ID('rpi_minimal', f['fp'])); fp.SetReference(self.ref(f['ref'])); fp.SetValue(f['value'])
            fp.Reference().SetVisible(False); fp.Value().SetLayer(pcbnew.F_Fab)
            b.Add(fp)
            for q in f['pads']:
                pd = pcbnew.PAD(fp)
                pd.SetNumber(q['num']); pd.SetShape(SHAPE[q['shape']])
                pd.SetSize(pcbnew.VECTOR2I(mm(q['w']), mm(q['h'])))
                if q['type'] == 'thru_hole':
                    dr = max(q['drill'], DRILL)
                    pd.SetAttribute(pcbnew.PAD_ATTRIB_PTH); pd.SetDrillSize(pcbnew.VECTOR2I(mm(dr), mm(dr)))
                    pd.SetLayerSet(pcbnew.PAD.PTHMask())
                else:
                    pd.SetAttribute(pcbnew.PAD_ATTRIB_SMD); pd.SetLayerSet(pcbnew.PAD.SMDMask())
                    if 'F.Paste' not in q['layers']:
                        ls = pd.GetLayerSet(); ls.RemoveLayer(pcbnew.F_Paste); pd.SetLayerSet(ls)
                loc = pcbnew.VECTOR2I(mm(q['x']), mm(q['y']))       # the footprint is still at the origin, unturned
                pd.SetPos0(loc); pd.SetPosition(loc)
                pd.SetOrientation(pcbnew.EDA_ANGLE(q['rot'] - f['rot'], pcbnew.DEGREES_T))
                n = self.net.get(q['net'])
                if n:
                    pd.SetNet(nets[n])
                fp.Add(pd)
            for kind, x0, y0, x1, y1 in f['courtyard']:
                g = pcbnew.FP_SHAPE(fp); g.SetShape(pcbnew.SHAPE_T_RECT if kind == 'fp_rect' else pcbnew.SHAPE_T_SEGMENT)
                g.SetStart0(pcbnew.VECTOR2I(mm(x0), mm(y0))); g.SetEnd0(pcbnew.VECTOR2I(mm(x1), mm(y1)))
                g.SetLayer(pcbnew.F_CrtYd); g.SetWidth(mm(0.05)); g.SetDrawCoord(); fp.Add(g)
            fx, fy, frot = self.moved.get(f['ref'], (f['x'], f['y'], f['rot']))
            fp.SetPosition(self.P(fx, fy))
            fp.SetOrientationDegrees(frot + self.rot)
        # the core's copper, locked (freerouting routes round it and leaves it out of the .ses)
        for t in self.data['segments']:
            if t['net'] in self.drop_nets or self.dropped((t['x0'], t['y0']), (t['x1'], t['y1'])):
                continue
            tr = pcbnew.PCB_TRACK(b); tr.SetStart(self.P(t['x0'], t['y0'])); tr.SetEnd(self.P(t['x1'], t['y1']))
            tr.SetWidth(mm(t['w'])); tr.SetLayer(pcbnew.F_Cu if t['layer'] == 'F.Cu' else pcbnew.B_Cu)
            tr.SetNet(nets[self.net[t['net']]]); tr.SetLocked(True); b.Add(tr)
        for v in self.data['vias']:
            if self.dropped((v['x'], v['y'])):
                continue
            vi = pcbnew.PCB_VIA(b); vi.SetPosition(self.P(v['x'], v['y'])); vi.SetWidth(mm(v['size']))
            vi.SetDrill(mm(max(v['drill'], DRILL)))
            vi.SetNet(nets[self.net[v['net']]]); vi.SetLocked(True); b.Add(vi)
        return next(fp for fp in b.GetFootprints() if fp.GetReference() == self.ref('U1'))

    def zlist(self):
        """The minimal design's zones, but those wholly inside one of drop_boxes."""
        return [z for z in self.data['zones'] if not any(all(x0 < x < x1 and y0 < y < y1 for x, y in z['pts'])
                                                         for x0, x1, y0, y1 in self.drop_boxes)]

    def zones(self, area=True):
        """The minimal design's zones (priorities one up, over the board's GND pours) and a 3V3 area on F.Cu over the
        core (the minimal design's F.Cu is a 3V3 pour, which several of its decoupling caps reach their supply
        through). Pads join solid, as in the minimal design's own 3V3 zones (connect_pads yes): with thermals, a pad
        hemmed in by the tracks into the core kept one spoke only (DRC starved_thermal at U6 pin 1)."""
        b = self.b

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
        x0, x1, y0, y1 = self.BOX
        if area:                                       # not in the DSN: the signals into the core cross it
            zone('3V3', pcbnew.F_Cu, [self.P(x0, y0), self.P(x1, y0), self.P(x1, y1), self.P(x0, y1)], 1, 0.2, 0.2, True)
        for z in self.zlist():
            zone(self.net[z['net']], pcbnew.F_Cu if z['layer'] == 'F.Cu' else pcbnew.B_Cu,
                 [self.P(px, py) for px, py in z['pts']], z['priority'] + 1, z['clearance'], z['min_thickness'],
                 z['connect'] == 'yes', z['thermal_gap'], z['thermal_width'])

    def keepouts(self):
        """For freerouting only: the core's zones as keepouts (no tracks / vias), so nothing else is routed through
        the regulator's and the crystal's copper. As planes in the DSN they would cover the other nets' pads under
        them. 3V3's are left out (3V3 is routed to the core's pins through them: VREG_VIN, pin 49), but for the ring
        under the chip (the 3V3 square round its centre): a signal via dropped there between the pins cuts the ring in
        two (FP008 f6: FPRX and SWDIO vias, DRC unconnected 3V3 zone)."""
        for z in self.zlist():
            xs = [p[0] for p in z['pts']]; ys = [p[1] for p in z['pts']]
            if z['net'] == '+3V3' and not (min(xs) < 0 < max(xs) and min(ys) < 0 < max(ys)):
                continue
            k = pcbnew.ZONE(self.b); k.SetIsRuleArea(True); k.SetDoNotAllowTracks(True); k.SetDoNotAllowVias(True)
            k.SetDoNotAllowCopperPour(False); k.SetDoNotAllowPads(False); k.SetDoNotAllowFootprints(False)
            k.SetLayer(pcbnew.F_Cu if z['layer'] == 'F.Cu' else pcbnew.B_Cu)
            ol = k.Outline(); ol.NewOutline()
            for px, py in z['pts']:
                q = self.P(px, py); ol.Append(q.x, q.y)
            self.b.Add(k)
