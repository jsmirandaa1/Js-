"""The Wealth Blueprint – motor de animação dos episódios longos (identidade visual fixa da marca).
Extraído do Ep. 001. Cada episódio importa este módulo, define CH (capítulos) e registra cenas com @shot.
  @shot(t0, chapter=None, trans='fade'|'cut', cam='push'|'pull'|'left'|'right'|'still')
Rodar: WORK=... python3 epXXX_build.py frames 12.0 60.0 | shots | render
"""
import cairo, json, math, random, subprocess, sys, os
from multiprocessing import Pool

WORK = os.environ.get('WORK', '/root/work/ep2')
W, H, FPS = 1920, 1080, 30
import soundfile as _sf
try:
    TL = json.load(open(f'{WORK}/tl3.json'))
    WD = json.load(open(f'{WORK}/w3.json'))
    DUR = _sf.info(f'{WORK}/voice3.wav').duration
except Exception:   # usado só como biblioteca (ex.: Shorts)
    TL, WD, DUR = [], [], 0.0


def T(i): return TL[i]['start']
def E(i): return TL[i]['end']


def WT(i, word, nth=0):
    lo, hi = T(i) - 1.2, E(i) + 0.4
    k = 0
    for x in WD:
        if lo <= x['s'] <= hi and word.lower() in x['w'].lower().strip(' .,?!:;'):
            if k == nth:
                return x['s']
            k += 1
    print('WARN word not found', i, word, file=sys.stderr)
    return T(i)


# ---------------------------------------------------------------- palette
BG0 = (0.024, 0.031, 0.047)
BG1 = (0.055, 0.075, 0.115)
GOLD = (0.83, 0.68, 0.42)
GOLD2 = (0.96, 0.86, 0.63)
GOLDD = (0.55, 0.43, 0.24)
IVORY = (0.95, 0.93, 0.89)
MUTED = (0.56, 0.60, 0.68)
SLATE = (0.25, 0.30, 0.38)
RED = (0.80, 0.38, 0.36)


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def sm(x): x = clamp(x); return x * x * (3 - 2 * x)
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3
def eio(x):
    x = clamp(x)
    return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def ap(g, t0, d=0.7): return sm((g - t0) / d)
def lerp(a, b, t): return a + (b - a) * t
def vis(g, t0, t1=None, fi=0.7, fo=0.6):
    a = ap(g, t0, fi)
    if t1 is not None:
        a = min(a, 1 - ap(g, t1, fo))
    return a


# ---------------------------------------------------------------- text
FONTS = {
    'serif': ('Playfair Display', 0, 1), 'serifi': ('Playfair Display', 1, 0),
    'serifm': ('Playfair Display SemiBold', 0, 0),
    'light': ('Inter Light', 0, 0), 'reg': ('Inter', 0, 0), 'med': ('Inter Medium', 0, 0),
    'semi': ('Inter SemiBold', 0, 0), 'bold': ('Inter', 0, 1), 'xb': ('Inter ExtraBold', 0, 0),
}


def font(c, f, size):
    fam, sl, w = FONTS[f]
    c.select_font_face(fam, cairo.FONT_SLANT_ITALIC if sl else cairo.FONT_SLANT_NORMAL,
                       cairo.FONT_WEIGHT_BOLD if w else cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size)


def tw(c, s, f, size, track=0):
    font(c, f, size)
    return c.text_extents(s).x_advance + track * max(0, len(s) - 1)


def text(c, s, x, y, size, f='reg', col=IVORY, a=1.0, align='c', track=0):
    if a <= 0.003 or not s:
        return 0
    w = tw(c, s, f, size, track)
    x0 = x - w / 2 if align == 'c' else (x - w if align == 'r' else x)
    c.set_source_rgba(*col, a)
    if track == 0:
        c.move_to(x0, y); c.show_text(s)
    else:
        xx = x0
        for ch in s:
            c.move_to(xx, y); c.show_text(ch)
            xx += c.text_extents(ch).x_advance + track
    c.new_path()
    return w


def runs(c, rs, x, y, a=1.0, align='c'):
    """rs: list of (str, font, size, col). Mixed-font line."""
    total = sum(tw(c, s, f, sz) for s, f, sz, col in rs)
    xx = x - total / 2 if align == 'c' else (x - total if align == 'r' else x)
    for s, f, sz, col in rs:
        text(c, s, xx, y, sz, f, col, a, 'l')
        xx += tw(c, s, f, sz)
    return total


