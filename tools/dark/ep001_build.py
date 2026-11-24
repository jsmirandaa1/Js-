"""The Wealth Blueprint – Ep. 001 "The First $100,000 Is the Hardest"
Motion graphics documentary renderer (pycairo -> ffmpeg).

Uso:
  WORK=/root/work/ep1 python3 ep001_build.py frames 12.5 60.0 200.0   # PNGs de teste
  WORK=/root/work/ep1 python3 ep001_build.py render                   # vídeo completo (sem áudio)
Precisa: WORK/tl3.json (frases com start/end), WORK/w3.json (palavras do Whisper), voice3.wav.
"""
import cairo, json, math, random, subprocess, sys, os
from multiprocessing import Pool

WORK = os.environ.get('WORK', '/root/work/ep1')
W, H, FPS = 1920, 1080, 30
TL = json.load(open(f'{WORK}/tl3.json'))
WD = json.load(open(f'{WORK}/w3.json'))
import soundfile as _sf
DUR = _sf.info(f'{WORK}/voice3.wav').duration


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


# ================================================================= SHOTS
SH = []   # (start, fn, chapter or None)


def shot(t0, chapter=None):
    def deco(fn):
        SH.append((t0, fn, chapter)); return fn
    return deco


CX, CY = W / 2, H / 2
CH = {1: 'Why the first $100,000 feels impossible', 2: 'The power of your first $100,000',
      3: 'Compound growth: the real game changer', 4: 'How to reach your first $100,000',
      5: 'The mindset shift', 6: 'The beginning'}

# ---------------- SCENE 1: HOOK
BANK_T = WT(0, 'bank') - 0.5


@shot(0.0)
def s_night(c, g):
    draw_sky(c, 'night', g, 0, BANK_T + 1, 1.0, 1.10, 0.4, -0.2)
    # window frame of a luxury apartment
    c.set_source_rgba(0.01, 0.012, 0.018, 0.97)
    for x in (W * 0.33, W * 0.67):
        c.rectangle(x - 9, 0, 18, H); c.fill()
    c.rectangle(0, H * 0.83, W, H * 0.17); c.fill()
    c.rectangle(0, 0, W, 34); c.fill()
    gr = cairo.LinearGradient(0, H * 0.83, 0, H)
    gr.add_color_stop_rgba(0, 0.9, 0.7, 0.4, 0.10); gr.add_color_stop_rgba(1, 0, 0, 0, 0)
    c.set_source(gr); c.rectangle(0, H * 0.83, W, H * 0.17); c.fill()
    for x in (W * 0.33, W * 0.67):
        line(c, x + 9, 34, x + 9, H * 0.83, GOLD, 0.10, 1.2)
    rtext(c, 'THE WEALTH BLUEPRINT', CX, H * 0.915, 18, 'semi', GOLD, g, 1.0, BANK_T - 0.4, 0, track=7, amax=0.8)


@shot(BANK_T)
def s_bank(c, g):
    a0 = 1.0
    focus = ap(g, T(4) - 0.2, 0.8)
    cx = lerp(W * 0.36, CX, eio((g - T(4) + 0.2) / 1.2))
    x, y, w, h = cx - 400, CY - 230, 800, 460
    glow(c, cx, CY, 650, GOLD, 0.06 + 0.10 * focus)
    glass(c, x, y, w, h, 28, a0)
    text(c, 'PRIVATE CHECKING  ••••  4821', x + 48, y + 72, 18, 'semi', MUTED, 1, 'l', 2)
    c.set_source_rgba(*GOLD, 0.9); c.arc(x + w - 70, y + 62, 14, 0, 6.3); c.fill()
    c.set_source_rgba(*GOLD2, 0.7); c.arc(x + w - 50, y + 62, 14, 0, 6.3); c.fill()
    text(c, 'Available balance', x + 48, y + 170, 26, 'light', IVORY, 0.8, 'l')
    p = eio((g - BANK_T - 0.4) / 3.2)
    v = 100000 * p
    text(c, money(v, True), x + 48, y + 290, 104, 'semi', IVORY, 1, 'l')
    # sparkline
    c.set_source_rgba(*GOLD, 0.9); c.set_line_width(2.5)
    for k in range(61):
        q = k / 60
        if q > p:
            break
        yy = y + h - 60 - (q ** 1.8) * 70 - math.sin(q * 19) * 6 * (1 - q)
        xx = x + 48 + q * (w - 96)
        c.line_to(xx, yy) if k else c.move_to(xx, yy)
    c.stroke()
    text(c, 'Updated just now', x + w - 48, y + 170, 18, 'reg', MUTED, 0.8, 'r')
    items = [(1, 'No debt'), (2, 'No financial stress'), (3, 'No living paycheck to paycheck')]
    for k, (i, s) in enumerate(items):
        a = vis(g, T(i) - 0.1, T(4) - 0.3, 0.5)
        yy = CY - 110 + k * 110
        if a > 0:
            check(c, W * 0.64, yy - 10, 24, a, clamp((g - T(i)) / 0.6))
            text(c, s, W * 0.64 + 50, yy, 40, 'light', IVORY, a, 'l')
    rtext(c, 'Just one hundred thousand dollars.', CX, CY + 330, 34, 'serifi', GOLD2, g, T(4) + 0.3, None)


@shot(T(5) - 0.4)
def s_mountain(c, g):
    t0 = T(5) - 0.4
    zoom = 1 + 0.05 * clamp((g - t0) / 8)
    c.save(); c.translate(CX, CY); c.scale(zoom, zoom); c.translate(-CX, -CY)
    base = H * 0.86
    for k, (col, a, pts) in enumerate([
        (SLATE, 0.35, [(0, 0.55), (0.12, 0.40), (0.25, 0.52), (0.38, 0.30), (0.5, 0.48), (0.7, 0.36), (0.85, 0.5), (1, 0.42)]),
        (SLATE, 0.6, [(0, 0.8), (0.18, 0.62), (0.32, 0.72), (0.5, 0.16), (0.66, 0.66), (0.82, 0.6), (1, 0.78)])]):
        c.move_to(0, H)
        for px, py in pts:
            c.line_to(px * W, py * H)
        c.line_to(W, H); c.close_path()
        gr = cairo.LinearGradient(0, H * 0.15, 0, H)
        gr.add_color_stop_rgba(0, *col, a); gr.add_color_stop_rgba(1, *BG0, a)
        c.set_source(gr); c.fill()
    # snow rim
    c.move_to(0.45 * W, 0.255 * H); c.line_to(0.5 * W, 0.16 * H); c.line_to(0.55 * W, 0.27 * H)
    c.set_source_rgba(*IVORY, 0.5); c.set_line_width(2); c.stroke()
    # dotted path
    p = eo((g - t0 - 0.5) / 4)
    pts = [(0.30 * W, base), (0.40 * W, 0.66 * H), (0.36 * W, 0.52 * H), (0.45 * W, 0.40 * H), (0.42 * W, 0.30 * H), (0.5 * W, 0.17 * H)]
    n = 80
    for k in range(int(n * p)):
        q = k / n * (len(pts) - 1); i = int(q); f = q - i
        px = lerp(pts[i][0], pts[i + 1][0], f); py = lerp(pts[i][1], pts[i + 1][1], f)
        if k % 2 == 0:
            c.set_source_rgba(*GOLD, 0.75); c.arc(px, py, 2.6, 0, 6.3); c.fill()
    # flag
    fa = ap(g, t0 + 0.6, 0.8)
    line(c, 0.5 * W, 0.17 * H, 0.5 * W, 0.17 * H - 70, IVORY, fa, 2)
    c.set_source_rgba(*GOLD, fa); c.move_to(0.5 * W, 0.17 * H - 70); c.line_to(0.5 * W + 70, 0.17 * H - 56)
    c.line_to(0.5 * W, 0.17 * H - 42); c.fill()
    glow(c, 0.5 * W, 0.17 * H - 50, 160, GOLD, 0.25 * fa)
    text(c, '$100K', 0.5 * W + 84, 0.17 * H - 46, 26, 'semi', GOLD2, fa, 'l')
    icon(c, 'person', 0.30 * W, base - 26, 40, ap(g, t0, 0.8), IVORY, 3)
    c.restore()
    para(c, 'For most people, reaching that number feels almost impossible.', CX, H * 0.93, 38, 'serifi', IVORY, g, T(5), T(6) - 0.3, 1500)
    rtext(c, "But here's something interesting.", CX, H * 0.93, 38, 'serifi', GOLD2, g, T(6), None)


