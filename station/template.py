"""1:1 paper templates (A4 PDF, matplotlib) for cutting windows and holes in Takachi cases by hand. Kept apart from
shapes.py (no CadQuery) so a template can be drawn without the CAD stack."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

RED = '#d0021b'
# A pen traced round the inside of a paper stencil runs this far inside its edge, and the cut goes inside that again,
# so a hole cut that way came out one size small (2026-10-07, the vein window). Templates for cutting by hand draw a
# dashed stencil line this far outside each cut: cut the paper out along it and the traced line lands on the cut.
STENCIL = 1.0


def rrect_xy(x0, x1, y0, y1, r, n=16):
    """A rounded rectangle as a closed point list (same shape as a DXF polyline with 90° bulges)."""
    if not r:
        return np.array([(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)])
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        a = np.radians(np.linspace(a0, a0 + 90, n + 1))
        pts += list(zip(cx + r * np.cos(a), cy + r * np.sin(a)))
    return np.array(pts + pts[:1])


def arc_ends_xy(L, W, re, rc, n=25):
    """Seen from above, a case whose long sides are straight and whose ends are arcs of radius `re` (tip on the axis,
    L apart) joined to the sides by corners of radius `rc` (Takachi SIC: re 34, rc 12). Closed point list, origin =
    centre, x along the case. Odd n puts a point on each end's tip."""
    ce = L / 2 - re                                     # the +x end arc's centre on the axis
    yc = W / 2 - rc                                     # the corner centres' distance off the axis
    xc = ce + np.sqrt((re - rc) ** 2 - yc ** 2)         # ... and along it, where the corner meets the end arc
    phi = np.degrees(np.arctan2(yc, xc - ce))           # the tangent point's direction from the end arc's centre
    arc = lambda cx, cy, r, a0, a1: list(zip(cx + r * np.cos(np.radians(np.linspace(a0, a1, n))),
                                             cy + r * np.sin(np.radians(np.linspace(a0, a1, n)))))
    half = arc(xc, -yc, rc, -90, -phi) + arc(ce, 0, re, -phi, phi) + arc(xc, yc, rc, phi, 90)
    pts = half + [(-x, -y) for x, y in half]
    return np.array(pts + pts[:1])


def arc_ends_tangent(W, re, rc):
    """Where the end arc of arc_ends_xy() meets a corner, across the case (± this from the axis)."""
    return (W / 2 - rc) * re / (re - rc)


def outline_xy(outline):
    """A view's outline: (x0, x1, y0, y1, r) for a rounded rectangle, or an (N, 2) point list."""
    return rrect_xy(*outline) if len(outline) == 5 and np.ndim(outline[0]) == 0 else np.asarray(outline)