def rtext(c, s, x, y, size, f, col, g, t0, t1=None, rise=18, d=0.8, align='c', track=0, amax=1.0):
    a = vis(g, t0, t1, d) * amax
    if a <= 0.003:
        return
    text(c, s, x, y + (1 - eo((g - t0) / d)) * rise, size, f, col, a, align, track)


def wrap(c, s, maxw, f, size):
    words, lines, cur = s.split(), [], ''
    for w_ in words:
        t = (cur + ' ' + w_).strip()
        if tw(c, t, f, size) > maxw and cur:
            lines.append(cur); cur = w_
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


def para(c, s, x, y, size, f, col, g, t0, t1=None, maxw=1300, lh=1.35, align='c', rise=18, amax=1.0):
    for k, ln in enumerate(wrap(c, s, maxw, f, size)):
        rtext(c, ln, x, y + k * size * lh, size, f, col, g, t0 + k * 0.08, t1, rise, align=align, amax=amax)


def money(v, dec=False):
    return ('$' + f'{v:,.2f}') if dec else ('$' + f'{v:,.0f}')


# ---------------------------------------------------------------- shapes
def rrect(c, x, y, w, h, r):
    c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    c.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    c.close_path()


def glass(c, x, y, w, h, r=22, a=1.0, border=GOLD, ba=0.55):
    rrect(c, x, y, w, h, r)
    gr = cairo.LinearGradient(x, y, x, y + h)
    gr.add_color_stop_rgba(0, 1, 1, 1, 0.075 * a)
    gr.add_color_stop_rgba(1, 1, 1, 1, 0.025 * a)
    c.set_source(gr); c.fill_preserve()
    gb = cairo.LinearGradient(x, y, x + w, y + h)
    gb.add_color_stop_rgba(0, *border, ba * a)
    gb.add_color_stop_rgba(0.5, *border, 0.12 * a)
    gb.add_color_stop_rgba(1, *border, ba * 0.8 * a)
    c.set_source(gb); c.set_line_width(1.6); c.stroke()


def line(c, x0, y0, x1, y1, col, a=1, w=2):
    c.set_source_rgba(*col, a); c.set_line_width(w)
    c.move_to(x0, y0); c.line_to(x1, y1); c.stroke()


def gline(c, x, y, w, g, t0, a=1.0, col=GOLD, lw=1.5):
    """gold rule that draws from center"""
    p = eio((g - t0) / 0.9)
    if p <= 0:
        return
    line(c, x - w / 2 * p, y, x + w / 2 * p, y, col, a, lw)


def strike(c, x, y, w, p, col=RED, a=1.0, lw=3):
    if p > 0:
        line(c, x - w / 2, y, x - w / 2 + w * p, y, col, a, lw)


def check(c, x, y, r, a, p=1.0):
    c.set_source_rgba(*GOLD, 0.18 * a); c.arc(x, y, r, 0, 2 * math.pi); c.fill()
    c.set_source_rgba(*GOLD, a); c.set_line_width(2); c.arc(x, y, r, 0, 2 * math.pi); c.stroke()
    c.set_line_width(3.2); c.set_line_cap(cairo.LINE_CAP_ROUND)
    pts = [(x - r * .42, y + r * .02), (x - r * .1, y + r * .34), (x + r * .45, y - r * .3)]
    c.move_to(*pts[0])
    if p < 0.4:
        q = p / 0.4; c.line_to(lerp(pts[0][0], pts[1][0], q), lerp(pts[0][1], pts[1][1], q))
    else:
        q = (p - 0.4) / 0.6
        c.line_to(*pts[1]); c.line_to(lerp(pts[1][0], pts[2][0], q), lerp(pts[1][1], pts[2][1], q))
    c.stroke(); c.set_line_cap(cairo.LINE_CAP_BUTT)


def cross(c, x, y, r, col=RED, a=1):
    c.set_source_rgba(*col, a); c.set_line_width(3)
    c.move_to(x - r, y - r); c.line_to(x + r, y + r); c.move_to(x + r, y - r); c.line_to(x - r, y + r); c.stroke()


