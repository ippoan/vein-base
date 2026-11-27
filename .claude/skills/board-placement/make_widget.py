"""Fill editor.html with a placement config (JSON) and print the widget code for show_widget.
    python3 .claude/skills/board-placement/make_widget.py .claude/skills/board-placement/configs/fp008_f13.json > /tmp/w.html
The config's outline / body may give `rrect` shorthands, expanded here into point lists:
    {"rrect": [x0, x1, y0, y1], "r": 12, "rtop": 2}  (rtop: the top corners' radius; y1 may be an expression like "ye")
"""
import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def rrect(x0, x1, y0, y1, r, rtop=None, n=8):
    rtop = r if rtop is None else rtop
    pts = []

    def arc(cx, cy, rr, a0, cyexpr=None):
        for k in range(n + 1):
            t = math.radians(a0 + 90 * k / n)
            x = round(cx + rr * math.cos(t), 3)
            dy = round(rr * math.sin(t), 3)
            pts.append([x, f'{cyexpr}+({dy})' if cyexpr else round(cy + dy, 3)])

    top = (lambda: f'({y1})-{rtop}') if isinstance(y1, str) else None
    arc(x1 - r, y0 + r, r, -90)
    if top:
        arc(x1 - rtop, None, rtop, 0, top()); arc(x0 + rtop, None, rtop, 90, top())
    else:
        arc(x1 - rtop, y1 - rtop, rtop, 0); arc(x0 + rtop, y1 - rtop, rtop, 90)
    arc(x0 + r, y0 + r, r, 180)
    return pts


def expand(v):
    if isinstance(v, dict) and 'rrect' in v:
        return rrect(*v['rrect'], v.get('r', 0), v.get('rtop'))
    return v


cfg = json.load(open(sys.argv[1]))
cfg['outline'] = expand(cfg['outline'])
if cfg.get('body'):
    cfg['body']['pts'] = expand(cfg['body']['pts'])
html = open(os.path.join(HERE, 'editor.html')).read()
print(html.replace('/*CONFIG*/', 'const CONFIG=' + json.dumps(cfg, ensure_ascii=False) + ';'))
