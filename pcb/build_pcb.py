"""vein-base: VoiceS3R Ext.Pin -> Finger Vein Module (A) relay board (NFC uses VoiceS3R's own PORT.A).
Board coords: origin = Atom center (M2 screw), +y = away from USB-C/PORT.A edge. Top (F) faces the Atom.
Ext.Pin rows are bottom-aligned at the USB-C/PORT.A end (y=-7.62), checked against the VoiceS3R silkscreen:
J1 (x=+7.62) 3V3,G5,G6,G7,G8 from y=+2.54 down; J2 (x=-7.62) G39,G38,5V,GND from y=0 down.
J3 = MX1.25 4P RA SMD, mates with the included 9P->4P cable (9P side re-pinned: 1->5, 2->6).
J3 pin order: 1=module RXD (<- G5), 2=module TXD (-> G6), 3=VCC 3V3, 4=GND.
Every part is on the top (F), so JLC's Economic PCBA (single side only) places them all in one pass.
J3 is 3.4 tall and the header plastic leaves only 2.54 under the Atom, so the board runs out past the Atom's +y
edge (Atom outline 24 x 24, +-12) and J3 sits there with its opening on the +y board edge. +y keeps it clear of the
USB-C / PORT.A plugs on the -y side.

Two variants share the parts, nets and helpers; VARIANTS holds only what differs:
  cup    -> vein_base.kicad_pcb: 20 x 29.9, 1.6 thick, for the 3D printed cup (case/). J3 courtyard y +12.5..+19.3.
  atomic -> vein_base_atomic.kicad_pcb: M5Stack's ATOMIC-TYPE-A outline, 1.0 thick, for the ATOMIC Proto Kit (A077)
            case. Notches at (+-8, +8) R3.7 clear the case's posts, so wires cross y +4.3..+11.7 within x +-3.8.
"""
import os
import pcbnew

VER = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'VERSION')).read().strip()

FP = '/usr/share/kicad/footprints/'
OX, OY = 100.0, 100.0
mm = pcbnew.FromMM


def P(x, y):
    return pcbnew.VECTOR2I(mm(OX + x), mm(OY - y))


# ATOMIC-TYPE-A board outline, the first LWPOLYLINE of Atomic_Type_A.dxf as (x, y, bulge) (DXF origin = the Atom's
# center hole; https://github.com/m5stack/M5_Hardware/tree/master/Common/Atomic_Type_A/Structures).
# The DXF's +y is our -y (its pin holes match J1 / J2 only that way), so atomic_outline() flips y and the bulges.
ATOMIC_DXF = [
    (10, 8.8, 0), (10, -4.3, 0), (8, -4.3, 1), (8, -11.7, 0), (10, -11.7, 0), (10, -20, 0), (9, -21, 0),
    (9, -27, 0), (10, -28, 0), (10, -33.2, 0), (9.65, -33.2, 1), (8.35, -33.2, 0), (8.35, -33.55, 0),
    (8.1, -33.8, 0), (4.6, -33.8, 0), (4.55, -33.75, 0), (4.55, -33.3, 1), (3.45, -33.3, 0), (3.45, -33.75, 0),
    (3.4, -33.8, 0), (-3.4, -33.8, 0), (-3.45, -33.75, 0), (-3.45, -33.3, 1), (-4.55, -33.3, 0), (-4.55, -33.75, 0),
    (-4.6, -33.8, 0), (-8.1, -33.8, 0), (-8.35, -33.55, 0), (-8.35, -33.2, 1), (-9.65, -33.2, 0), (-10, -33.2, 0),
    (-10, -28, 0), (-9, -27, 0), (-9, -21, 0), (-10, -20, 0), (-10, -11.7, 0), (-8, -11.7, 1), (-8, -4.3, 0),
    (-10, -4.3, 0), (-10, 9.6, 0), (-9.6, 10, 0), (-4.5, 10, 0), (-3.914, 9.414, 0), (-1.414, 9.414, -0.414427),
    (1.414, 9.414, 0), (3.914, 9.414, 0), (4.5, 10, 0), (9.6, 10, 0), (10, 9.6, 0),
]


def atomic_outline():
    return [(x, -y, -bu) for x, y, bu in ATOMIC_DXF]


def cup_routes(x1, x2, x3, x4, yv):
    return {
        # G5: B.Cu down the right of the screw hole -> J1-2
        'G5_TX': [(x1, yv), (5.5, yv - 5.5 + x1), (5.5, 0.8), (6.8, 0.8), (7.62, 0.0)],
        # G6: B.Cu, parallel inside G5 -> J1-3
        'G6_RX': [(x2, yv), (4.3, yv - 4.3 + x2), (4.3, -1.7), (6.8, -1.7), (7.62, -2.54)],
        # 3V3: F.Cu under the G5 / G6 vias -> J1-1
        '3V3': [(x3, 10.5), (6.5, 10.5), (7.62, 9.38), (7.62, 2.54)],
        # GND: F.Cu down the left of the screw hole -> J2-4
        'GND': [(x4, 12.0), (-5.5, 8.375), (-5.5, -6.0), (-7.62, -7.62)],
    }