def glow(c, x, y, r, col=GOLD, a=0.25):
    c.new_path()
    gr = cairo.RadialGradient(x, y, 0, x, y, r)
    gr.add_color_stop_rgba(0, *col, a)
    gr.add_color_stop_rgba(1, *col, 0)
    c.set_source(gr); c.arc(x, y, r, 0, 2 * math.pi); c.fill()


# ---- line-art icons (centered at x,y, size s, stroke)
def icon(c, kind, x, y, s, a=1.0, col=GOLD, lw=2.4):
    if a <= 0.003:
        return
    c.save(); c.translate(x, y); c.scale(s / 100, s / 100)
    c.set_source_rgba(*col, a); c.set_line_width(lw * 100 / s)
    c.set_line_join(cairo.LINE_JOIN_ROUND); c.set_line_cap(cairo.LINE_CAP_ROUND)
    if kind == 'car':
        c.move_to(-48, 14); c.line_to(-48, -2); c.curve_to(-46, -8, -40, -10, -32, -11)
        c.line_to(-20, -26); c.curve_to(-16, -30, -10, -31, -4, -31); c.line_to(18, -31)
        c.curve_to(24, -31, 28, -29, 31, -25); c.line_to(40, -12); c.curve_to(46, -10, 50, -6, 50, 2)
        c.line_to(50, 14); c.close_path(); c.stroke()
        for wx in (-28, 28):
            c.new_sub_path(); c.arc(wx, 14, 11, 0, 2 * math.pi); c.stroke()
        c.move_to(-26, -12); c.line_to(-15, -25); c.line_to(4, -25); c.line_to(4, -12); c.close_path(); c.stroke()
        c.move_to(10, -12); c.line_to(10, -25); c.line_to(18, -25); c.line_to(30, -12); c.close_path(); c.stroke()
    elif kind == 'house':
        c.move_to(-42, -4); c.line_to(0, -40); c.line_to(42, -4); c.stroke()
        c.move_to(-32, -12); c.line_to(-32, 38); c.line_to(32, 38); c.line_to(32, -12); c.stroke()
        c.rectangle(-9, 10, 18, 28); c.stroke()
        c.rectangle(14, -4, 12, 12); c.stroke()
    elif kind == 'globe':
        c.arc(0, 0, 40, 0, 2 * math.pi); c.stroke()
        c.save(); c.scale(0.45, 1); c.arc(0, 0, 40, 0, 2 * math.pi); c.restore(); c.stroke()
        c.move_to(0, -40); c.line_to(0, 40); c.stroke()
        c.move_to(-40, 0); c.line_to(40, 0); c.stroke()
        c.move_to(-34, -20); c.line_to(34, -20); c.move_to(-34, 20); c.line_to(34, 20); c.stroke()
    elif kind == 'watch':
        c.arc(0, 0, 30, 0, 2 * math.pi); c.stroke()
        c.arc(0, 0, 24, 0, 2 * math.pi); c.stroke()
        c.move_to(0, 0); c.line_to(0, -16); c.move_to(0, 0); c.line_to(11, 6); c.stroke()
        c.rectangle(-14, -54, 28, 22); c.stroke(); c.rectangle(-14, 32, 28, 22); c.stroke()
        c.move_to(31, -4); c.line_to(37, -4); c.line_to(37, 4); c.line_to(31, 4); c.stroke()
    elif kind == 'palm':
        c.move_to(-4, 44); c.curve_to(-2, 10, 4, -10, 10, -26); c.stroke()
        for ang, ln in ((-160, 40), (-130, 36), (-60, 38), (-20, 42), (-95, 30)):
            r = math.radians(ang)
            c.move_to(10, -26); c.curve_to(10 + math.cos(r) * ln * .5, -26 + math.sin(r) * ln * .5 - 10,
                                           10 + math.cos(r) * ln, -26 + math.sin(r) * ln - 4,
                                           10 + math.cos(r) * ln, -26 + math.sin(r) * ln + 12)
            c.stroke()
        c.move_to(-44, 44); c.line_to(44, 44); c.stroke()
    elif kind == 'shield':
        c.move_to(0, -44); c.line_to(36, -30); c.curve_to(36, 6, 24, 30, 0, 46)
        c.curve_to(-24, 30, -36, 6, -36, -30); c.close_path(); c.stroke()
        c.move_to(-14, 0); c.line_to(-3, 12); c.line_to(17, -12); c.stroke()
    elif kind == 'bolt':
        c.move_to(6, -44); c.line_to(-22, 6); c.line_to(0, 6); c.line_to(-6, 44); c.line_to(22, -8)
        c.line_to(0, -8); c.close_path(); c.stroke()
    elif kind == 'briefcase':
        rrect(c, -44, -22, 88, 60, 8); c.stroke()
        c.move_to(-14, -22); c.line_to(-14, -34); c.line_to(14, -34); c.line_to(14, -22); c.stroke()
        c.move_to(-44, 2); c.line_to(44, 2); c.stroke()
    elif kind == 'compass':
        c.arc(0, 0, 40, 0, 2 * math.pi); c.stroke()
        c.move_to(0, -26); c.line_to(9, 0); c.line_to(0, 26); c.line_to(-9, 0); c.close_path(); c.stroke()
    elif kind == 'chat':
        rrect(c, -46, -36, 92, 62, 14); c.stroke()
        c.move_to(-20, 26); c.line_to(-30, 44); c.line_to(-4, 26); c.stroke()
        for dx in (-20, 0, 20):
            c.new_sub_path(); c.arc(dx, -5, 4, 0, 2 * math.pi); c.fill()
    elif kind == 'bell':
        c.move_to(-30, 22); c.curve_to(-22, 12, -24, -4, -22, -14); c.curve_to(-18, -34, 18, -34, 22, -14)
        c.curve_to(24, -4, 22, 12, 30, 22); c.close_path(); c.stroke()
        c.move_to(-8, 30); c.curve_to(-6, 40, 6, 40, 8, 30); c.stroke()
    elif kind == 'person':
        c.arc(0, -26, 13, 0, 2 * math.pi); c.stroke()
        c.move_to(-26, 40); c.curve_to(-26, 6, -14, -6, 0, -6); c.curve_to(14, -6, 26, 6, 26, 40); c.stroke()
    elif kind == 'heart':
        c.move_to(0, 34); c.curve_to(-50, 0, -36, -40, 0, -18); c.curve_to(36, -40, 50, 0, 0, 34); c.stroke()
    c.restore()