@shot(T(7) - 0.4)
def s_first(c, g):
    a = vis(g, T(7) - 0.2, T(8) - 0.3)
    runs(c, [('Your first ', 'serif', 92, IVORY), ('$100,000', 'semi', 92, GOLD2)], CX, CY - 20, a)
    gline(c, CX, CY + 40, 520, g, T(7) + 0.3, a * 0.8)
    rtext(c, "may be one of the hardest financial milestones you'll ever achieve.", CX, CY + 110, 36, 'light', IVORY, g, WT(7, 'hardest') - 0.4, T(8) - 0.3, amax=0.9)
    rtext(c, 'Once you get there…', CX, CY - 160, 40, 'serifi', MUTED, g, T(8), None)
    rtext(c, 'something begins to change.', CX, CY - 100, 52, 'serif', IVORY, g, WT(8, 'something'), None)
    rtext(c, 'Not just the amount of money you have.', CX, CY + 40, 40, 'light', IVORY, g, T(9), None, amax=0.75)
    sw = tw(c, 'Not just the amount of money you have.', 'light', 40)
    strike(c, CX, CY + 28, sw + 20, eio((g - T(10) + 0.1) / 0.7), MUTED, 0.8, 2.5)
    rtext(c, 'The way money starts working for you.', CX, CY + 150, 58, 'serif', GOLD2, g, T(10) + 0.2, None)


@shot(T(11) - 0.4)
def s_agenda(c, g):
    rtext(c, 'IN THIS EPISODE', CX, CY - 250, 20, 'semi', GOLD, g, T(11) - 0.3, None, track=8)
    gline(c, CX, CY - 220, 160, g, T(11))
    items = [(T(11) + 0.1, '01', 'Why the first $100,000 is so difficult'),
             (WT(11, 'next') - 0.5, '02', 'Why the next $100,000 can become easier'),
             (WT(11, 'actually') - 0.6, '03', 'The real power of compound growth')]
    for k, (t, n, s) in enumerate(items):
        y = CY - 90 + k * 130
        a = ap(g, t, 0.7)
        if a <= 0:
            continue
        dx = (1 - eo((g - t) / 0.8)) * -40
        glass(c, CX - 560 + dx, y - 62, 1120, 100, 18, a, GOLD, 0.35)
        text(c, n, CX - 500 + dx, y + 2, 40, 'light', GOLD, a, 'l')
        text(c, s, CX - 410 + dx, y, 38, 'serifm', IVORY, a, 'l')


TITLE_T = E(11) + 0.4


@shot(TITLE_T)
def s_title(c, g):
    t0 = TITLE_T
    glow(c, CX, CY, 800, GOLD, 0.10 * ap(g, t0, 1.5))
    rtext(c, 'THE WEALTH BLUEPRINT', CX, CY - 170, 22, 'semi', GOLD, g, t0 + 0.2, None, track=10)
    rtext(c, 'EPISODE 001', CX, CY - 128, 18, 'med', MUTED, g, t0 + 0.4, None, track=8)
    rtext(c, 'The First', CX, CY - 10, 84, 'serif', IVORY, g, t0 + 0.6, None, rise=30)
    a = ap(g, t0 + 0.9, 0.9)
    text(c, '$100,000', CX, CY + 110 + (1 - eo((g - t0 - 0.9) / 0.9)) * 30, 132, 'semi', GOLD2, a)
    rtext(c, 'IS THE HARDEST', CX, CY + 190, 30, 'med', IVORY, g, t0 + 1.3, None, track=14, amax=0.9)
    gline(c, CX, CY + 230, 420, g, t0 + 1.5)


# ---------------- SCENE 2
@shot(T(12) - 0.5, 1)
def s_zero(c, g):
    rtext(c, "Let's start with the biggest problem.", CX, CY - 260, 34, 'serifi', MUTED, g, T(12), None)
    a = ap(g, T(12) + 0.4, 1.0)
    glow(c, CX, CY + 20, 380, GOLD, 0.12 * a)
    text(c, '$0', CX, CY + 90, 260, 'light', IVORY, a)
    rtext(c, 'STARTING FROM ZERO', CX, CY + 170, 22, 'semi', GOLD, g, T(13) - 0.2, None, track=9)
    para(c, 'Every dollar you save has to come from your own effort.', CX, CY + 260, 38, 'serifm', IVORY, g, WT(13, 'every') - 0.2, None, 1400)


@shot(T(14) - 0.4, 1)
def s_paycheck(c, g):
    x0, y0, bw, bh = CX - 700, CY - 20, 1400, 110
    a = ap(g, T(14) - 0.2, 0.7)
    rtext(c, 'You work.', CX - 260, CY - 260, 54, 'serif', IVORY, g, T(14), None)
    rtext(c, 'You get paid.', CX + 220, CY - 260, 54, 'serif', GOLD2, g, WT(14, 'get') - 0.1, None)
    # paycheck bar
    fill = eio((g - WT(14, 'paid')) / 0.9)
    if fill > 0:
        rrect(c, x0, y0, bw * fill, bh, 14)
        gr = cairo.LinearGradient(x0, 0, x0 + bw, 0)
        gr.add_color_stop_rgba(0, *GOLD, 0.95); gr.add_color_stop_rgba(1, *GOLD2, 0.95)
        c.set_source(gr); c.fill()
        text(c, 'MONTHLY PAYCHECK', x0, y0 - 24, 20, 'semi', MUTED, fill, 'l', 4)
    segs = [('Rent', 'rent', 0.40, (0.36, 0.40, 0.50)), ('Groceries', 'groceries', 0.15, (0.32, 0.36, 0.46)),
            ('Transport', 'transportation', 0.1125, (0.28, 0.32, 0.42)), ('Insurance', 'insurance', 0.0875, (0.25, 0.29, 0.38)),
            ('Other', 'expenses', 0.125, (0.22, 0.26, 0.34))]
    xx = x0
    for k, (lab, wd, fr, col) in enumerate(segs):
        t = WT(15, wd) - 0.15
        p = eio((g - t) / 0.6)
        if p > 0:
            ww = bw * fr * p
            c.save(); rrect(c, x0, y0, bw, bh, 14); c.clip()
            c.set_source_rgba(*col, 1); c.rectangle(xx, y0, ww, bh); c.fill()
            line(c, xx + ww, y0, xx + ww, y0 + bh, BG0, 1, 3)
            c.restore()
            text(c, lab, xx + bw * fr / 2, y0 + bh + 48, 26, 'med', IVORY, p * 0.85)
        xx += bw * fr
    la = ap(g, T(16) + 0.2, 0.7)
    if la > 0:
        lx = x0 + bw * 0.875
        glow(c, lx + bw * 0.0625, y0 + bh / 2, 200, GOLD, 0.35 * la)
        c.set_source_rgba(*GOLD2, la * (0.6 + 0.4 * math.sin(g * 4) ** 2)); c.set_line_width(3)
        rrect(c, lx + 3, y0 - 6, bw * 0.125 - 3, bh + 12, 12); c.stroke()
        text(c, "WHAT'S LEFT", lx + bw * 0.0625, y0 + bh + 110, 24, 'bold', GOLD2, la, 'c', 4)
    rtext(c, 'And whatever is left is what you can save.', CX, H - 120, 34, 'serifi', MUTED, g, T(16), None)


