"""The machining positions of a Takachi case on one sheet (A4 landscape PDF, matplotlib, in Japanese): every face seen
from outside, dimensioned in chains from the outline's edges, the walls with the joint between the body and the cover.
What Takachi asked for after the per-face DXFs (drawing.py), which use this repo's own axes. No CadQuery, like
template.py. Sheet coordinates are mm from the top left corner, y down; text sizes are mm."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from template import RED, rrect_xy

BLUE, GREY = '#1565c0', '0.35'
FONT = 'IPAexGothic'                         # apt fonts-ipaexfont-gothic (TrueType, so the PDF embeds it)
W, H = 297.0, 210.0


def page():
    """A4 landscape axes in mm (y down) and txt(x, y, s, size=2.6, ha='center', color='k', rot=0)."""
    try:
        font_manager.findfont(FONT, fallback_to_default=False)
    except ValueError:
        raise SystemExit(f'position sheet: the font {FONT} is missing (apt install fonts-ipaexfont-gothic)')
    fig = plt.figure(figsize=(W / 25.4, H / 25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.set_aspect('equal')
    ax.axis('off')

    def txt(x, y, s, size=2.6, ha='center', color='k', rot=0):
        ax.text(x, y, s, fontsize=size / 0.3528, family=FONT, ha=ha, va='baseline', color=color, rotation=rot,
                rotation_mode='anchor')
    return fig, ax, txt


def num(v):
    return f'{v:.2f}'.rstrip('0').rstrip('.')


def _tick(ax, x, y):
    ax.plot([x - 0.7, x + 0.7], [y + 0.7, y - 0.7], color='k', lw=0.5)


def hdim(ax, txt, xs, y, ext=None, labels=None):
    """A chain of dimensions through the sheet x positions xs on the line y, extension lines from y = ext."""
    ax.plot([xs[0], xs[-1]], [y, y], color='k', lw=0.3)
    for x in xs:
        _tick(ax, x, y)
        if ext is not None:
            ax.plot([x, x], [ext, y + (1 if y > ext else -1)], color='k', lw=0.3)
    for i, (a, b) in enumerate(zip(xs, xs[1:])):
        txt((a + b) / 2, y - 0.7, labels[i] if labels else num(abs(b - a)), 2.4)


def vdim(ax, txt, ys, x, ext=None, labels=None):
    """The same down the line x through the sheet y positions ys, extension lines from x = ext."""
    ax.plot([x, x], [ys[0], ys[-1]], color='k', lw=0.3)
    for y in ys:
        _tick(ax, x, y)
        if ext is not None:
            ax.plot([ext, x + (1 if x > ext else -1)], [y, y], color='k', lw=0.3)
    for i, (a, b) in enumerate(zip(ys, ys[1:])):
        txt(x - 0.7, (a + b) / 2, labels[i] if labels else num(abs(b - a)), 2.4, rot=90)


def cut(ax, x0, x1, y0, y1, r=0, color=RED):
    """A cut (rounded rectangle) in sheet mm: red = to machine, BLUE = the cover's edge relieved (to discuss)."""
    ax.fill(*rrect_xy(x0, x1, y0, y1, r).T, facecolor='#fde8ea' if color == RED else '#e3f0fb', edgecolor=color, lw=0.8)


def wall(ax, txt, x0, y0, w, h, joint, title, left='', right='', parts=('カバー', 'ボディー')):
    """A wall w × h seen from outside with its top left corner at (x0, y0), the bottom = the floor's outside face,
    the body / cover joint dashed at the height `joint`. Returns the mappers (along the wall, height) -> sheet x, y."""
    px, py = (lambda a: x0 + a), (lambda z: y0 + h - z)
    txt(x0, y0 - 9.0, title, 3.2, 'left')
    ax.plot(*rrect_xy(x0, x0 + w, y0, y0 + h, 0).T, color='k', lw=0.8)
    ax.plot([x0, x0 + w], [py(joint)] * 2, color=GREY, lw=0.4, ls=(0, (4, 3)))
    txt(x0 - 1.2, py(h / 2) + 4, left, 2.2, 'right', GREY)
    txt(x0 + w + 1.2, py(h / 2) + 4, right, 2.2, 'left', GREY)
    txt(x0 + w + 1.2, py(joint) - 1.6, f'{parts[0]} {num(h - joint)}', 2.1, 'left', GREY)
    txt(x0 + w + 1.2, py(joint) + 3.0, f'{parts[1]} {num(joint)}', 2.1, 'left', GREY)
    return px, py


def notch(ax, px, py, a0, a1, z0, z1, r=0):
    """A notch in a wall() from the height z0, open at z1 (the body's top edge), its bottom corners rounded r."""
    t = np.radians(np.linspace(180, 90, 9))
    xs = [px(a0), *(px(a0) + r + r * np.cos(t)), *(px(a1) - r + r * np.cos(t - np.pi / 2)), px(a1)]
    ys = [py(z1), *(py(z0 + r) + r * np.sin(t)), *(py(z0 + r) + r * np.sin(t - np.pi / 2)), py(z1)]
    ax.fill(xs, ys, facecolor='#fde8ea', edgecolor='none')
    ax.plot(xs, ys, color=RED, lw=0.8)


def legend(ax, txt, y, joint):
    cut(ax, 8, 12, y - 2.2, y + 0.4)
    txt(13.5, y, '加工をお願いする箇所(貫通)', 2.7, 'left')
    cut(ax, 78, 82, y - 2.2, y + 0.4, color=BLUE)
    txt(83.5, y, 'カバーの縁の逃がし(カバーも同じ幅で加工。承認図 20042642 と同じ)', 2.7, 'left')
    ax.plot([190, 194], [y - 0.8] * 2, color=GREY, lw=0.4, ls=(0, (4, 3)))
    txt(195.5, y, f'ボディーとカバーの合わせ目(底面から {num(joint)})', 2.7, 'left')