def gear(c, x, y, r, teeth, rot, a, col=GOLD):
    c.save(); c.translate(x, y); c.rotate(rot)
    c.set_source_rgba(*col, a); c.set_line_width(2.4)
    n = teeth * 2
    for k in range(n * 2 + 1):
        ang = k / (n * 2) * 2 * math.pi
        rr = r if (k // 2) % 2 == 0 else r * 0.86
        px, py = rr * math.cos(ang), rr * math.sin(ang)
        c.line_to(px, py) if k else c.move_to(px, py)
    c.close_path()
    c.set_source_rgba(*col, 0.07 * a); c.fill_preserve()
    c.set_source_rgba(*col, a); c.stroke()
    c.arc(0, 0, r * 0.35, 0, 2 * math.pi); c.stroke()
    for k in range(6):
        ang = k / 6 * 2 * math.pi
        line(c, r * 0.35 * math.cos(ang), r * 0.35 * math.sin(ang), r * 0.74 * math.cos(ang), r * 0.74 * math.sin(ang), col, a * .6, 2)
    c.restore()


# ---------------------------------------------------------------- cached layers
_cache = {}


def bokeh_sprite():
    if 'bokeh' not in _cache:
        s = cairo.ImageSurface(cairo.FORMAT_ARGB32, 128, 128)
        c = cairo.Context(s)
        gr = cairo.RadialGradient(64, 64, 0, 64, 64, 64)
        gr.add_color_stop_rgba(0, *GOLD2, 1)
        gr.add_color_stop_rgba(0.55, *GOLD, 0.45)
        gr.add_color_stop_rgba(1, *GOLD, 0)
        c.set_source(gr); c.paint()
        _cache['bokeh'] = s
    return _cache['bokeh']


rnd = random.Random(7)
PARTS = [(rnd.uniform(0, W + 300), rnd.uniform(0, H), rnd.uniform(4, 16), rnd.uniform(0.12, 0.6),
          rnd.uniform(0, 6.28), rnd.uniform(0.04, 0.16)) for _ in range(34)]


def background(c, g, strength=1.0):
    c.set_source_rgb(*BG0); c.paint()
    gr = cairo.RadialGradient(W * .5, H * .42, 0, W * .5, H * .42, 1250)
    gr.add_color_stop_rgb(0, *BG1); gr.add_color_stop_rgb(1, *BG0)
    c.set_source(gr); c.paint()
    sp = bokeh_sprite()
    for x0, y0, vx, sc, ph, al in PARTS:
        x = (x0 + vx * g) % (W + 300) - 150
        y = y0 + math.sin(g * 0.13 + ph) * 40
        a = al * (0.65 + 0.35 * math.sin(g * 0.4 + ph)) * strength
        c.save(); c.translate(x, y); c.scale(sc, sc)
        c.set_source_surface(sp, -64, -64); c.paint_with_alpha(a); c.restore()


def vignette(c):
    if 'vig' not in _cache:
        s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        cc = cairo.Context(s)
        gr = cairo.RadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, W * 0.72)
        gr.add_color_stop_rgba(0, 0, 0, 0, 0)
        gr.add_color_stop_rgba(1, 0, 0, 0, 0.72)
        cc.set_source(gr); cc.paint()
        _cache['vig'] = s
    c.set_source_surface(_cache['vig']); c.paint()