@shot(T(17) - 0.4, 1)
def s_ledger(c, g):
    x, y, w = CX - 520, CY - 300, 1040
    glass(c, x, y, w, 600, 26, ap(g, T(17) - 0.3))
    rows = [(T(17) + 0.3, 'Monthly income', 'after taxes', '$4,000', IVORY),
            (WT(18, 'expenses') - 0.2, 'Expenses', 'rent, food, transport…', '−$3,500', RED),
            (WT(18, 'save') - 0.1, 'Saved each month', '', '$500', GOLD2)]
    for k, (t, lab, sub, val, col) in enumerate(rows):
        yy = y + 120 + k * 120 + (30 if k == 2 else 0)
        a = ap(g, t, 0.6)
        text(c, lab, x + 70, yy, 38, 'reg', IVORY, a, 'l')
        if sub:
            text(c, sub, x + 70, yy + 36, 22, 'light', MUTED, a, 'l')
        text(c, val, x + w - 70, yy, 50, 'semi', col, a, 'r')
        if k == 1:
            gline(c, CX, yy + 75, w - 140, g, t + 0.5, a * 0.5, IVORY, 1.2)
    a = ap(g, T(19) - 0.1, 0.7)
    glow(c, CX, y + 520, 300, GOLD, 0.2 * a)
    runs(c, [('= ', 'light', 64, IVORY), ('$6,000', 'semi', 76, GOLD2), (' per year', 'light', 44, IVORY)], CX, y + 545 + (1 - eo((g - T(19)) / .8)) * 20, a)


@shot(T(20) - 0.4, 1)
def s_years(c, g):
    x0, x1, y = 260, W - 260, CY + 60
    years = 18
    a = ap(g, T(20) - 0.3, 0.6)
    line(c, x0, y + 70, x1, y + 70, MUTED, 0.5 * a, 1.5)
    for yr in range(0, years + 1, 2):
        xx = lerp(x0, x1, yr / years)
        line(c, xx, y + 64, xx, y + 76, MUTED, 0.6 * a, 1.5)
        text(c, str(yr), xx, y + 110, 22, 'reg', MUTED, a * 0.8)
    text(c, 'YEARS', x1, y + 150, 18, 'semi', MUTED, a * 0.7, 'r', 4)
    rrect(c, x0, y - 10, x1 - x0, 46, 23); c.set_source_rgba(1, 1, 1, 0.05 * a); c.fill()
    tgt = 100000 / 6000
    p = eio((g - WT(20, 'pace')) / max(1, (E(21) - WT(20, 'pace'))))
    yrs = tgt * p
    xx = lerp(x0, x1, yrs / years)
    if p > 0:
        rrect(c, x0, y - 10, max(46, xx - x0), 46, 23)
        gr = cairo.LinearGradient(x0, 0, x1, 0)
        gr.add_color_stop_rgba(0, *GOLDD, 0.9); gr.add_color_stop_rgba(1, *GOLD2, 0.95)
        c.set_source(gr); c.fill()
        text(c, money(6000 * yrs), xx, y - 40, 34, 'semi', IVORY, a * (1 - sm((p - 0.9) / 0.08)), 'c')
    fx = lerp(x0, x1, tgt / years)
    line(c, fx, y - 10, fx, y - 150, GOLD, a * 0.8, 2)
    c.set_source_rgba(*GOLD, a); c.move_to(fx, y - 150); c.line_to(fx + 46, y - 138); c.line_to(fx, y - 126); c.fill()
    text(c, '$100,000', fx + 56, y - 128, 26, 'semi', GOLD2, a, 'l')
    text(c, 'Saving $6,000 a year · no investment returns', CX, CY - 330, 26, 'light', MUTED, a)
    b = ap(g, T(21) - 0.1, 0.7)
    glow(c, CX, CY - 190, 360, GOLD, 0.12 * b)
    runs(c, [('16+', 'semi', 150, GOLD2), (' years', 'serif', 90, IVORY)], CX, CY - 150 + (1 - eo((g - T(21)) / .8)) * 24, b)
    rtext(c, 'That’s why the beginning feels so slow.', CX, H - 110, 34, 'serifi', IVORY, g, T(22), T(23) + 1.5, amax=0.85)
    rtext(c, 'Effort in. Progress… barely visible.', CX, H - 110, 34, 'serifi', MUTED, g, T(23) + 1.6, None)


@shot(T(24) - 0.4, 1)
def s_compare(c, g):
    rtext(c, 'This is where many people give up.', CX, CY - 270, 46, 'serif', IVORY, g, T(24), None)
    items = [('car', 'An expensive car', WT(25, 'car')), ('house', 'A beautiful house', WT(25, 'house')),
             ('globe', 'Traveling the world', WT(25, 'world'))]
    for k, (ic, lab, t) in enumerate(items):
        x = CX + (k - 1) * 440
        a = ap(g, t - 0.2, 0.6)
        dim = 1 - 0.55 * ap(g, WT(25, 'falling') - 0.2, 1.0)
        glow(c, x, CY, 200, GOLD, 0.10 * a * dim)
        icon(c, ic, x, CY - 10, 150, a * dim, GOLD, 2.2)
        text(c, lab, x, CY + 130, 30, 'light', IVORY, a * dim)
    rtext(c, '“I’m falling behind.”', CX, CY + 290, 52, 'serifi', IVORY, g, WT(25, 'falling') - 0.3, None)


@shot(T(26) - 0.4, 1)
def s_process(c, g):
    rtext(c, "Building wealth isn't a competition.", CX, CY - 80, 56, 'serif', IVORY, g, T(26), None)
    p = eo((g - T(27) + 0.2) / 1.6)
    # staircase path
    if p > 0:
        c.set_source_rgba(*GOLD, 0.8); c.set_line_width(2.5)
        n = 7; sx, sy, st = CX - 420, CY + 260, 120
        pts = [(sx, sy)]
        for k in range(n):
            pts.append((sx + k * st + st, pts[-1][1])); pts.append((pts[-1][0], pts[-1][1] - 26))
        tot = len(pts) - 1
        upto = p * tot
        c.move_to(*pts[0])
        for k in range(1, len(pts)):
            if k <= upto:
                c.line_to(*pts[k])
            else:
                f = upto - (k - 1)
                if f > 0:
                    c.line_to(lerp(pts[k - 1][0], pts[k][0], f), lerp(pts[k - 1][1], pts[k][1], f))
                break
        c.stroke()
    rtext(c, "It's a process.", CX, CY + 70, 84, 'serifi', GOLD2, g, T(27) - 0.1, None)


# ---------------- chapter cards
def chapter_card(n, t0):
    @shot(t0)
    def card(c, g):
        glow(c, CX, CY, 700, GOLD, 0.07 * ap(g, t0, 1.2))
        rtext(c, f'CHAPTER {n}', CX, CY - 70, 22, 'semi', GOLD, g, t0 + 0.15, None, track=10)
        gline(c, CX, CY - 40, 140, g, t0 + 0.3)
        title = CH[n]
        rtext(c, title, CX, CY + 50, 66 if len(title) < 34 else 58, 'serif', IVORY, g, t0 + 0.35, None, rise=26)
    return card


chapter_card(2, E(27) + 0.5)

# ---------------- SCENE 3
ROWY = [CY - 150, CY + 20, CY + 190]


