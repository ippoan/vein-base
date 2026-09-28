"""Dimensioned hole drawings (DXF with ezdxf, plus the same drawing as a PDF) for machining a Takachi case: one face per
sheet, seen from outside. Kept apart from shapes.py (no CadQuery), like template.py."""
import ezdxf
from ezdxf.enums import TextEntityAlignment
from ezdxf.addons.drawing import matplotlib as edm


def rrect(msp, x0, x1, y0, y1, r, layer):
    """Rounded rectangle as one closed polyline (bulge 0.4142 = 90° arc)."""
    b = 0.41421356
    pts = [(x0 + r, y0, 0), (x1 - r, y0, b), (x1, y0 + r, 0), (x1, y1 - r, b), (x1 - r, y1, 0), (x0 + r, y1, b),
           (x0, y1 - r, 0), (x0, y0 + r, b)] if r else [(x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0)]
    msp.add_lwpolyline(pts, format='xyb', close=True, dxfattribs={'layer': layer})


def dim(msp, base, p1, p2, angle=0):
    msp.add_linear_dim(base=base, p1=p1, p2=p2, angle=angle, dimstyle='EZDXF', dxfattribs={'layer': 'DIM'},
                       override={'dimlfac': 1, 'dimtxt': 2.5, 'dimasz': 2.0, 'dimdec': 1, 'dimexo': 1.0, 'dimexe': 1.5,
                                 'dimtad': 1, 'dimzin': 8}).render()


def note(msp, text, at, height=2.5, align=TextEntityAlignment.LEFT):
    msp.add_text(text, height=height, dxfattribs={'layer': 'NOTE'}).set_placement(at, align=align)


def face(msp, outline, holes, titles=(), datum=(0, 0), step=7):
    """One face of the case seen from outside. outline = (x0, x1, y0, y1, r), dimensioned overall; every hole gets its
    size and its centre from `datum` (the case centre for Takachi, who machine from the part's centre, or a corner a
    ruler can start from). titles = [(text, (x, y))] around the outline.
    holes = [dict(cut=('rect', x0, x1, y0, y1, r) | ('circle', x, y, r) | ('circles', [(x, y), ...], r),
                  text=[lines], at=(x, y) of the text, wdim / hdim = where the width / height dimension line goes
                  (default 4 past the hole's +y / +x edge))]; for 'circles' the first centre is the one dimensioned."""
    x0c, x1c, y0c, y1c, rc = outline
    mx, my = (x0c + x1c) / 2, (y0c + y1c) / 2
    rrect(msp, *outline, 'OUTLINE')
    msp.add_line((x0c - 4, my), (x1c + 4, my), dxfattribs={'layer': 'CENTER'})
    msp.add_line((mx, y0c - 4), (mx, y1c + 4), dxfattribs={'layer': 'CENTER'})
    for t, at in titles:
        note(msp, t, at, 3.0, TextEntityAlignment.MIDDLE_CENTER)
    dim(msp, (mx, y1c + 8), (x0c, y1c - rc), (x1c, y1c - rc))
    dim(msp, (x1c + 8, my), (x1c - rc, y0c), (x1c - rc, y1c), 90)
    for i, h in enumerate(holes):
        kind, *g = h['cut']
        if kind == 'rect':
            x0, x1, y0, y1, r = g
            (cx, cy), s = ((x0 + x1) / 2, (y0 + y1) / 2), 3
            rrect(msp, x0, x1, y0, y1, r, 'CUT')
        else:
            pts, r = ([g[:2]], g[2]) if kind == 'circle' else g
            for x, y in pts:
                msp.add_circle((x, y), r, dxfattribs={'layer': 'CUT'})
            (cx, cy), s = pts[0], r + 1
        msp.add_line((cx - s, cy), (cx + s, cy), dxfattribs={'layer': 'CENTER'})
        msp.add_line((cx, cy - s), (cx, cy + s), dxfattribs={'layer': 'CENTER'})
        if kind == 'rect':
            dim(msp, (mx, h.get('wdim', y1 + 4)), (x0, y1), (x1, y1))                  # width
            dim(msp, (h.get('hdim', x1 + 4), my), (x1, y0), (x1, y1), 90)              # height
        dim(msp, (mx, y0c - 8 - step * i), datum, (cx, cy))                              # centre x from the datum
        dim(msp, (x0c - 8 - step * i, my), datum, (cx, cy), 90)                          # centre y from the datum
        lx, ly = h['at']
        for k, t in enumerate(h['text']):
            note(msp, t, (lx, ly - 3.5 * k))


def sheet(path, title, notes, draw, x0, y0):
    """Write path (.dxf) with draw(msp) and the title / notes from (x0, y0) down, and the same drawing as a PDF next
    to it (Takachi asks for a dimensioned 2D drawing, DXF or PDF). Returns (dxf, pdf)."""
    doc = ezdxf.new('R2010', setup=True)   # setup: the EZDXF dimension style
    for ly, col in (('OUTLINE', 8), ('CUT', 1), ('COUNTERBORE', 5), ('CSK', 3), ('CENTER', 3), ('DIM', 5), ('NOTE', 7)):
        doc.layers.add(ly, color=col)
    msp = doc.modelspace()
    draw(msp)
    y = y0
    for t in [title] + notes:
        msp.add_text(t, height=2.0, dxfattribs={'layer': 'NOTE'}).set_placement((x0, y))
        y -= 3.5
    doc.saveas(path)
    print('wrote', path)
    pdf = path[:-4] + '.pdf'
    edm.qsave(msp, pdf, bg='#FFFFFF', size_inches=(11.69, 8.27))
    print('wrote', pdf)
    return path, pdf