def skyline(kind):
    key = 'sky_' + kind
    if key in _cache:
        return _cache[key]
    SW, SH = 2400, 1350
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, SW, SH)
    c = cairo.Context(s)
    r = random.Random(11 if kind == 'night' else 23)
    hz = SH * 0.70
    sky = cairo.LinearGradient(0, 0, 0, hz)
    if kind == 'night':
        for p, col in ((0, (0.012, 0.018, 0.04)), (0.6, (0.04, 0.055, 0.11)), (1, (0.16, 0.13, 0.2))):
            sky.add_color_stop_rgb(p, *col)
    else:
        for p, col in ((0, (0.07, 0.09, 0.18)), (0.45, (0.33, 0.24, 0.34)), (0.78, (0.85, 0.47, 0.36)), (1, (0.98, 0.76, 0.48))):
            sky.add_color_stop_rgb(p, *col)
    c.set_source(sky); c.rectangle(0, 0, SW, hz + 5); c.fill()
    if kind == 'night':
        for _ in range(260):
            x, y = r.uniform(0, SW), r.uniform(0, hz * 0.7)
            c.set_source_rgba(1, 1, 1, r.uniform(0.15, 0.7)); c.arc(x, y, r.uniform(0.6, 1.7), 0, 6.3); c.fill()
        glow(c, SW * 0.72, hz * 0.25, 140, (0.9, 0.9, 1.0), 0.10)
        c.set_source_rgba(0.95, 0.94, 0.88, 0.9); c.arc(SW * 0.72, hz * 0.25, 26, 0, 6.3); c.fill()
        gh = cairo.LinearGradient(0, hz - 260, 0, hz)
        gh.add_color_stop_rgba(0, 0.9, 0.55, 0.3, 0); gh.add_color_stop_rgba(1, 0.9, 0.55, 0.3, 0.16)
        c.set_source(gh); c.rectangle(0, hz - 260, SW, 260); c.fill()
    else:
        glow(c, SW * 0.55, hz, 700, (1.0, 0.8, 0.5), 0.55)
        glow(c, SW * 0.55, hz, 160, (1.0, 0.95, 0.8), 0.9)
    # building layers: far -> near
    layers = [(0.30, (0.20, 0.20, 0.30) if kind == 'night' else (0.50, 0.38, 0.45), 0.06, 1.0),
              (0.45, (0.10, 0.11, 0.17) if kind == 'night' else (0.28, 0.22, 0.30), 0.12, 0.9),
              (0.62, (0.035, 0.04, 0.065) if kind == 'night' else (0.12, 0.10, 0.15), 0.25, 0.8)]
    for li, (hmax, col, litp, wsc) in enumerate(layers):
        x = -40
        while x < SW + 40:
            bw = r.uniform(50, 150) * wsc
            bh = r.uniform(0.25, 1.0) ** 1.6 * hz * hmax + 40
            if r.random() < 0.07:
                bh *= 1.55
            top = hz - bh
            c.set_source_rgb(*col)
            c.rectangle(x, top, bw, bh + 400); c.fill()
            # setbacks / spire
            if r.random() < 0.35:
                sw = bw * r.uniform(0.45, 0.7); sh = r.uniform(20, 70)
                c.rectangle(x + (bw - sw) / 2, top - sh, sw, sh + 2); c.fill()
                if r.random() < 0.5:
                    c.move_to(x + bw / 2 - sw * 0.2, top - sh); c.line_to(x + bw / 2, top - sh - r.uniform(40, 120))
                    c.line_to(x + bw / 2 + sw * 0.2, top - sh); c.fill()
            # windows
            if li >= 1:
                wx, wy = 9 * wsc, 13 * wsc
                for yy in range(int(top + 12), int(hz + 400), int(wy + 6)):
                    for xx in range(int(x + 8), int(x + bw - 10), int(wx + 6)):
                        if r.random() < litp:
                            br = r.uniform(0.5, 1)
                            if kind == 'night':
                                c.set_source_rgba(1.0, 0.82, 0.52, br * (0.55 if li == 1 else 0.9))
                            else:
                                c.set_source_rgba(1.0, 0.8, 0.55, br * 0.35)
                            c.rectangle(xx, yy, wx * 0.6, wy * 0.55); c.fill()
                c.set_source_rgb(*col)
            if kind == 'dawn':
                c.set_source_rgba(1.0, 0.75, 0.45, 0.18 + 0.1 * li)
                c.rectangle(x + bw - 3, top, 3, bh); c.fill()
            x += bw + r.uniform(-8, 10)
    # river / reflection band
    ref = cairo.LinearGradient(0, hz + 150, 0, SH)
    if kind == 'night':
        ref.add_color_stop_rgba(0, 0.02, 0.025, 0.045, 0.0); ref.add_color_stop_rgba(1, 0.01, 0.012, 0.02, 0.95)
    else:
        ref.add_color_stop_rgba(0, 0.1, 0.08, 0.12, 0.0); ref.add_color_stop_rgba(1, 0.06, 0.05, 0.08, 0.95)
    c.set_source(ref); c.rectangle(0, hz + 150, SW, SH); c.fill()
    _cache[key] = s
    return s