@shot(T(28) - 0.6, 2)
def s_rows(c, g):
    rtext(c, 'Why that first $100,000 matters', CX, 200, 52, 'serif', IVORY, g, T(28) - 0.3, None)
    ha = ap(g, T(29) - 0.2, 0.6)
    for lab, x in (('INVESTED', 330), ('RETURN', 760), ('ONE YEAR OF GROWTH', 1080)):
        text(c, lab, x, 330, 18, 'semi', MUTED, ha * 0.8, 'l', 4)
    rows = [(T(29), WT(30, 'approximately'), 10000, 700), (T(32), WT(33, 'that'), 100000, 7000),
            (T(36), WT(37, 'represent'), 1000000, 70000)]
    hi7 = vis(g, T(34) - 0.1, T(36) - 0.3, 0.5)
    for k, (ta, tg, amt, gain) in enumerate(rows):
        y = ROWY[k] + 30
        a = ap(g, ta - 0.1, 0.6)
        if a <= 0:
            continue
        text(c, money(amt), 330, y, 62, 'semi', IVORY, a, 'l')
        ca = 0.7 + 0.3 * hi7
        if hi7 > 0:
            glow(c, 800, y - 20, 110, GOLD, 0.35 * hi7)
        text(c, '× 7%', 760, y, 46, 'light', GOLD2 if hi7 > 0.5 else IVORY, a * ca, 'l')
        p = eio((g - tg + 0.1) / 1.0)
        bw = 700 * gain / 70000 * p
        if p > 0:
            rrect(c, 1080, y - 44, max(8, bw), 48, 6)
            gr = cairo.LinearGradient(1080, 0, 1780, 0)
            gr.add_color_stop_rgba(0, *GOLDD, 1); gr.add_color_stop_rgba(1, *GOLD2, 1)
            c.set_source(gr); c.fill()
            tx = 1080 + max(8, bw) + 20
            val = '+' + money(gain * p)
            if tx + tw(c, val, 'semi', 40) > W - 60:
                text(c, val, 1080 + bw - 20, y - 6, 40, 'semi', BG0, a, 'r')
            else:
                text(c, val, tx, y - 6, 40, 'semi', GOLD2, a, 'l')
    rtext(c, 'Useful — but probably not life-changing.', CX, H - 90, 32, 'serifi', MUTED, g, T(31), T(32) - 0.3)
    b = vis(g, T(35) - 0.1, T(36) - 0.2, 0.5)
    if b > 0:
        rrect(c, 1520, ROWY[1] - 60, 160, 70, 35); c.set_source_rgba(*GOLD, 0.95 * b); c.fill()
        text(c, '10× more', 1600, ROWY[1] - 14, 28, 'bold', BG0, b)
    rtext(c, 'Same percentage. Ten times the money working for you.', CX, H - 90, 32, 'serifi', GOLD2, g, T(34), T(36) - 0.3)
    rtext(c, 'Hypothetical 7% annual return, for illustration only.', CX, H - 90, 24, 'light', MUTED, g, T(36), None, amax=0.8)


@shot(T(38) - 0.4, 2)
def s_volatile(c, g):
    rtext(c, 'Returns are never guaranteed.', CX, 210, 54, 'serif', IVORY, g, T(38), None)
    r = random.Random(5)
    vals = [0.12, 0.08, -0.11, 0.17, 0.05, -0.04, 0.21, 0.09, -0.18, 0.14, 0.11, 0.02, 0.16, -0.06, 0.1]
    x0, base, bw = CX - 720, CY + 120, 96
    line(c, x0 - 20, base, x0 + len(vals) * bw, base, MUTED, 0.5, 1.5)
    for k, v in enumerate(vals):
        t = T(38) + 0.2 + k * 0.12
        p = eo((g - t) / 0.6)
        if p <= 0:
            continue
        neg = v < 0
        hl = 1.0 if not neg else (0.6 + 0.4 * ap(g, T(39), 0.5))
        hh = v * 1100 * p
        col = RED if neg else GOLD
        c.set_source_rgba(*col, 0.85 * hl)
        c.rectangle(x0 + k * bw + 14, base - max(hh, 0), bw - 28, abs(hh)); c.fill()
        text(c, f'{"+" if v > 0 else "−"}{abs(v) * 100:.0f}%', x0 + k * bw + bw / 2, base - hh - 16 if v > 0 else base - hh + 34, 20, 'med', col, p * hl)
    rtext(c, 'Some years can be negative.', CX - 330, H - 120, 34, 'serifi', RED, g, T(39) + 0.1, None)
    rtext(c, 'Taxes and fees matter.', CX + 360, H - 120, 34, 'serifi', IVORY, g, WT(39, 'taxes') - 0.2, None)


@shot(T(40) - 0.4, 2)
def s_engines(c, g):
    rtext(c, 'But the principle is important.', CX, CY - 40, 50, 'serifi', MUTED, g, T(40), T(41) - 0.2)
    para(c, 'The more capital you build, the more meaningful growth can become.', CX, CY - 40, 52, 'serif', IVORY, g, T(41), T(42) - 0.2, 1400)
    rtext(c, 'A SECOND ENGINE', CX, 190, 24, 'semi', GOLD, g, T(42), None, track=10)
    rtext(c, 'Your money starts working too.', CX, 260, 44, 'serif', IVORY, g, T(42) + 0.2, None)
    a1 = ap(g, T(43) - 0.1, 0.8); a2 = ap(g, T(44) - 0.1, 0.8)
    rot = g * 0.6
    r1, r2 = 170, 170
    gx1, gx2, gy = CX - 168, CX + 168, CY + 150
    gear(c, gx1, gy, r1, 12, rot * (1 if a2 > 0 else 0.5), a1, IVORY)
    gear(c, gx2, gy, r2, 12, -rot + math.pi / 24, a2, GOLD)
    if a2 > 0:
        glow(c, gx2, gy, 260, GOLD, 0.15 * a2)
    text(c, 'EARN', gx1, gy + 10, 30, 'bold', IVORY, a1, 'c', 4)
    text(c, 'your ability to work', gx1, gy + r1 + 60, 26, 'light', MUTED, a1)
    text(c, 'GROW', gx2, gy + 10, 30, 'bold', GOLD2, a2, 'c', 4)
    text(c, 'your capital, compounding', gx2, gy + r2 + 60, 26, 'light', MUTED, a2)


chapter_card(3, E(44) + 0.5)


# ---------------- SCENE 4
def fv(t): return 100000 * 1.07 ** t