def atomic_routes(x1, x2, x3, x4, yv):
    # through the post notches' band (y +4.3..+11.7) at x -3.0..+3.3, then around the 4.2 hole as on the cup board
    return {
        'G5_TX': [(x1, yv), (3.3, yv - 3.3 + x1), (3.3, 4.0), (5.5, 1.8), (5.5, 0.8), (6.8, 0.8), (7.62, 0.0)],
        'G6_RX': [(x2, yv), (2.3, yv - 2.3 + x2), (2.3, 3.0), (4.3, 1.0), (4.3, -1.7), (6.8, -1.7), (7.62, -2.54)],
        '3V3': [(x3, yv - 1.5), (2.8, yv - 1.5 - 2.8 + x3), (2.8, 4.3), (4.56, 2.54), (7.62, 2.54)],
        'GND': [(x4, yv - 1.9), (-3.0, yv - 1.9 - 3.0 - x4), (-3.0, 4.3), (-5.5, 1.8), (-5.5, -6.0), (-7.62, -7.62)],
    }


VARIANTS = [
    dict(out='vein_base.kicad_pcb', thickness=1.6,
         outline=[(-10, -10.6, 0), (10, -10.6, 0), (10, 19.3, 0), (-10, 19.3, 0)],
         # 2.4 mm loose-fit M2 hole from the project library (stock M2 is 2.2 mm)
         hole='MountingHole_2.4mm_M2', j3y=19.3 - 3.1, routes=cup_routes,
         silk=[('GND', -4.6, -7.0, 'F'), ('USB-C / cable side', 0, -9.6, 'F'),
               ('J3 1RX 2TX 3V3 4G', 0, 8.3, 'B'), (f'vein-base v{VER}', 0, 6.0, 'B')]),
    dict(out='vein_base_atomic.kicad_pcb', thickness=1.0, outline=atomic_outline(),
         # the ATOMIC-TYPE-A center hole, 4.2 non-plated
         hole='MountingHole_4.2mm_NPTH', j3y=33.2 - 3.1, routes=atomic_routes,
         silk=[('GND', -4.6, -7.0, 'F'), ('USB-C / cable side', 0, -8.2, 'F'),
               ('J3 1RX 2TX 3V3 4G', 0, 24.0, 'B'), (f'vein-base atomic v{VER}', 0, 16.0, 'B')]),
]

LIBS = {}  # nickname -> fp-lib-table uri
LAY = {'F.Cu': pcbnew.F_Cu, 'B.Cu': pcbnew.B_Cu}
SILK = {'F': pcbnew.F_SilkS, 'B': pcbnew.B_SilkS}
b = nets = None  # the board being built and its nets, set by build()


def load(lib, name, base=FP, uri_base=FP):
    fp = pcbnew.FootprintLoad(base + lib, name)
    nick = lib.removesuffix('.pretty'); LIBS[nick] = uri_base + lib
    fp.SetFPID(pcbnew.LIB_ID(nick, name))  # DRC library parity needs the lib nickname
    b.Add(fp); return fp


def padpos(fp, num):
    for p in fp.Pads():
        if p.GetNumber() == num:
            v = p.GetPosition()
            return (round(pcbnew.ToMM(v.x) - OX, 3), round(OY - pcbnew.ToMM(v.y), 3))


def track(pts, net, layer, w):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(b); t.SetStart(P(x1, y1)); t.SetEnd(P(x2, y2))
        t.SetWidth(mm(w)); t.SetLayer(LAY[layer]); t.SetNet(nets[net]); b.Add(t)


def via(x, y, net):
    v = pcbnew.PCB_VIA(b); v.SetPosition(P(x, y)); v.SetWidth(mm(0.6)); v.SetDrill(mm(0.3))
    v.SetNet(nets[net]); b.Add(v)


def edge(pts):
    """Closed Edge.Cuts outline from (x, y, bulge) vertices; bulge (DXF) = tan(arc angle / 4), + = counter-clockwise."""
    for (xa, ya, bu), (xb, yb, _) in zip(pts, pts[1:] + pts[:1]):
        s = pcbnew.PCB_SHAPE(b)
        if bu:
            dx, dy = xb - xa, yb - ya
            k = bu / 2  # sagitta / chord; the arc bulges to the right of a -> b when counter-clockwise
            s.SetShape(pcbnew.SHAPE_T_ARC)
            s.SetArcGeometry(P(xa, ya), P((xa + xb) / 2 + k * dy, (ya + yb) / 2 - k * dx), P(xb, yb))
        else:
            s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(P(xa, ya)); s.SetEnd(P(xb, yb))
        s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.1)); b.Add(s)


