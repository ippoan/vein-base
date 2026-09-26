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


def vein_unit_template(path, title, case, top, win, end, notes):
    """The Vein Unit's two cuts on one A4 sheet, 1:1.
    case = (L, W, R): the outline seen from above (origin = centre, x along the case)
    top = (left label, right label, back label, front label) around the top view
    win = (x0, x1, y0, y1, r): the cover window
    end = dict(side=+1 / -1 (which x end), h=body height, hole=('rect', y0, y1, z0, z1) or ('circle', y, z, r),
               label=the text over the end view); z from the bottom of the body."""
    fig, ax, txt = a4(60)
    L, W, R = case
    # ---- the cover, seen from above
    ax.plot(*rrect_xy(-L / 2, L / 2, -W / 2, W / 2, R).T, color='0.35', lw=0.6)
    ax.plot([-L / 2 + 4, L / 2 - 4], [0, 0], color='0.6', lw=0.3, ls='-.')
    ax.plot([0, 0], [-W / 2 + 4, W / 2 - 4], color='0.6', lw=0.3, ls='-.')
    txt(-L / 2 - 2, 0, top[0], ha='right', va='center', fs=7, weight='bold')
    txt(L / 2 + 2, 0, top[1], ha='left', va='center', fs=7, weight='bold')
    txt(0, W / 2 + 2.5, top[3], ha='center', fs=7, weight='bold')
    txt(0, -W / 2 - 5.5, top[2], ha='center', fs=7, weight='bold')
    x0, x1, y0, y1, r = win
    ax.plot(*rrect_xy(x0, x1, y0, y1, r).T, color=RED, lw=0.5)
    for cx, cy in ((x0 + r, y0 + r), (x1 - r, y0 + r), (x1 - r, y1 - r), (x0 + r, y1 - r)):
        cross(ax, cx, cy)
    txt((x0 + x1) / 2, (y0 + y1) / 2 + 1.5, 'vein window', ha='center', va='center', fs=7, weight='bold', color=RED)
    txt((x0 + x1) / 2, (y0 + y1) / 2 - 2.5, f'{x1 - x0:.1f} x {y1 - y0:.1f}  R{r:g}', ha='center', va='center',
        fs=6, color=RED)
    txt(-L / 2, W / 2 + 9, 'COVER, seen from above (lay face up on the cover)', fs=8, weight='bold')
    rows = [f'window  {x1 - x0:5.1f} x {y1 - y0:4.1f}  R{r:<4g} from the outline: left {x0 + L / 2:4.1f}  '
            f'right {L / 2 - x1:4.1f}  -y {y0 + W / 2:4.1f}  +y {W / 2 - y1:4.1f}']
    # ---- the end wall, seen from outside that end (y to the right when looking at +x, mirrored at -x)
    h, hole = end['h'], end['hole']
    yb = -W / 2 - 40                                   # bottom of the body on the sheet
    s = -end['side']                                   # looking at the +x end from outside, +y is on the left
    ax.plot(*rrect_xy(-W / 2, W / 2, yb, yb + h, 0).T, color='0.35', lw=0.6)
    for yy in (-(W / 2 - R), W / 2 - R):               # where the rounded corners start (the flat face between)
        ax.plot([yy, yy], [yb, yb + h], color='0.6', lw=0.3, ls='--')
    ax.plot([0, 0], [yb - 2, yb + h + 2], color='0.6', lw=0.3, ls='-.')
    txt(-W / 2, yb + h + 5, end['label'], fs=8, weight='bold')
    txt(0, yb - 5, 'BOTTOM of the body (desk side)', ha='center', fs=7, weight='bold')
    txt(s * (W / 2 + 2), yb + h / 2, '+y', ha='left' if s > 0 else 'right', va='center', fs=6, color='0.4')
    if hole[0] == 'rect':
        _, hy0, hy1, hz0, hz1 = hole
        ax.plot(*rrect_xy(*sorted((s * hy0, s * hy1)), yb + hz0, yb + hz1, 0).T, color=RED, lw=0.5)
        for cx in ((hy0 + hy1) / 2 - (hy1 - hy0) / 4, (hy0 + hy1) / 2 + (hy1 - hy0) / 4):
            cross(ax, s * cx, yb + (hz0 + hz1) / 2)
        rows.append(f'end hole {hy1 - hy0:4.1f} x {hz1 - hz0:4.1f}  from the bottom {hz0:4.1f} .. {hz1:4.1f}  '
                    f'(top edge {h - hz1:.1f} below the body rim)  centred')
    else:
        _, hy, hz, hr = hole
        a = np.linspace(0, 2 * np.pi, 65)
        ax.plot(s * hy + hr * np.cos(a), yb + hz + hr * np.sin(a), color=RED, lw=0.5)
        cross(ax, s * hy, yb + hz)
        rows.append(f'end hole  dia {2 * hr:.1f}  centre {hz:.1f} from the bottom, centred')
    ruler(ax, txt, yb - 17)
    notes_block(ax, txt, yb - 32, [title, 'PRINT AT 100% / ACTUAL SIZE (no "fit to page", no scaling).'] + notes +
                [''] + rows, mono=rows)
    return save(fig, path)