@shot(T(45) - 0.6, 3)
def s_curve(c, g):
    rtext(c, "Here's where it gets interesting.", CX, 150, 44, 'serifi', MUTED, g, T(45) - 0.2, T(46))
    rtext(c, '$100,000 invested · 7% hypothetical average annual return · growth reinvested', CX, 150, 26, 'light', IVORY, g, T(46) + 0.2, None, amax=0.75)
    x0, x1, y0, y1 = 260, W - 300, H - 170, 250
    def X(t): return lerp(x0, x1, t / 20)
    def Y(v): return lerp(y0, y1, (v - 0) / 420000)
    a = ap(g, T(46), 0.8)
    for v in (100000, 200000, 300000, 400000):
        line(c, x0, Y(v), x1, Y(v), MUTED, 0.13 * a, 1)
        text(c, f'${v // 1000}K', x0 - 20, Y(v) + 7, 20, 'reg', MUTED, a * 0.8, 'r')
    for yr in (0, 5, 10, 15, 20):
        text(c, f'Year {yr}', X(yr), y0 + 40, 20, 'reg', MUTED, a * 0.8)
    line(c, x0, y0, x1, y0, MUTED, 0.5 * a, 1.5)
    # milestone head position
    ms = [(T(46) + 1.0, 0), (WT(48, 'year') , 1), (WT(49, 'five'), 5), (WT(50, '10'), 10), (WT(51, '20'), 20)]
    head = 0
    for k in range(1, len(ms)):
        tk, yk = ms[k]
        if g >= tk:
            prev = ms[k - 1][1]
            head = lerp(prev, yk, eio((g - tk) / 1.4))
    # contributed baseline
    ba = ap(g, T(46) + 0.6, 0.8)
    c.set_dash([10, 8]); line(c, x0, Y(100000), lerp(x0, x1, max(head, 0.01) / 20), Y(100000), IVORY, 0.55 * ba, 2); c.set_dash([])
    if head > 0.01:
        c.move_to(X(0), Y(100000))
        n = 120
        for k in range(n + 1):
            t = head * k / n
            c.line_to(X(t), Y(fv(t)))
        c.line_to(X(head), Y(100000)); c.close_path()
        gr = cairo.LinearGradient(0, Y(400000), 0, Y(100000))
        gr.add_color_stop_rgba(0, *GOLD, 0.35); gr.add_color_stop_rgba(1, *GOLD, 0.03)
        c.set_source(gr); c.fill()
        c.move_to(X(0), Y(100000))
        for k in range(n + 1):
            t = head * k / n
            c.line_to(X(t), Y(fv(t)))
        c.set_source_rgba(*GOLD2, 1); c.set_line_width(4); c.stroke()
        hx, hy = X(head), Y(fv(head))
        glow(c, hx, hy, 60, GOLD2, 0.6)
        c.set_source_rgba(*GOLD2, 1); c.arc(hx, hy, 7, 0, 6.3); c.fill()
    for tk, yk in ms[1:]:
        p = ap(g, tk + 0.9, 0.5)
        if p <= 0 or yk == 0:
            continue
        mx, my = X(yk), Y(fv(yk))
        c.set_source_rgba(*IVORY, p); c.arc(mx, my, 6, 0, 6.3); c.fill()
        lab = {1: '$107,000', 5: '$140,255', 10: '$196,715', 20: '$386,968'}[yk]
        dx = 0 if yk < 20 else -10
        text(c, lab, mx + dx, my - 34, 34 if yk == 20 else 28, 'semi', GOLD2 if yk == 20 else IVORY, p, 'c' if yk < 20 else 'r')
    # zero added label
    z = ap(g, T(52) - 0.1, 0.6)
    if z > 0:
        glass(c, x0 + 60, Y(250000) - 70, 520, 140, 18, z)
        text(c, '+$0', x0 + 110, Y(250000) + 18, 64, 'semi', GOLD2, z, 'l')
        text(c, 'added after day one', x0 + 260, Y(250000) + 10, 28, 'light', IVORY, z, 'l')
        text(c, 'GROWTH', X(16), Y(fv(16) / 2 + 50000) + 60, 22, 'bold', BG0, z * 0.8, 'c', 6)
        text(c, 'YOUR $100,000', X(4), Y(100000) + 34, 18, 'semi', IVORY, z * 0.7, 'c', 4)


def draw_tree(c, x, y, ang, ln, depth, p, maxd, leaves):
    # p in [0,1] growth progress across depth levels
    lvl = maxd - depth
    q = clamp(p * maxd - lvl)
    if q <= 0:
        return
    x2 = x + math.cos(ang) * ln * q
    y2 = y + math.sin(ang) * ln * q
    c.set_line_width(max(1.0, depth * 1.7))
    c.set_source_rgba(*lerp_col(GOLDD, GOLD2, lvl / maxd), 0.95)
    c.move_to(x, y); c.line_to(x2, y2); c.stroke()
    if depth <= 1:
        if q >= 1:
            leaves.append((x2, y2))
        return
    if q >= 1:
        sp = 0.42 + 0.04 * math.sin(depth * 3.1)
        draw_tree(c, x2, y2, ang - sp, ln * 0.76, depth - 1, p, maxd, leaves)
        draw_tree(c, x2, y2, ang + sp * 0.9, ln * 0.74, depth - 1, p, maxd, leaves)
        if depth % 3 == 0:
            draw_tree(c, x2, y2, ang + 0.05, ln * 0.6, depth - 1, p, maxd, leaves)


def lerp_col(a, b, t): return tuple(lerp(a[i], b[i], t) for i in range(3))


@shot(T(53) - 0.4, 3)
def s_tree(c, g):
    t0, t1 = T(53) - 0.2, E(55) + 0.5
    p = eio((g - t0) / (t1 - t0))
    leaves = []
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    draw_tree(c, CX + 360, H - 110, -math.pi / 2, 175, 10, p, 10, leaves)
    c.set_line_cap(cairo.LINE_CAP_BUTT)
    la = ap(g, t1 - 1.2, 1.4)
    for k, (lx, ly) in enumerate(leaves):
        tw_ = 0.6 + 0.4 * math.sin(g * 2 + k)
        c.set_source_rgba(*GOLD2, la * 0.8 * tw_); c.arc(lx, ly, 4.5, 0, 6.3); c.fill()
    # seed
    sa = 1 - ap(g, t0 + 1.0, 0.8)
    c.set_source_rgba(*GOLD2, sa); c.arc(CX + 360, H - 112, 9, 0, 6.3); c.fill()
    line(c, CX + 60, H - 108, CX + 660, H - 108, GOLD, 0.35, 1.5)
    L = 160
    rtext(c, 'COMPOUND GROWTH', L, CY - 200, 22, 'semi', GOLD, g, T(53), None, align='l', track=8)
    rtext(c, 'Returns', L, CY - 110, 62, 'serif', IVORY, g, T(54), None, align='l')
    rtext(c, 'that earn returns', L, CY - 30, 62, 'serif', IVORY, g, WT(54, 'those') - 0.2, None, align='l')
    rtext(c, 'that earn returns…', L, CY + 50, 62, 'serifi', GOLD2, g, WT(54, 'additional') - 0.2, None, align='l')
    rtext(c, 'Growth building on top of previous growth.', L, CY + 160, 32, 'light', IVORY, g, T(55), None, align='l', amax=0.85)


@shot(T(56) - 0.4, 3)
def s_time(c, g):
    rtext(c, "But there's one important detail.", CX, CY - 40, 44, 'serifi', MUTED, g, T(56), T(57) - 0.1)
    a = vis(g, T(57) - 0.1, T(58) - 0.3)
    text(c, 'The process takes', CX, CY - 10, 70, 'serif', IVORY, a)
    text(c, 'TIME', CX, CY + 110, 120, 'light', GOLD2, a * ap(g, WT(57, 'time') - 0.1, 0.6), 'c', 30)
    b = vis(g, T(58) - 0.1, T(60) - 0.4)
    if b > 0:
        text(c, 'Invest today', CX - 380, CY - 20, 58, 'serif', IVORY, b)
        p = eio((g - WT(59, 'wealthy') + 0.2) / 0.8)
        line(c, CX - 140, CY - 38, CX - 140 + 230 * ap(g, T(58) + 0.4, 0.7), CY - 38, GOLD, b, 2.5)
        text(c, 'Rich tomorrow', CX + 380, CY - 20, 58, 'serif', IVORY, b * ap(g, WT(59, 'wealthy') - 0.3, 0.5))
        strike(c, CX + 380, CY - 38, 420, eio((g - E(59) + 0.4) / 0.6), RED, b, 4)
        rtext(c, 'People want financial freedom immediately.', CX, CY + 150, 32, 'light', MUTED, g, T(58), None, amax=0.9 * b)
    words = [('Patience', WT(60, 'patience')), ('Consistency', WT(60, 'consistency')), ('Good decisions', WT(60, 'good'))]
    rtext(c, 'WEALTH BUILDING USUALLY REWARDS', CX, CY - 150, 22, 'semi', GOLD, g, T(60), None, track=8)
    for k, (wd, t) in enumerate(words):
        x = CX + (k - 1) * 520
        a = ap(g, t - 0.15, 0.6)
        if a > 0:
            glow(c, x, CY, 220, GOLD, 0.12 * a)
            text(c, wd, x, CY + 20 + (1 - eo((g - t) / .7)) * 20, 62, 'serif', GOLD2 if k == 0 else IVORY, a)


