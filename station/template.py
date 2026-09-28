"""1:1 paper templates (A4 PDF, matplotlib) for cutting windows and holes in Takachi cases by hand. Kept apart from
shapes.py (no CadQuery) so a template can be drawn without the CAD stack."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

RED = '#d0021b'


def rrect_xy(x0, x1, y0, y1, r, n=16):
    """A rounded rectangle as a closed point list (same shape as a DXF polyline with 90° bulges)."""
    if not r:
        return np.array([(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)])
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        a = np.radians(np.linspace(a0, a0 + 90, n + 1))
        pts += list(zip(cx + r * np.cos(a), cy + r * np.sin(a)))
    return np.array(pts + pts[:1])


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


def view(ax, txt, outline, holes=(), text=(), lines=(), at=(0, 0)):
    """One face of the case, 1:1, in its own mm with its origin at `at` on the sheet: the grey outline
    (x0, x1, y0, y1, r), extra lines [(xs, ys, plot kwargs)], text [(x, y, s, txt kwargs)] and the cuts in red:
    ('rect', x0, x1, y0, y1, r[, label]) with + at the corner drill centres (two + on the centre line when r = 0) and,
    with a label, the label and the size inside; ('circle', x, y, r) with + at the centre."""
    dx, dy = at
    ax.plot(*(rrect_xy(*outline) + (dx, dy)).T, color='0.35', lw=0.6)
    for xs, ys, kw in lines:
        ax.plot(np.add(xs, dx), np.add(ys, dy), **kw)
    for x, y, s, kw in text:
        txt(x + dx, y + dy, s, **kw)
    for kind, *g in holes:
        if kind == 'circle':
            x, y, r = g
            a = np.linspace(0, 2 * np.pi, 65)
            ax.plot(x + dx + r * np.cos(a), y + dy + r * np.sin(a), color=RED, lw=0.5)
            cross(ax, x + dx, y + dy)
            continue
        x0, x1, y0, y1, r = g[:5]
        ax.plot(*(rrect_xy(x0, x1, y0, y1, r) + (dx, dy)).T, color=RED, lw=0.5)
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


def cut_template(path, y_top, views, ruler_y, notes_y, notes, mono=()):
    """A4 portrait, 1 mm on paper = 1 mm (y_top = the sheet's top edge in sheet mm, x -105..105): the faces to lay on
    the case and cut by hand (views = [view() keyword arguments]), a 50 mm line to check the print scale and the notes."""
    fig, ax, txt = a4(y_top)
    for v in views:
        view(ax, txt, **v)
    ruler(ax, txt, ruler_y)
    notes_block(ax, txt, notes_y, notes, mono=mono)
    return save(fig, path)