def draw_sky(c, kind, g, t0, t1, z0=1.0, z1=1.08, px=0.0, py=0.0, a=1.0):
    s = skyline(kind)
    p = clamp((g - t0) / max(0.1, t1 - t0))
    z = lerp(z0, z1, p) * (W / 2400) * 1.02
    c.save()
    c.translate(W / 2 + px * p * 60, H / 2 + py * p * 40)
    c.scale(z * 1.25, z * 1.25)
    c.set_source_surface(s, -1200, -720)
    c.paint_with_alpha(a)
    c.restore()


def chapter_label(c, n, title, a):
    if a <= 0.003:
        return
    text(c, f'{n:02d}', 80, 78, 18, 'semi', GOLD, a * 0.85, 'l', 2)
    line(c, 112, 72, 152, 72, GOLD, a * 0.6, 1.2)
    text(c, title.upper(), 166, 78, 16, 'med', IVORY, a * 0.55, 'l', 3)



# ================================================================= shot registry
SH = []   # (t0, fn, chapter, trans, cam)
CH = {}
CX, CY = W / 2, H / 2


def shot(t0, chapter=None, trans='fade', cam='push'):
    def deco(fn):
        SH.append((t0, fn, chapter, trans, cam)); return fn
    return deco


def chapter_card(n, t0):
    @shot(t0)
    def card(c, g):
        glow(c, CX, CY, 700, GOLD, 0.07 * ap(g, t0, 1.2))
        rtext(c, f'CHAPTER {n}', CX, CY - 70, 22, 'semi', GOLD, g, t0 + 0.15, None, track=10)
        gline(c, CX, CY - 40, 140, g, t0 + 0.3)
        title = CH[n]
        rtext(c, title, CX, CY + 50, 66 if len(title) < 34 else 58, 'serif', IVORY, g, t0 + 0.35, None, rise=26)
    return card


def lerp_col(a, b, t): return tuple(lerp(a[i], b[i], t) for i in range(3))


def person(c, x, y, s, a=1.0, col=IVORY, fill=0.0, pose='stand'):
    """silhueta estilizada de pessoa (cabeça + tronco), base em (x,y), altura ~ s"""
    if a <= 0.003:
        return
    c.save(); c.translate(x, y); c.scale(s / 200, s / 200)
    c.new_path()
    c.arc(0, -165, 30, 0, 2 * math.pi)
    c.move_to(-58, 0); c.curve_to(-60, -70, -45, -118, 0, -122); c.curve_to(45, -118, 60, -70, 58, 0); c.close_path()
    if fill > 0:
        c.set_source_rgba(*col, a * fill); c.fill_preserve()
    c.set_source_rgba(*col, a); c.set_line_width(4.5); c.stroke()
    c.restore()