@shot(T(61) - 0.4, 3)
def s_bars(c, g):
    rtext(c, 'YEARS TO REACH EACH $100,000', CX, 160, 24, 'semi', GOLD, g, T(61) - 0.3, None, track=8)
    rtext(c, 'Investing the same $500 every month', CX, 225, 36, 'serif', IVORY, g, T(61) - 0.1, None)
    data = [('1st', 11.1), ('2nd', 6.2), ('3rd', 4.3), ('4th', 3.3), ('5th', 2.7)]
    base, scl, bw, gap = H - 190, 38, 170, 90
    tot = len(data) * bw + (len(data) - 1) * gap
    x0 = CX - tot / 2
    late = ap(g, T(62) - 0.1, 0.8)
    for k, (lab, yrs) in enumerate(data):
        t = T(61) + 0.1 + k * 0.45
        p = eio((g - t) / 0.9)
        x = x0 + k * (bw + gap)
        hh = yrs * scl * p
        hot = (k >= 2) * late
        col = lerp_col((0.38, 0.42, 0.52), GOLD, max(0.0 if k else 0, hot))
        if k == 0:
            col = (0.42, 0.46, 0.56)
        if hot > 0:
            glow(c, x + bw / 2, base - hh / 2, 220, GOLD, 0.18 * hot)
        rrect(c, x, base - hh, bw, max(hh, 1), 10); c.set_source_rgba(*col, 0.95); c.fill()
        text(c, f'{yrs * p:.1f} yrs', x + bw / 2, base - hh - 24, 36, 'semi', GOLD2 if hot > 0.5 else IVORY, ap(g, t, 0.5))
        text(c, f'{lab} $100K', x + bw / 2, base + 50, 26, 'med', MUTED, ap(g, t, 0.5))
    line(c, x0 - 40, base, x0 + tot + 40, base, MUTED, 0.5, 1.5)
    rtext(c, 'The early years feel slow.', CX - 420, 320, 34, 'serifi', MUTED, g, T(61), None, align='c')
    rtext(c, 'The later years get interesting.', CX + 420, 320, 34, 'serifi', GOLD2, g, T(62), None, align='c')
    text(c, 'Hypothetical example: $500/month at a 7% average annual return, compounded monthly. Not a guarantee of future results.', CX, H - 70, 19, 'light', MUTED, 0.7 * ap(g, T(61), 1))


chapter_card(4, E(62) + 0.5)


# ---------------- SCENE 5
def step_header(c, g, n, title, t0):
    a = ap(g, t0, 0.6)
    c.set_source_rgba(*GOLD, a); c.set_line_width(2); c.arc(160, 165, 34, 0, 6.3); c.stroke()
    text(c, f'{n:02d}', 160, 176, 28, 'semi', GOLD2, a)
    text(c, title, 220, 180, 44, 'serif', IVORY, a, 'l')


@shot(T(63) - 0.5, 4)
def s_steps(c, g):
    runs(c, [('So how do you reach your first ', 'serif', 56, IVORY), ('$100,000', 'semi', 56, GOLD2), ('?', 'serif', 56, IVORY)],
         CX, CY - 160, ap(g, T(63) - 0.2, 0.7))
    titles = ['Widen the gap', 'Grow your income', 'Invest consistently']
    for k, t in enumerate(titles):
        x = CX + (k - 1) * 480
        tt = T(64) + 0.2 + k * 0.35
        a = ap(g, tt, 0.6)
        if a <= 0:
            continue
        glass(c, x - 200, CY - 20, 400, 240, 22, a)
        text(c, f'0{k + 1}', x, CY + 90, 72, 'light', GOLD2, a)
        text(c, t, x, CY + 170, 32, 'serifm', IVORY, a)


@shot(T(65) - 0.4, 4)
def s_gap(c, g):
    step_header(c, g, 1, 'Widen the gap between earning and spending', T(65) - 0.3)
    x0 = 300
    grow = eio((g - WT(68, 'more') + 0.1) / 1.6)
    inc = lerp(1050, 1350, grow)
    spd = lerp(760, 1350, eio((g - WT(68, 'spend') + 0.1) / 1.6))
    a1 = ap(g, T(65) + 0.3, 0.7)
    y1, y2 = CY - 70, CY + 110
    text(c, 'INCOME', x0, y1 - 22, 20, 'semi', MUTED, a1, 'l', 4)
    rrect(c, x0, y1, inc * eio((g - T(65) - 0.3) / 1.0), 80, 12); c.set_source_rgba(*IVORY, 0.9 * a1); c.fill()
    a2 = ap(g, WT(65, 'spend') - 0.2, 0.7)
    text(c, 'SPENDING', x0, y2 - 22, 20, 'semi', MUTED, a2, 'l', 4)
    rrect(c, x0, y2, spd * eio((g - WT(65, 'spend') + 0.2) / 1.0), 80, 12); c.set_source_rgba(*SLATE, a2 * 1.4 if a2 < .7 else 1); c.fill()
    ga = ap(g, WT(65, 'spend') + 0.6, 0.8)
    gap_w = max(0, inc - spd)
    if ga > 0 and gap_w > 4:
        gx = x0 + spd
        c.save(); c.rectangle(gx, y1, gap_w, y2 + 80 - y1); c.clip()
        c.set_source_rgba(*GOLD, 0.18 * ga); c.paint()
        c.set_source_rgba(*GOLD, 0.6 * ga); c.set_line_width(2)
        for k in range(-20, 60):
            c.move_to(gx + k * 22, y1 - 10); c.line_to(gx + k * 22 - 260, y2 + 100)
        c.stroke(); c.restore()
        c.set_source_rgba(*GOLD2, ga); c.set_line_width(2.5); c.rectangle(gx, y1, gap_w, y2 + 80 - y1); c.stroke()
        text(c, 'YOUR GAP', gx + gap_w / 2, y2 + 140, 26, 'bold', GOLD2, ga * clamp(gap_w / 120), 'c', 5)
    rtext(c, "You don't need to get rich overnight. You need room.", CX, H - 110, 34, 'serifi', IVORY, g, T(66), T(68) - 0.2, amax=0.85)
    rtext(c, 'Earn more, spend more — no progress.', CX, H - 110, 36, 'serifi', RED, g, WT(68, 'everything') - 0.2, None)


@shot(T(69) - 0.4, 4)
def s_income(c, g):
    step_header(c, g, 2, 'Focus on increasing your income', T(69) - 0.3)
    # left: cutting has a floor
    la = ap(g, T(70) - 0.1, 0.7)
    lx = CX - 420
    shrink = eio((g - T(70) - 0.3) / 2.0)
    hh = lerp(420, 170, shrink)
    base = H - 210
    if la > 0:
        rrect(c, lx - 90, base - hh, 180, hh, 12); c.set_source_rgba(*SLATE, la); c.fill()
        c.set_dash([10, 8]); line(c, lx - 160, base - 170, lx + 160, base - 170, RED, la * 0.9, 2.5); c.set_dash([])
        text(c, 'LIMIT', lx + 170, base - 162, 20, 'bold', RED, la * 0.9, 'l', 4)
        text(c, 'Cutting expenses', lx, base + 50, 30, 'med', IVORY, la)
    ra = ap(g, T(71) - 0.1, 0.7)
    rx = CX + 380
    if ra > 0:
        up = eio((g - T(71)) / 2.6)
        c.set_source_rgba(*GOLD2, ra); c.set_line_width(4)
        pts = [(rx - 220, base), (rx - 140, base - 60), (rx - 80, base - 40), (rx, base - 170), (rx + 70, base - 140), (rx + 160, base - 380), (rx + 210, base - 560)]
        n = len(pts) - 1; upto = up * n
        c.move_to(*pts[0])
        for k in range(1, len(pts)):
            if k <= upto:
                c.line_to(*pts[k])
            else:
                f = upto - (k - 1)
                if f > 0:
                    c.line_to(lerp(pts[k - 1][0], pts[k][0], f), lerp(pts[k - 1][1], pts[k][1], f))
                break
        c.stroke()
        text(c, 'Earning potential', rx, base + 50, 30, 'med', GOLD2, ra)
        text(c, 'no fixed ceiling', rx, base + 90, 24, 'light', MUTED, ra)
    # chips
    chips = [('Valuable skills', WT(72, 'skills') - 0.4), ('Better opportunities', WT(72, 'better') - 0.2),
             ('A side business', WT(73, 'side') - 0.3), ('Additional income', WT(73, 'additional') - 0.3)]
    ca = 1 - ap(g, T(74) - 0.2, 0.5)
    for k, (lab, t) in enumerate(chips):
        a = ap(g, t, 0.5) * ca
        if a <= 0:
            continue
        x = CX + (k - 1.5) * 400
        y = 300
        glass(c, x - 180, y - 44, 360, 76, 38, a)
        icon(c, ['bolt', 'compass', 'briefcase', 'shield'][k] if k != 3 else 'bolt', x - 135, y - 6, 34, a, GOLD, 2.2)
        text(c, lab, x + 18, y + 4, 26, 'med', IVORY, a)
    rtext(c, 'Your income is your most powerful tool when you start from zero.', CX, 310, 36, 'serifi', GOLD2, g, T(74) + 0.4, None)