def text(s, x, y, layer=pcbnew.F_SilkS, size=0.8, mirror=False):
    t = pcbnew.PCB_TEXT(b); t.SetText(s); t.SetPosition(P(x, y)); t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size))); t.SetTextThickness(mm(0.12))
    if mirror: t.SetMirrored(True)
    b.Add(t)


def build(v):
    global b, nets
    print(v['out'])
    b = pcbnew.BOARD()
    ds = b.GetDesignSettings()
    ds.SetCopperLayerCount(2)
    ds.SetBoardThickness(mm(v['thickness']))

    nets = {}
    for n in ['3V3', 'GND', 'G5_TX', 'G6_RX', '5V', 'G7', 'G8', 'G38', 'G39']:
        ni = pcbnew.NETINFO_ITEM(b, n); b.Add(ni); nets[n] = ni

    J1 = load('Connector_PinHeader_2.54mm.pretty', 'PinHeader_1x05_P2.54mm_Vertical')
    J1.SetReference('J1'); J1.SetValue('Hdr 1x5 2.54 (3V3,G5,G6,G7,G8)'); J1.SetPosition(P(7.62, 2.54))
    for pad, n in zip(sorted(J1.Pads(), key=lambda p: int(p.GetNumber())), ['3V3', 'G5_TX', 'G6_RX', 'G7', 'G8']):
        pad.SetNet(nets[n])

    J2 = load('Connector_PinHeader_2.54mm.pretty', 'PinHeader_1x04_P2.54mm_Vertical')
    J2.SetReference('J2'); J2.SetValue('Hdr 1x4 2.54 (G39,G38,5V,GND)'); J2.SetPosition(P(-7.62, 0))
    for pad, n in zip(sorted(J2.Pads(), key=lambda p: int(p.GetNumber())), ['G39', 'G38', '5V', 'GND']):
        pad.SetNet(nets[n])

    J3 = load('Connector_Molex.pretty', 'Molex_PicoBlade_53261-0471_1x04-1MP_P1.25mm_Horizontal')
    J3.SetReference('J3'); J3.SetValue('MX1.25-4P RA SMD (Molex 53261-0471)')
    J3.SetPosition(P(0, v['j3y']))   # opening on the +y edge, as on the station board
    J3.SetOrientationDegrees(180)
    for p in J3.Pads():
        n = p.GetNumber()
        if n != 'MP':
            p.SetNet(nets[{'1': 'G5_TX', '2': 'G6_RX', '3': '3V3', '4': 'GND'}[n]])
    print('J3 pads:', [(n, padpos(J3, n)) for n in '1234'])
    J3.BuildCourtyardCaches()
    cy = J3.GetCourtyard(pcbnew.F_CrtYd).BBox()
    print('J3 courtyard y', round(OY - pcbnew.ToMM(cy.GetBottom()), 3), '..', round(OY - pcbnew.ToMM(cy.GetY()), 3),
          'x', round(pcbnew.ToMM(cy.GetX()) - OX, 3), '..', round(pcbnew.ToMM(cy.GetRight()) - OX, 3))

    H1 = load('vein_base.pretty', v['hole'], base='', uri_base='${KIPRJMOD}/')
    H1.SetReference('H1'); H1.SetPosition(P(0, 0))

    x1, x2, x3, x4 = (padpos(J3, n)[0] for n in '1234')
    yp = padpos(J3, '1')[1]            # the pads' Atom-side end is 0.8 lower
    yv = yp - 1.8                      # G5 / G6 vias to B.Cu, just below the pads
    r = v['routes'](x1, x2, x3, x4, yv)
    for x, net in [(x1, 'G5_TX'), (x2, 'G6_RX')]:  # J3-1 / J3-2: via -> B.Cu
        track([(x, yp), (x, yv)], net, 'F.Cu', 0.3); via(x, yv, net)
        track(r[net], net, 'B.Cu', 0.3)
    for x, net in [(x3, '3V3'), (x4, 'GND')]:      # J3-3 / J3-4: F.Cu
        track([(x, yp)] + r[net], net, 'F.Cu', 0.4)
    print('pads', x1, x2, x3, x4, yp)

    edge(v['outline'])
    for s, x, y, side in v['silk']:
        text(s, x, y, layer=SILK[side], mirror=side == 'B')

    b.Save(v['out'])


for v in VARIANTS:
    build(v)
# project-local fp-lib-table so DRC can resolve the footprint libraries
with open('fp-lib-table', 'w') as f:
    f.write('(fp_lib_table\n  (version 7)\n')
    for nick, uri in sorted(LIBS.items()):
        f.write(f'  (lib (name "{nick}")(type "KiCad")(uri "{uri}")(options "")(descr ""))\n')
    f.write(')\n')
print('saved')