# ================================================================= renderer
XF = 0.7
CUT = 0.28


def shot_at(g):
    k = 0
    for i, s in enumerate(SH):
        if g >= s[0]:
            k = i
    return k


def _cam(c, g, fn, s0, s1, mode, punch=0.0):
    c.save()
    p = clamp((g - s0) / max(1, s1 - s0))
    z = {'push': 1.0 + 0.03 * p, 'pull': 1.035 - 0.03 * p}.get(mode, 1.02)
    dx = {'left': -50 * (p - 0.5), 'right': 50 * (p - 0.5)}.get(mode, 0)
    z += punch
    c.translate(CX + dx, CY); c.scale(z, z); c.translate(-CX, -CY)
    fn(c, g)
    c.restore()


def draw_frame(c, g):
    background(c, g)
    k = shot_at(g)
    t0, fn, ch, trans, cam = SH[k]
    t_end = SH[k + 1][0] if k + 1 < len(SH) else DUR + 1
    cha = 1 if ch else 0
    if k > 0 and trans == 'fade' and g < t0 + XF:
        pt0, pfn, pch, _, pcam = SH[k - 1]
        _cam(c, g, pfn, pt0, t0 + XF, pcam)
        a = sm((g - t0) / XF)
        c.push_group(); background(c, g); _cam(c, g, fn, t0, t_end, cam)
        c.pop_group_to_source(); c.paint_with_alpha(a)
        if pch and pch != ch:
            chapter_label(c, pch, CH[pch], 1 - a)
        cha = (a if ch else 0) if pch != ch else cha
    elif k > 0 and trans == 'cut' and g < t0 + CUT:
        q = (g - t0) / CUT
        _cam(c, g, fn, t0, t_end, cam, punch=0.05 * (1 - eo(q)))
        c.set_source_rgba(1, 0.97, 0.9, 0.08 * (1 - q)); c.paint()
    else:
        _cam(c, g, fn, t0, t_end, cam)
    if ch:
        chapter_label(c, ch, CH[ch], cha * ap(g, t0, 0.8) if (k > 0 and SH[k - 1][2] != ch) else cha)
    vignette(c)
    fa = min(ap(g, 0, 1.2), 1 - ap(g, DUR - 1.5, 1.5))
    if fa < 1:
        c.set_source_rgba(0, 0, 0, 1 - fa); c.paint()


def render_range(args):
    idx, f0, f1, out = args
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}',
                          '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
                          '-pix_fmt', 'yuv420p', '-tune', 'animation', out], stdin=subprocess.PIPE)
    for f in range(f0, f1):
        c.save(); draw_frame(c, f / FPS); c.restore()
        surf.flush(); p.stdin.write(bytes(surf.get_data()))
        if (f - f0) % 900 == 0:
            print(f'[{idx}] {f - f0}/{f1 - f0}', flush=True)
    p.stdin.close(); p.wait()
    return out


def main(argv):
    SH.sort(key=lambda x: x[0])
    mode = argv[1]
    if mode == 'frames':
        os.makedirs(f'{WORK}/frames', exist_ok=True)
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(surf)
        for s in argv[2:]:
            g = float(s); c.save(); draw_frame(c, g); c.restore()
            surf.write_to_png(f'{WORK}/frames/f_{g:07.2f}.png')
    elif mode == 'shots':
        for s in SH:
            print(f'{s[0]:7.2f} {s[1].__name__} {s[2]} {s[3]} {s[4]}')
    elif mode == 'render':
        N = int(DUR * FPS); P = int(os.environ.get('PROCS', '4'))
        os.makedirs(f'{WORK}/seg', exist_ok=True)
        step = math.ceil(N / P)
        jobs = [(i, i * step, min(N, (i + 1) * step), f'{WORK}/seg/seg{i}.mp4') for i in range(P)]
        with Pool(P) as pool:
            outs = pool.map(render_range, jobs)
        with open(f'{WORK}/seg/list.txt', 'w') as fh:
            for o in outs:
                fh.write(f"file '{o}'\n")
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', f'{WORK}/seg/list.txt',
                        '-c', 'copy', f'{WORK}/video_noaudio.mp4'], check=True)
        print('done')