@shot(T(75) - 0.4, 4)
def s_invest(c, g):
    step_header(c, g, 3, 'Invest consistently — and understand it', T(75) - 0.3)
    # monthly auto transfers
    ma = vis(g, T(75) + 0.3, T(79) - 0.3)
    months = 'JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC'.split()
    for k, m in enumerate(months):
        x = 250 + k * 118
        p = ap(g, T(75) + 0.6 + k * 0.22, 0.4)
        c.set_source_rgba(*GOLD, 0.9 * p * ma); c.arc(x, 330, 26, 0, 6.3); c.fill()
        c.set_source_rgba(*MUTED, 0.4 * ma); c.set_line_width(1.5); c.arc(x, 330, 26, 0, 6.3); c.stroke()
        text(c, '+', x, 341, 30, 'semi', BG0, p * ma)
        text(c, m, x, 390, 16, 'semi', MUTED, ma * 0.8, 'c', 2)
    text(c, 'AUTOMATIC MONTHLY TRANSFER', CX, 270, 18, 'semi', GOLD, ma * 0.8, 'c', 6)
    items = [('Not money you need for rent', T(76) + 0.1, 'house'), ('Emergency fund first', WT(77, 'emergency') - 0.3, 'shield'),
             ('Know your risk tolerance', WT(77, 'risk') - 0.3, 'compass'), ('Fees · Taxes · Diversification', T(78) + 0.2, 'watch')]
    for k, (lab, t, ic) in enumerate(items):
        a = vis(g, t, T(79) - 0.3, 0.6)
        if a <= 0:
            continue
        y = 510 + k * 105
        check(c, 300, y - 10, 24, a, clamp((g - t) / 0.6))
        text(c, lab, 350, y, 38, 'light', IVORY, a, 'l')
    # scam notification
    na = vis(g, T(79), None, 0.5)
    if na > 0:
        dy = (1 - eo((g - T(79)) / 0.6)) * -60
        x, y, w, h = CX - 420, CY - 130 + dy, 840, 170
        rrect(c, x, y, w, h, 26); c.set_source_rgba(0.13, 0.14, 0.18, 0.96 * na); c.fill()
        text(c, 'INTERNET STRANGER  ·  now', x + 40, y + 52, 18, 'semi', MUTED, na, 'l', 3)
        text(c, '“This coin will make you rich. Guaranteed!”', x + 40, y + 115, 34, 'semi', IVORY, na, 'l')
        sp = eio((g - WT(79, 'rich') - 0.3) / 0.6)
        if sp > 0:
            cross(c, x + w - 60, y + 50, 18 * sp, RED, na)
            c.set_source_rgba(*RED, 0.9 * sp); c.set_line_width(3); rrect(c, x, y, w, h, 26); c.stroke()
    rtext(c, 'There is no guaranteed shortcut.', CX, CY + 220, 54, 'serif', IVORY, g, T(80), None)


@shot(T(81) - 0.4, 4)
def s_security(c, g):
    a = ap(g, T(81) - 0.1, 0.6)
    text(c, 'Look wealthy', CX - 400, CY + 20, 70, 'serif', MUTED, a)
    strike(c, CX - 400, CY - 4, tw(c, 'Look wealthy', 'serif', 70) + 30, eio((g - T(82) + 0.1) / 0.6), RED, a, 4)
    b = ap(g, T(82) - 0.1, 0.7)
    glow(c, CX + 420, CY - 20, 330, GOLD, 0.16 * b)
    icon(c, 'shield', CX + 420, CY - 150, 110, b, GOLD2, 2.6)
    text(c, 'Build real security', CX + 420, CY + 20, 70, 'serif', GOLD2, b)
    text(c, 'THE GOAL', CX, 230, 22, 'semi', GOLD, a, 'c', 10)


chapter_card(5, E(82) + 0.5)


# ---------------- SCENE 6
@shot(T(83) - 0.5, 5)
def s_dawn(c, g):
    draw_sky(c, 'dawn', g, T(83) - 0.5, E(85) + 1, 1.04, 1.12, -0.6, 0.2)
    gr = cairo.LinearGradient(0, H * 0.55, 0, H)
    gr.add_color_stop_rgba(0, 0, 0, 0, 0); gr.add_color_stop_rgba(1, 0, 0, 0, 0.75)
    c.set_source(gr); c.paint()
    para(c, 'Your relationship with money begins to change.', CX, H - 150, 46, 'serif', IVORY, g, WT(83, 'relationship') - 0.4, T(84) - 0.2, 1500)
    rtext(c, 'At first, you need every paycheck.', CX, H - 150, 46, 'serif', IVORY, g, T(84), T(85) - 0.2)
    runs(c, [('Then you start creating ', 'serif', 46, IVORY), ('options.', 'serifi', 50, GOLD2)], CX, H - 150, ap(g, T(85) + 0.2, 0.7))


@shot(T(86) - 0.4, 5)
def s_options(c, g):
    cards = [(T(86), 'bolt', 'Unexpected expense', 'Handled — without panic'),
             (T(87), 'briefcase', 'Career decisions', 'Made without feeling trapped'),
             (T(88), 'compass', 'Your future', 'Beyond the next 30 days')]
    rtext(c, 'OPTIONS', CX, 200, 24, 'semi', GOLD, g, T(86) - 0.3, None, track=12)
    for k, (t, ic, ti, sub) in enumerate(cards):
        x = CX + (k - 1) * 560
        a = ap(g, t - 0.1, 0.7)
        if a <= 0:
            continue
        dy = (1 - eo((g - t) / 0.8)) * 40
        glass(c, x - 240, CY - 220 + dy, 480, 470, 26, a)
        glow(c, x, CY - 80 + dy, 140, GOLD, 0.15 * a)
        icon(c, ic, x, CY - 80 + dy, 110, a, GOLD2, 2.4)
        text(c, ti, x, CY + 90 + dy, 38, 'serifm', IVORY, a)
        text(c, sub, x, CY + 150 + dy, 26, 'light', MUTED, a)


@shot(T(89) - 0.4, 5)
def s_notjust(c, g):
    rtext(c, "That's what building wealth is really about.", CX, CY - 230, 48, 'serif', IVORY, g, T(89) - 0.1, None)
    items = [('watch', 'Expensive watches', WT(90, 'watches')), ('car', 'Sports cars', WT(90, 'sports')), ('palm', 'Luxury vacations', WT(90, 'luxury'))]
    fade = 1 - 0.6 * ap(g, E(90) - 0.3, 0.8)
    rtext(c, "It's not just…", CX, CY - 120, 34, 'serifi', MUTED, g, T(90), None)
    for k, (ic, lab, t) in enumerate(items):
        x = CX + (k - 1) * 440
        a = ap(g, t - 0.3, 0.6) * fade
        icon(c, ic, x, CY + 60, 140, a, IVORY, 2.0)
        text(c, lab, x, CY + 200, 30, 'light', IVORY, a)


