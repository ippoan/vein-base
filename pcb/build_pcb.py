"""vein-base v0.6: VoiceS3R Ext.Pin -> Finger Vein Module (A) relay board (NFC uses VoiceS3R's own PORT.A).
Board coords: origin = Atom center (M2 screw), +y = away from USB-C/PORT.A edge. Top (F) faces the Atom.
Ext.Pin rows are bottom-aligned at the USB-C/PORT.A end (y=-7.62), checked against the VoiceS3R silkscreen:
J1 (x=+7.62) 3V3,G5,G6,G7,G8 from y=+2.54 down; J2 (x=-7.62) G39,G38,5V,GND from y=0 down.
J3 = MX1.25 4P RA SMD (bottom), mates with the included 9P->4P cable (9P side re-pinned: 1->5, 2->6).
J3 pin order: 1=module RXD (<- G5), 2=module TXD (-> G6), 3=VCC 3V3, 4=GND.
"""
import pcbnew

FP = '/usr/share/kicad/footprints/'
OX, OY = 100.0, 100.0
mm = pcbnew.FromMM


def P(x, y):
    return pcbnew.VECTOR2I(mm(OX + x), mm(OY - y))


b = pcbnew.BOARD()
ds = b.GetDesignSettings()
ds.SetCopperLayerCount(2)
ds.SetBoardThickness(mm(1.6))

nets = {}
for n in ['3V3', 'GND', 'G5_TX', 'G6_RX', '5V', 'G7', 'G8', 'G38', 'G39']:
    ni = pcbnew.NETINFO_ITEM(b, n); b.Add(ni); nets[n] = ni


LIBS = {}  # nickname -> fp-lib-table uri


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
J3.SetPosition(P(0, -10.6 + 3.1))
J3.Flip(J3.GetPosition(), False)
J3.SetOrientationDegrees(180)
for p in J3.Pads():
    n = p.GetNumber()
    if n != 'MP':
        p.SetNet(nets[{'1': 'G5_TX', '2': 'G6_RX', '3': '3V3', '4': 'GND'}[n]])
print('J3 pads:', [(n, padpos(J3, n)) for n in '1234'])

# 2.4 mm loose-fit M2 hole from the project library (stock M2 is 2.2 mm)
H1 = load('vein_base.pretty', 'MountingHole_2.4mm_M2', base='', uri_base='${KIPRJMOD}/')
H1.SetReference('H1'); H1.SetPosition(P(0, 0))

LAY = {'F.Cu': pcbnew.F_Cu, 'B.Cu': pcbnew.B_Cu}


def track(pts, net, layer, w):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(b); t.SetStart(P(x1, y1)); t.SetEnd(P(x2, y2))
        t.SetWidth(mm(w)); t.SetLayer(LAY[layer]); t.SetNet(nets[net]); b.Add(t)


def via(x, y, net):
    v = pcbnew.PCB_VIA(b); v.SetPosition(P(x, y)); v.SetWidth(mm(0.6)); v.SetDrill(mm(0.3))
    v.SetNet(nets[net]); b.Add(v)


x1, x2, x3, x4 = (padpos(J3, n)[0] for n in '1234')
yp = padpos(J3, '1')[1]            # -5.1 (connector opening faces -y, same side as USB-C / PORT.A)
yr = yp + 0.8                      # rear end of the pads (toward +y)
# G6 (J3-2): via -> F.Cu -> J1-3
track([(x2, yp), (x2, -3.3)], 'G6_RX', 'B.Cu', 0.3); via(x2, -3.3, 'G6_RX')
track([(x2, -3.3), (6.8, -3.3), (7.62, -2.54)], 'G6_RX', 'F.Cu', 0.3)
# G5 (J3-1): B.Cu -> J1-2
track([(x1, yp), (x1, -2.2), (3.0, -1.0), (6.0, -1.0), (7.62, 0.0)], 'G5_TX', 'B.Cu', 0.3)
# 3V3 (J3-3): B.Cu around the left of the screw hole -> J1-1
track([(x3, yp), (x3, -3.6), (-2.0, -2.2), (-2.0, 1.8), (-0.8, 3.0), (6.2, 3.0), (7.62, 2.54)], '3V3', 'B.Cu', 0.4)
# GND (J3-4): B.Cu -> J2-4
track([(x4, yp), (x4, -4.0), (-6.1, -4.0), (-6.1, -6.6), (-7.62, -7.62)], 'GND', 'B.Cu', 0.4)
print('pads', x1, x2, x3, x4, yp)

X0, X1, Y0, Y1 = -10, 10, -10.6, 9.3
for (a, c), (d, e) in [((X0, Y0), (X1, Y0)), ((X1, Y0), (X1, Y1)), ((X1, Y1), (X0, Y1)), ((X0, Y1), (X0, Y0))]:
    s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(P(a, c)); s.SetEnd(P(d, e)); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.1)); b.Add(s)


def text(s, x, y, layer=pcbnew.F_SilkS, size=0.8, mirror=False):
    t = pcbnew.PCB_TEXT(b); t.SetText(s); t.SetPosition(P(x, y)); t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size))); t.SetTextThickness(mm(0.12))
    if mirror: t.SetMirrored(True)
    b.Add(t)


#text('3V3', 7.62, 9.8)
text('GND', -4.6, -7.0)
text('USB-C / cable side', 0, -9.6)
text('J3 1RX 2TX 3V3 4G', 0, 8.3, layer=pcbnew.B_SilkS, size=0.8, mirror=True)
text('vein-base v0.6', 0, 6.0, layer=pcbnew.B_SilkS, size=0.8, mirror=True)

b.Save('vein_base.kicad_pcb')
# project-local fp-lib-table so DRC can resolve the footprint libraries
with open('fp-lib-table', 'w') as f:
    f.write('(fp_lib_table\n  (version 7)\n')
    for nick, uri in sorted(LIBS.items()):
        f.write(f'  (lib (name "{nick}")(type "KiCad")(uri "{uri}")(options "")(descr ""))\n')
    f.write(')\n')
print('saved')