def a4(y_top):
    """A4 portrait axes in mm, x -105..105, y_top at the top edge of the sheet."""
    W, H = 210.0, 297.0
    fig = plt.figure(figsize=(W / 25.4, H / 25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(-W / 2, W / 2)
    ax.set_ylim(y_top - H, y_top)
    ax.set_aspect('equal')
    ax.axis('off')
    txt = lambda x, y, s, **k: ax.text(x, y, s, fontsize=k.pop('fs', 7), family=k.pop('family', 'DejaVu Sans'), **k)
    return fig, ax, txt


def cross(ax, cx, cy, s=1.2):
    ax.plot([cx - s, cx + s], [cy, cy], color=RED, lw=0.25)
    ax.plot([cx, cx], [cy - s, cy + s], color=RED, lw=0.25)


def ruler(ax, txt, y):
    """A 50 mm line to check the print scale."""
    ax.plot([-25, 25], [y, y], color='k', lw=0.6)
    for i in range(6):
        ax.plot([-25 + 10 * i] * 2, [y, y + (3 if i in (0, 5) else 1.8)], color='k', lw=0.4)
    txt(0, y - 4.5, '50 mm: measure this line. If it is not 50 mm, reprint.', ha='center', fs=7)


def notes_block(ax, txt, y, lines, mono=()):
    for i, t in enumerate(lines):
        txt(-95, y, t, fs=6.2 if t in mono else 7, family='DejaVu Sans Mono' if t in mono else 'DejaVu Sans',
            weight='bold' if i < 2 else 'normal')
        y -= 5


def save(fig, path):
    fig.savefig(path, metadata={'CreationDate': None})
    plt.close(fig)
    print('wrote', path)
    return path


def view(ax, txt, outline, holes=(), text=(), lines=(), at=(0, 0), stencil=0.0):
    """One face of the case, 1:1, in its own mm with its origin at `at` on the sheet: the grey outline
    ((x0, x1, y0, y1, r) or a point list, see outline_xy()), extra lines [(xs, ys, plot kwargs)], text [(x, y, s, txt kwargs)] and the cuts in red:
    ('rect', x0, x1, y0, y1, r[, label]) with + at the corner drill centres (two + on the centre line when r = 0) and,
    with a label, the label and the size inside; ('circle', x, y, r) with + at the centre. stencil > 0: a dashed red
    line that far outside each cut (see STENCIL)."""
    dx, dy = at
    ax.plot(*(outline_xy(outline) + (dx, dy)).T, color='0.35', lw=0.6)
    for xs, ys, kw in lines:
        ax.plot(np.add(xs, dx), np.add(ys, dy), **kw)
    for x, y, s, kw in text:
        txt(x + dx, y + dy, s, **kw)
    for kind, *g in holes:
        if kind == 'circle':
            x, y, r = g
            a = np.linspace(0, 2 * np.pi, 65)
            ax.plot(x + dx + r * np.cos(a), y + dy + r * np.sin(a), color=RED, lw=0.5)
            if stencil:
                rs = r + stencil
                ax.plot(x + dx + rs * np.cos(a), y + dy + rs * np.sin(a), color=RED, lw=0.3, ls=(0, (8, 5)))
            cross(ax, x + dx, y + dy)
            continue
        x0, x1, y0, y1, r = g[:5]
        ax.plot(*(rrect_xy(x0, x1, y0, y1, r) + (dx, dy)).T, color=RED, lw=0.5)
        if stencil:
            s = stencil
            ax.plot(*(rrect_xy(x0 - s, x1 + s, y0 - s, y1 + s, r + s if r else 0) + (dx, dy)).T, color=RED, lw=0.3,
                    ls=(0, (8, 5)))
        if r:
            marks = ((x0 + r, y0 + r), (x1 - r, y0 + r), (x1 - r, y1 - r), (x0 + r, y1 - r))
        else:
            marks = [((x0 + x1) / 2 + k * (x1 - x0) / 4, (y0 + y1) / 2) for k in (-1, 1)]
        for cx, cy in marks:
            cross(ax, cx + dx, cy + dy)
        if len(g) > 5:
            cx, cy = (x0 + x1) / 2 + dx, (y0 + y1) / 2 + dy
            txt(cx, cy + 1.5, g[5], ha='center', va='center', fs=7, weight='bold', color=RED)
            txt(cx, cy - 2.5, f'{x1 - x0:.1f} x {y1 - y0:.1f}  R{r:g}', ha='center', va='center', fs=6, color=RED)


def edge_row(label, cut, outline, names=('left', 'right', 'back', 'front')):
    """One line of the notes: a cut's size and its distances from the outline's edges (names = -x, +x, -y, +y)."""
    x0c, x1c, y0c, y1c, _ = outline
    kind, *g = cut
    if kind == 'circle':
        x, y, r = g
        return (f'{label:9s} dia {2 * r:<11.1f} centre: {names[0]} {x - x0c:5.1f}  {names[1]} {x1c - x:5.1f}  '
                f'{names[2]} {y - y0c:5.1f}  {names[3]} {y1c - y:5.1f}')
    x0, x1, y0, y1, r = g[:5]
    return (f'{label:9s} {x1 - x0:5.1f} x {y1 - y0:4.1f}  R{r:<4g} {names[0]} {x0 - x0c:5.1f}  {names[1]} {x1c - x1:5.1f}'
            f'  {names[2]} {y0 - y0c:5.1f}  {names[3]} {y1c - y1:5.1f}' +
            (f'   drill at the + marks, dia {2 * r:.1f} or less' if r else ''))


def cut_template(path, y_top, views, ruler_y, notes_y, notes, mono=(), stencil=0.0):
    """A4 portrait, 1 mm on paper = 1 mm (y_top = the sheet's top edge in sheet mm, x -105..105): the faces to lay on
    the case and cut by hand (views = [view() keyword arguments]), a 50 mm line to check the print scale and the notes.
    stencil > 0 adds the dashed stencil lines (see STENCIL) and a note on them."""
    fig, ax, txt = a4(y_top)
    for v in views:
        view(ax, txt, stencil=stencil, **v)
    if stencil:
        notes = list(notes) + ['', f'Dashed red = stencil line, {stencil:g} outside the cut. To cut the paper out and trace '
                                   'inside it with a pen,', 'cut along the dashed line: the traced line then lands on or just outside the '
                                   'solid red line (the real size). Cut to the solid line.']
    ruler(ax, txt, ruler_y)
    notes_block(ax, txt, notes_y, notes, mono=mono)
    return save(fig, path)