@shot(T(91) - 0.4, 5)
def s_freedom(c, g):
    a = ap(g, T(91) - 0.2, 1.0)
    glow(c, CX, CY - 60, 700, GOLD, 0.13 * a)
    sp = lerp(70, 34, eo((g - T(91) + 0.2) / 2.5))
    text(c, 'FREEDOM', CX, CY - 10, 170, 'serif', GOLD2, a, 'c', sp)
    gline(c, CX, CY + 50, 600, g, T(91) + 0.4, a)
    subs = [(T(92), 'to make your own decisions'), (T(93), 'to spend more time with the people you love'),
            (T(94), 'to build a life beyond your next paycheck')]
    for k, (t, s) in enumerate(subs):
        t1 = subs[k + 1][0] - 0.25 if k < 2 else None
        rtext(c, s, CX, CY + 150, 46, 'serifi', IVORY, g, t - 0.1, t1)


chapter_card(6, E(94) + 0.5)


# ---------------- SCENE 7
@shot(T(95) - 0.5, 6)
def s_final(c, g):
    t0 = T(95) - 0.5
    draw_sky(c, 'dawn', g, t0, E(101) + 2, 1.15, 1.02, 0.5, -0.3)
    c.set_source_rgba(0, 0, 0, 0.30 + 0.25 * ap(g, T(100), 1.2)); c.paint()
    rtext(c, 'Remember this:', CX, CY - 250, 34, 'serifi', GOLD2, g, T(95), T(98) - 0.3)
    runs(c, [('Your first ', 'serif', 60, IVORY), ('$100,000', 'semi', 60, GOLD2), (" won't magically make you rich.", 'serif', 60, IVORY)],
         CX, CY - 120, vis(g, T(96) - 0.1, T(98) - 0.3))
    para(c, 'But it can change the direction of your financial future.', CX, CY - 20, 46, 'serifi', IVORY, g, T(97), T(98) - 0.3, 1500)
    rtext(c, "Don't focus on looking wealthy.", CX, CY - 120, 54, 'serif', MUTED, g, T(98), T(100) - 0.3)
    rtext(c, 'Focus on becoming stronger every single year.', CX, CY - 20, 54, 'serif', IVORY, g, T(99), T(100) - 0.3)
    rtext(c, "The real goal isn't to impress people.", CX, CY - 200, 44, 'serifi', IVORY, g, T(100), None, amax=0.85)
    rtext(c, "It's a life where money gives you choices.", CX, CY - 130, 44, 'serifi', IVORY, g, T(101), None, amax=0.85)
    ba = ap(g, WT(101, 'choices') + 0.2, 1.2)
    if ba > 0:
        glow(c, CX, CY + 110, 700, GOLD, 0.16 * ba)
        text(c, '$100,000', CX, CY + 130 + (1 - eo((g - WT(101, 'choices') - 0.2) / 1.2)) * 30, 150, 'semi', GOLD2, ba)
        text(c, 'IS THE BEGINNING', CX, CY + 215, 40, 'serifm', GOLD, ba, 'c', 16)


@shot(T(102) - 0.4, 6)
def s_question(c, g):
    rtext(c, 'A question for you', CX, 240, 30, 'serifi', GOLD2, g, T(102), None)
    para(c, 'If you had to start from zero today, what would be your strategy to reach your first $100,000?', CX, CY - 60, 60, 'serif', IVORY, g, T(103) - 0.1, None, 1350)
    a = ap(g, T(104) - 0.2, 0.6)
    icon(c, 'chat', CX - 250, CY + 250, 70, a, GOLD2, 2.6)
    text(c, 'Tell me in the comments', CX + 50, CY + 262, 40, 'med', IVORY, a)


@shot(T(105) - 0.4, 6)
def s_end(c, g):
    t0 = T(105) - 0.4
    a = ap(g, t0, 0.8)
    # monogram
    my = 220
    c.set_source_rgba(*GOLD, a); c.set_line_width(2)
    c.rectangle(CX - 46, my - 46, 92, 92); c.stroke()
    c.rectangle(CX - 38, my - 38, 76, 76); c.stroke()
    text(c, 'WB', CX, my + 16, 40, 'serif', GOLD2, a)
    text(c, 'THE WEALTH BLUEPRINT', CX, my + 130, 44, 'serif', IVORY, a, 'c', 10)
    gline(c, CX, my + 170, 360, g, t0 + 0.4, a)
    # subscribe button
    b = ap(g, WT(105, 'subscribe') - 0.1, 0.6)
    pulse = 1 + 0.03 * math.sin(g * 5) * ap(g, WT(105, 'subscribe') + 0.5, 0.5)
    bx, by = CX, my + 290
    c.save(); c.translate(bx, by); c.scale(pulse, pulse)
    rrect(c, -170, -42, 340, 84, 42); c.set_source_rgba(*GOLD, b); c.fill()
    text(c, 'SUBSCRIBE', 18, 11, 28, 'bold', BG0, b, 'c', 4)
    icon(c, 'bell', -110, 0, 36, b, BG0, 3)
    c.restore()
    rtext(c, 'Stories, strategies and lessons about building wealth.', CX, my + 410, 30, 'light', MUTED, g, WT(105, 'stories') - 0.2, None)
    rtext(c, 'Understand money. Build wealth.', CX, H - 150, 46, 'serifi', GOLD2, g, T(106) - 0.1, None)
    # end screen placeholders area hint (kept clean: lower third free)


# ================================================================= renderer
SH.sort(key=lambda x: x[0])
XF = 0.7


def shot_at(g):
    k = 0
    for i, (t0, fn, ch) in enumerate(SH):
        if g >= t0:
            k = i
    return k


def chapter_alpha(g, k):
    t0, fn, ch = SH[k]
    return ch


def draw_frame(c, g):
    background(c, g)
    k = shot_at(g)
    t0, fn, ch = SH[k]
    t_end = SH[k + 1][0] if k + 1 < len(SH) else DUR + 1
    # camera
    def cam(fn_, s0, s1):
        c.save()
        p = clamp((g - s0) / max(1, s1 - s0))
        z = 1.0 + 0.025 * p
        c.translate(CX, CY); c.scale(z, z); c.translate(-CX, -CY)
        fn_(c, g)
        c.restore()
    if g < t0 + XF and k > 0:
        pt0, pfn, pch = SH[k - 1]
        cam(pfn, pt0, t0 + XF)
        a = sm((g - t0) / XF)
        c.push_group()
        background(c, g)
        cam(fn, t0, t_end)
        c.pop_group_to_source(); c.paint_with_alpha(a)
        cha = (a if ch else 0) if (pch != ch) else (1 if ch else 0)
        if pch and pch != ch:
            chapter_label(c, pch, CH[pch], 1 - a)
    else:
        cam(fn, t0, t_end)
        cha = 1 if ch else 0
    if ch:
        chapter_label(c, ch, CH[ch], cha * ap(g, t0, 0.8) if (k > 0 and SH[k - 1][2] != ch) else cha)
    vignette(c)
    # fade in / out
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
        g = f / FPS
        c.save(); draw_frame(c, g); c.restore()
        surf.flush()
        p.stdin.write(bytes(surf.get_data()))
        if (f - f0) % 900 == 0:
            print(f'[{idx}] {f - f0}/{f1 - f0}', flush=True)
    p.stdin.close(); p.wait()
    return out


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'frames':
        os.makedirs(f'{WORK}/frames', exist_ok=True)
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        c = cairo.Context(surf)
        for s in sys.argv[2:]:
            g = float(s)
            c.save(); draw_frame(c, g); c.restore()
            surf.write_to_png(f'{WORK}/frames/f_{g:07.2f}.png')
    elif mode == 'shots':
        for t0, fn, ch in SH:
            print(f'{t0:7.2f} {fn.__name__} {ch}')
    elif mode == 'render':
        N = int(DUR * FPS)
        P = int(os.environ.get('PROCS', '4'))
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
