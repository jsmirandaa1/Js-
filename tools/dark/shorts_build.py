"""The Wealth Blueprint – Shorts 9:16 (filmagem Pexels + gráficos + legenda palavra por palavra).

Uso:
  WORK=/root/work/shorts python3 shorts_build.py fetch 1        # baixa os clipes do Pexels do short 1
  WORK=/root/work/shorts python3 shorts_build.py render 1       # monta o short 1 -> WORK/out/short1.mp4
  WORK=/root/work/shorts python3 shorts_build.py frames 1 2.0 10.0   # quadros de teste
Precisa: WORK/v{n}.wav (narração), tl{n}.json (frases), w{n}.json (palavras do Whisper).
Pexels: a chave é injetada pelo proxy do ambiente (Network secret em api.pexels.com).
"""
import cairo, json, math, os, subprocess, sys, urllib.parse, urllib.request
import numpy as np, soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wb_audio

WORK = os.environ.get('WORK', '/root/work/shorts')
W, H, FPS = 1080, 1920, 30
END_CARD = 3.4
CX = W / 2

BG0 = (0.024, 0.031, 0.047); GOLD = (0.83, 0.68, 0.42); GOLD2 = (0.96, 0.86, 0.63)
IVORY = (0.97, 0.96, 0.93); MUTED = (0.62, 0.65, 0.72); RED = (0.86, 0.36, 0.34); GREEN = (0.55, 0.80, 0.55)

FONTS = {'serif': ('Playfair Display', 0, 1), 'serifi': ('Playfair Display', 1, 0), 'serifm': ('Playfair Display SemiBold', 0, 0),
         'light': ('Inter Light', 0, 0), 'reg': ('Inter', 0, 0), 'med': ('Inter Medium', 0, 0),
         'semi': ('Inter SemiBold', 0, 0), 'bold': ('Inter', 0, 1), 'xb': ('Inter ExtraBold', 0, 0)}


def clamp(x, a=0., b=1.): return max(a, min(b, x))
def sm(x): x = clamp(x); return x * x * (3 - 2 * x)
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3
def eio(x): x = clamp(x); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def ap(g, t0, d=0.4): return sm((g - t0) / d)
def lerp(a, b, t): return a + (b - a) * t
def vis(g, t0, t1=None, fi=0.35, fo=0.3):
    a = ap(g, t0, fi)
    return min(a, 1 - ap(g, t1, fo)) if t1 is not None else a


def font(c, f, size):
    fam, sl, w = FONTS[f]
    c.select_font_face(fam, cairo.FONT_SLANT_ITALIC if sl else cairo.FONT_SLANT_NORMAL,
                       cairo.FONT_WEIGHT_BOLD if w else cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size)


def tw(c, s, f, size, track=0):
    font(c, f, size); return c.text_extents(s).x_advance + track * max(0, len(s) - 1)


def text(c, s, x, y, size, f='reg', col=IVORY, a=1.0, align='c', track=0, shadow=0.0):
    if a <= 0.003 or not s:
        return 0
    w = tw(c, s, f, size, track)
    x0 = x - w / 2 if align == 'c' else (x - w if align == 'r' else x)
    def put(dx, dy, rgba):
        c.set_source_rgba(*rgba)
        xx = x0 + dx
        if track == 0:
            c.move_to(xx, y + dy); c.show_text(s)
        else:
            for ch in s:
                c.move_to(xx, y + dy); c.show_text(ch); xx += c.text_extents(ch).x_advance + track
    if shadow > 0:
        for d in (4, 2):
            put(0, d, (0, 0, 0, shadow * a * 0.45))
    put(0, 0, (*col, a))
    c.new_path()
    return w


def rrect(c, x, y, w, h, r):
    c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0); c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi); c.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    c.close_path()


def panel(c, x, y, w, h, a=1.0, r=26):
    rrect(c, x, y, w, h, r); c.set_source_rgba(0.02, 0.025, 0.04, 0.72 * a); c.fill_preserve()
    gb = cairo.LinearGradient(x, y, x + w, y + h)
    gb.add_color_stop_rgba(0, *GOLD, 0.7 * a); gb.add_color_stop_rgba(0.5, *GOLD, 0.15 * a); gb.add_color_stop_rgba(1, *GOLD, 0.55 * a)
    c.set_source(gb); c.set_line_width(2); c.stroke()


def glow(c, x, y, r, col=GOLD, a=0.25):
    c.new_path()
    gr = cairo.RadialGradient(x, y, 0, x, y, r)
    gr.add_color_stop_rgba(0, *col, a); gr.add_color_stop_rgba(1, *col, 0)
    c.set_source(gr); c.arc(x, y, r, 0, 2 * math.pi); c.fill()


def line(c, x0, y0, x1, y1, col, a=1, w=2):
    c.set_source_rgba(*col, a); c.set_line_width(w); c.move_to(x0, y0); c.line_to(x1, y1); c.stroke()


def money(v): return '$' + f'{v:,.0f}'


# ================================================================= timing helpers
class Short:
    def __init__(self, n):
        self.n = n
        self.tl = json.load(open(f'{WORK}/tl{n}.json'))
        self.wd = json.load(open(f'{WORK}/w{n}.json'))
        self.voice_dur = sf.info(f'{WORK}/v{n}.wav').duration
        self.dur = self.voice_dur + 0.5 + END_CARD
        self.end_t = self.voice_dur + 0.5
        self.words = self.align()

    def T(self, i): return self.tl[i]['start']
    def E(self, i): return self.tl[i]['end']

    def WT(self, i, word, nth=0):
        k = 0
        for w in self.words:
            if w['i'] == i and word.lower() in w['w'].lower().strip('.,?!:;"“”'):
                if k == nth:
                    return w['s']
                k += 1
        print('WARN word', self.n, i, word, file=sys.stderr)
        return self.T(i)

    def align(self):
        """legenda: palavras do roteiro com tempos do Whisper"""
        out = []
        for x in self.tl:
            disp = x['text'].split()
            ws = [w for w in self.wd if x['start'] - 0.35 <= (w['s'] + w['e']) / 2 <= x['end'] + 0.35]
            merged = []
            for w in ws:
                t = w['w']
                if merged and (t[:1] in ',.%' or t in ('K', "'s") or t.startswith(',')):
                    merged[-1]['e'] = w['e']; merged[-1]['w'] += t
                else:
                    merged.append(dict(w=t, s=w['s'], e=w['e']))
            if len(merged) == len(disp):
                for d, m in zip(disp, merged):
                    out.append(dict(w=d, s=m['s'], e=m['e'], i=x['i']))
            else:
                tot = sum(len(d) + 1 for d in disp); t = x['start']
                for d in disp:
                    dd = (x['end'] - x['start']) * (len(d) + 1) / tot
                    out.append(dict(w=d, s=t, e=t + dd, i=x['i'])); t += dd
        return out


# ================================================================= captions
def captions(c, S, g):
    """grupos de até 3 palavras (quebra em pontuação), palavra atual em dourado"""
    if g >= S.end_t - 0.2:
        return
    groups, cur = [], []
    for w in S.words:
        cur.append(w)
        if len(cur) >= 3 or w['w'][-1:] in '.,?!:' or (len(cur) >= 2 and len(' '.join(x['w'] for x in cur)) > 16):
            groups.append(cur); cur = []
    if cur:
        groups.append(cur)
    G = None
    for k, gr in enumerate(groups):
        nxt = groups[k + 1][0]['s'] if k + 1 < len(groups) else gr[-1]['e'] + 0.4
        if gr[0]['s'] - 0.05 <= g < min(nxt, gr[-1]['e'] + 0.6):
            G = gr
    if not G:
        return
    size = 84
    y = H * 0.70
    pop = eo((g - G[0]['s'] + 0.05) / 0.18)
    words = [w['w'] for w in G]
    widths = [tw(c, s, 'xb', size) for s in words]
    sp = 22
    total = sum(widths) + sp * (len(words) - 1)
    lines_ = [(words, widths)]
    if total > W - 140:
        h1 = (len(words) + 1) // 2
        lines_ = [(words[:h1], widths[:h1]), (words[h1:], widths[h1:])]
    idx = 0
    for li, (ws, wds) in enumerate(lines_):
        tot = sum(wds) + sp * (len(ws) - 1)
        x = CX - tot / 2
        yy = y + li * (size * 1.12) + (1 - pop) * 14
        for s, wdt in zip(ws, wds):
            wobj = G[idx]
            active = wobj['s'] - 0.03 <= g
            now = wobj['s'] - 0.03 <= g < wobj['e'] + 0.05
            col = GOLD2 if now else IVORY
            a = 1.0 if active else 0.55
            text(c, s, x, yy, size, 'xb', col, a * pop, 'l', 0, shadow=1.0)
            x += wdt + sp; idx += 1


# ================================================================= branding
def brand_top(c, g, S):
    a = 0.85 * ap(g, 0.2, 0.6) * (1 - ap(g, S.end_t - 0.4, 0.3))
    text(c, 'THE WEALTH BLUEPRINT', CX, 150, 24, 'semi', GOLD2, a, 'c', 7, shadow=0.8)


def hook_title(c, g, S, title):
    a = vis(g, 0.15, 2.6, 0.35, 0.4)
    if a <= 0:
        return
    font_size = 64
    lines_ = []
    cur = ''
    for w in title.upper().split():
        t = (cur + ' ' + w).strip()
        if tw(c, t, 'xb', font_size) > W - 160 and cur:
            lines_.append(cur); cur = w
        else:
            cur = t
    lines_.append(cur)
    y0 = 300
    for k, ln in enumerate(lines_):
        wdt = tw(c, ln, 'xb', font_size)
        rrect(c, CX - wdt / 2 - 22, y0 + k * 84 - 62, wdt + 44, 80, 10)
        c.set_source_rgba(0.02, 0.025, 0.04, 0.78 * a); c.fill()
        text(c, ln, CX, y0 + k * 84, font_size, 'xb', GOLD2 if k == len(lines_) - 1 else IVORY, a)


def end_card(c, g, S):
    t0 = S.end_t
    if g < t0 - 0.35:
        return
    fa = ap(g, t0 - 0.35, 0.35)
    c.set_source_rgba(0, 0, 0, fa); c.paint()
    a = ap(g, t0 + 0.15, 0.7)
    glow(c, CX, H * 0.46, 520, GOLD, 0.10 * a)
    c.set_source_rgba(*GOLD, a); c.set_line_width(2)
    c.rectangle(CX - 46, H * 0.36 - 46, 92, 92); c.stroke(); c.rectangle(CX - 38, H * 0.36 - 38, 76, 76); c.stroke()
    text(c, 'WB', CX, H * 0.36 + 15, 40, 'serif', GOLD2, a)
    text(c, 'THE WEALTH', CX, H * 0.47, 76, 'serif', GOLD2, a, 'c', 8)
    text(c, 'BLUEPRINT', CX, H * 0.47 + 92, 76, 'serif', GOLD2, a, 'c', 8)
    p = eio((g - t0 - 0.5) / 0.9)
    line(c, CX - 200 * p, H * 0.47 + 140, CX + 200 * p, H * 0.47 + 140, GOLD, a, 1.6)
    text(c, 'UNDERSTAND MONEY. BUILD WEALTH.', CX, H * 0.47 + 205, 26, 'med', IVORY, ap(g, t0 + 0.8, 0.6) * 0.85, 'c', 5)
    fo = ap(g, S.dur - 0.5, 0.5)
    if fo > 0:
        c.set_source_rgba(0, 0, 0, fo); c.paint()


# ================================================================= graphics (overlays on footage)
def g_counter(c, g, t0, t1, val, label='', y=H * 0.40, prefix=''):
    a = vis(g, t0, t1)
    if a <= 0:
        return
    v = val * eio((g - t0) / 1.0)
    glow(c, CX, y - 40, 420, (0, 0, 0), 0.55 * a)
    text(c, prefix + money(v), CX, y, 150, 'xb', GOLD2, a, shadow=1)
    if label:
        text(c, label, CX, y + 70, 30, 'semi', IVORY, a, 'c', 6, shadow=1)


def g_bars(c, g, t0, t1, rows, y=H * 0.30, title=''):
    """rows: [(label, value, t_show, color)] barras horizontais"""
    a = vis(g, t0, t1)
    if a <= 0:
        return
    x, w = 90, W - 180
    hh = 140 + len(rows) * 150
    panel(c, x, y, w, hh, a)
    if title:
        text(c, title, CX, y + 64, 26, 'semi', GOLD, a, 'c', 5)
    vmax = max(r[1] for r in rows)
    for k, (lab, v, ts, col) in enumerate(rows):
        yy = y + 130 + k * 150
        b = ap(g, ts, 0.4) * a
        if b <= 0:
            continue
        text(c, lab, x + 50, yy, 34, 'semi', IVORY, b, 'l')
        p = eio((g - ts - 0.1) / 0.9)
        bw = max(10, (w - 100) * v / vmax * p)
        rrect(c, x + 50, yy + 22, bw, 46, 8)
        gr = cairo.LinearGradient(x + 50, 0, x + w - 50, 0)
        gr.add_color_stop_rgba(0, *[cc * 0.7 for cc in col], b); gr.add_color_stop_rgba(1, *col, b)
        c.set_source(gr); c.fill()
        val = money(v * p)
        if bw > 260:
            text(c, val, x + 50 + bw - 18, yy + 58, 32, 'xb', BG0, b, 'r')
        else:
            text(c, val, x + 50 + bw + 18, yy + 58, 32, 'xb', col, b, 'l')


def g_curve(c, g, t0, t1, principal=1000, years=30, rate=0.07, y=H * 0.22, marks=(10, 20, 30)):
    a = vis(g, t0, t1)
    if a <= 0:
        return
    x, w, hh = 80, W - 160, 640
    panel(c, x, y, w, hh, a)
    text(c, f'{money(principal)} · {rate * 100:.0f}% HYPOTHETICAL / YEAR', CX, y + 60, 24, 'semi', GOLD, a, 'c', 4)
    px0, px1, py0, py1 = x + 60, x + w - 60, y + hh - 80, y + 130
    vmax = principal * (1 + rate) ** years
    def P(t): return lerp(px0, px1, t / years), lerp(py0, py1, (principal * (1 + rate) ** t) / vmax)
    line(c, px0, py0, px1, py0, MUTED, 0.5 * a, 1.5)
    p = eio((g - t0 - 0.3) / max(1.0, (t1 - t0) * 0.75))
    head = years * p
    c.move_to(*P(0))
    for k in range(101):
        c.line_to(*P(head * k / 100))
    c.line_to(P(head)[0], py0); c.line_to(px0, py0); c.close_path()
    gr = cairo.LinearGradient(0, py1, 0, py0)
    gr.add_color_stop_rgba(0, *GOLD, 0.45 * a); gr.add_color_stop_rgba(1, *GOLD, 0.02 * a)
    c.set_source(gr); c.fill()
    c.move_to(*P(0))
    for k in range(101):
        c.line_to(*P(head * k / 100))
    c.set_source_rgba(*GOLD2, a); c.set_line_width(5); c.stroke()
    hx, hy = P(head)
    glow(c, hx, hy, 50, GOLD2, 0.7 * a)
    for m in marks:
        if head >= m:
            mx, my = P(m)
            c.set_source_rgba(*IVORY, a); c.arc(mx, my, 7, 0, 6.3); c.fill()
            v = principal * (1 + rate) ** m
            text(c, money(v), mx - (10 if m == years else 0), my - 26, 34, 'xb', GOLD2 if m == years else IVORY, a, 'r' if m == years else 'c')
            text(c, f'YEAR {m}', mx, py0 + 40, 20, 'semi', MUTED, a, 'c', 3)


def g_stamp(c, g, t0, t1, word, col=RED, y=H * 0.40):
    a = vis(g, t0, t1, 0.15)
    if a <= 0:
        return
    s = 1 + 0.6 * (1 - eo((g - t0) / 0.25))
    c.save(); c.translate(CX, y); c.rotate(-0.12); c.scale(s, s)
    wdt = tw(c, word, 'xb', 110, 6)
    c.set_source_rgba(*col, a); c.set_line_width(8)
    rrect(c, -wdt / 2 - 36, -105, wdt + 72, 140, 14); c.stroke()
    text(c, word, 0, 0, 110, 'xb', col, a, 'c', 6)
    c.restore()


def g_vs(c, g, t0, t1, left, right, y=H * 0.30):
    a = vis(g, t0, t1)
    if a <= 0:
        return
    for k, (lab, sub, col) in enumerate((left, right)):
        b = ap(g, t0 + k * 0.6, 0.4) * a
        yy = y + k * 300
        panel(c, 110, yy, W - 220, 240, b)
        text(c, lab, CX, yy + 120, 58, 'xb', col, b)
        text(c, sub, CX, yy + 180, 28, 'med', IVORY, b * 0.85)
    b = ap(g, t0 + 0.3, 0.4) * a
    c.set_source_rgba(*GOLD, b); c.arc(CX, y + 270, 44, 0, 6.3); c.fill()
    text(c, 'VS', CX, y + 284, 34, 'xb', BG0, b)


def g_notif(c, g, t0, t1, app, msg, amount, y=H * 0.26):
    a = vis(g, t0, t1)
    if a <= 0:
        return
    dy = (1 - eo((g - t0) / 0.45)) * -80
    rrect(c, 70, y + dy, W - 140, 200, 36); c.set_source_rgba(0.12, 0.13, 0.16, 0.94 * a); c.fill()
    c.set_source_rgba(*GOLD, a); rrect(c, 110, y + dy + 40, 64, 64, 16); c.fill()
    text(c, '$', 142, y + dy + 88, 40, 'xb', BG0, a)
    text(c, app, 200, y + dy + 70, 26, 'semi', MUTED, a, 'l', 2)
    text(c, msg, 200, y + dy + 130, 38, 'semi', IVORY, a, 'l')
    text(c, amount, W - 110, y + dy + 130, 42, 'xb', GREEN, a, 'r')


def g_transfer(c, g, t0, t1, frm, to, amount, y=H * 0.28):
    a = vis(g, t0, t1)
    if a <= 0:
        return
    panel(c, 90, y, W - 180, 330, a)
    text(c, 'AUTOMATIC TRANSFER', CX, y + 62, 24, 'semi', GOLD, a, 'c', 5)
    text(c, frm, 250, y + 200, 38, 'semi', IVORY, a)
    text(c, to, W - 250, y + 200, 38, 'semi', GOLD2, a)
    p = (g - t0 - 0.3) % 1.4 / 1.4
    for k in range(5):
        q = (p + k / 5) % 1
        xx = lerp(400, W - 400, q)
        c.set_source_rgba(*GOLD2, a * math.sin(q * math.pi)); c.arc(xx, y + 188, 8, 0, 6.3); c.fill()
    text(c, amount, CX, y + 280, 44, 'xb', GOLD2, a)


def g_streams(c, g, t0, t1, labels, y=H * 0.24):
    """1 fonte de renda -> várias"""
    a = vis(g, t0, t1)
    if a <= 0:
        return
    panel(c, 80, y, W - 160, 620, a)
    text(c, 'YOU', CX, y + 560, 34, 'xb', IVORY, a, 'c', 4)
    n = len(labels)
    for k, lab in enumerate(labels):
        b = ap(g, t0 + 0.2 + k * 0.45, 0.4) * a
        if b <= 0:
            continue
        x = lerp(220, W - 220, k / max(1, n - 1)) if n > 1 else CX
        p = eio((g - t0 - 0.2 - k * 0.45) / 0.6)
        c.set_source_rgba(*GOLD2, b); c.set_line_width(4)
        c.move_to(x, y + 170); c.curve_to(x, y + 350, CX, y + 330, CX, lerp(y + 170, y + 510, p) if p < 1 else y + 510); c.stroke()
        c.set_source_rgba(*GOLD, b); c.arc(x, y + 140, 38, 0, 6.3); c.fill()
        text(c, '$', x, y + 154, 40, 'xb', BG0, b)
        text(c, lab, x, y + 225 + (k % 2) * 0 , 24, 'semi', IVORY, b)


def g_equation(c, g, t0, t1, rows, result, rcol, y=H * 0.28):
    a = vis(g, t0, t1)
    if a <= 0:
        return
    panel(c, 110, y, W - 220, 160 + len(rows) * 110, a)
    for k, (lab, val, col, ts) in enumerate(rows):
        b = ap(g, ts, 0.35) * a
        yy = y + 110 + k * 110
        text(c, lab, 170, yy, 40, 'med', IVORY, b, 'l')
        text(c, val, W - 170, yy, 52, 'xb', col, b, 'r')
    yy = y + 110 + len(rows) * 110 - 40
    rt, rlab = result
    b = ap(g, rt, 0.35) * a
    line(c, 170, yy - 30, W - 170, yy - 30, IVORY, 0.4 * b, 2)
    text(c, rlab, 170, yy + 40, 40, 'med', IVORY, b, 'l')


# ================================================================= specs (one per short)
def spec(S):
    T, E, WT = S.T, S.E, S.WT
    n = S.n
    # cuts: list of (start_time, pexels_query)   gfx: list of callables(c, g)
    if n == 1:
        cuts = [(0, 'counting dollar bills hands'), (T(1), 'new york city skyline night aerial'),
                (T(2), 'stock market chart screen'), (T(3), 'businessman looking at financial charts'),
                (T(4), 'gold coins stack'), (T(5), 'man writing financial plan notebook'),
                (T(6), 'putting coins in piggy bank'), (T(7), 'building construction timelapse'),
                (T(8), 'city sunrise timelapse'), (T(9), 'man walking up stairs'), (T(10), 'city aerial dusk')]
        gfx = [lambda c, g: g_counter(c, g, T(0) + 0.2, T(1) + 0.3, 100000, 'YOUR FIRST'),
               lambda c, g: g_bars(c, g, T(2) - 0.1, E(4) + 0.2, [('$10,000 invested', 700, WT(2, '$700') - 0.3, IVORY),
                                                                 ('$100,000 invested', 7000, WT(3, '$7,000') - 0.4, GOLD2)],
                                   title='ONE YEAR AT 7% (HYPOTHETICAL)'),
               lambda c, g: g_stamp(c, g, WT(4, 'Ten') - 0.1, E(4) + 0.2, '10×', GOLD2, H * 0.58)]
    elif n == 2:
        cuts = [(0, 'rich man in suit luxury'), (WT(1, 'Expensive') - 0.1, 'luxury sports car'),
                (WT(1, 'Designer') - 0.1, 'designer clothing store shopping'), (WT(1, 'Luxury') - 0.1, 'luxury watch close up'),
                (T(2), 'credit card payment terminal'), (T(3), 'man thinking by window city'),
                (T(4), 'shopping bags luxury woman'), (T(5), 'counting money hands dollars'),
                (T(6), 'man walking street ordinary'), (T(7), 'driving ordinary car road'),
                (WT(7, 'Lamborghini') - 0.6, 'lamborghini'), (T(8), 'saving coins jar')]
        gfx = [lambda c, g: g_stamp(c, g, WT(2, 'financed') - 0.1, E(2) + 0.4, 'FINANCED', RED),
               lambda c, g: g_vs(c, g, T(4) - 0.1, E(4) + 0.4, ('LOOKING WEALTHY', 'what people see', RED), ('BUILDING WEALTH', 'what actually matters', GOLD2))]
    elif n == 3:
        cuts = [(0, 'man sleeping bed night'), (T(1), 'gold coins'), (T(2), 'stock market data screen'),
                (T(3), 'person using banking app phone'), (T(4), 'stock market chart rising'),
                (T(5), 'plant growing timelapse'), (T(6), 'calendar pages'), (T(7), 'tree growing timelapse'),
                (T(8), 'young man studying laptop'), (T(9), 'city sunrise aerial')]
        gfx = [lambda c, g: g_curve(c, g, T(2), E(4) + 0.4, 1000, 30, 0.07, marks=(10, 20, 30)),
               lambda c, g: g_stamp(c, g, WT(6, 'thirty') - 0.2, E(6) + 0.2, '30 DAYS?', RED)]
    elif n == 4:
        cuts = [(0, 'businessman office skyscraper'), (T(1), 'man thinking'), (T(2), 'luxury shopping mall'),
                (T(3), 'empty wallet'), (T(4), 'woman budget planning saving money'), (T(5), 'family home sunset'),
                (T(6), 'salary paycheck money'), (T(7), 'calculator budget planning'), (T(8), 'man working laptop night'),
                (T(9), 'investment app phone')]
        gfx = [lambda c, g: g_bars(c, g, T(2) - 0.1, E(3) + 0.3, [('Earned', 10000, WT(2, 'earn') - 0.2, IVORY),
                                                                 ('Spent', 10000, WT(2, 'spend') - 0.2, RED)], title='EVERY MONTH'),
               lambda c, g: g_stamp(c, g, T(3) - 0.05, E(3) + 0.3, '$0 LEFT', RED, H * 0.60),
               lambda c, g: g_bars(c, g, T(4) - 0.1, E(5) + 0.3, [('Earned', 5000, T(4), IVORY),
                                                                 ('Saved & invested', 1000, WT(4, 'saving') - 0.2, GOLD2)], title='SOMEONE ELSE')]
    elif n == 5:
        cuts = [(0, 'office worker packing box'), (T(1), 'stressed man bills'), (T(2), 'office worker commute'),
                (T(3), 'working on laptop cafe'), (WT(4, 'small') - 0.2, 'small business shop owner'),
                (WT(4, 'freelancing') - 0.1, 'freelancer working laptop home'), (WT(4, 'digital') - 0.1, 'designer tablet digital'),
                (WT(4, 'skill') - 0.3, 'person learning skill workshop'), (T(5), 'man thinking'),
                (T(6), 'busy crowded city fast'), (T(7), 'woman working focused desk'), (T(8), 'opening door light'),
                (T(9), 'city aerial')]
        gfx = [lambda c, g: g_streams(c, g, T(2) - 0.1, E(2) + 0.2, ['PAYCHECK']),
               lambda c, g: g_streams(c, g, T(3) - 0.1, E(3) + 0.4, ['PAYCHECK', 'SIDE INCOME', 'SKILLS']),
               lambda c, g: g_stamp(c, g, WT(7, 'one') - 0.1, E(7), 'ONE', GOLD2, H * 0.40)]
    elif n == 6:
        cuts = [(0, 'shopping spending money'), (T(1), 'empty wallet'), (T(2), 'man writing notebook'),
                (T(3), 'phone notification hand'), (T(4), 'coins jar'), (T(5), 'online banking laptop'),
                (T(6), 'budget planning calculator'), (T(7), 'sunrise city'), (T(8), 'man running morning'),
                (T(9), 'piggy bank coins')]
        gfx = [lambda c, g: g_notif(c, g, T(3) + 0.1, E(3) + 0.2, 'BANK · NOW', 'Paycheck deposited', '+$3,000'),
               lambda c, g: g_transfer(c, g, T(5) - 0.1, E(6) + 0.2, 'Checking', 'Future', '$300 / month', H * 0.28)]
    else:
        cuts = [(0, 'man working late night office'), (T(1), 'luxury house exterior'), (T(2), 'modern office building'),
                (T(3), 'stock market screen'), (T(4), 'man working late desk lamp'), (T(5), 'closing wallet'),
                (T(6), 'business handshake'), (T(7), 'early morning workout'), (T(8), 'office routine work'),
                (T(9), 'clock time lapse'), (T(10), 'runner road sunrise'), (T(11), 'man looking at city sunrise'),
                (T(12), 'sunrise city aerial')]
        gfx = []
    return cuts, gfx


TITLES = {1: 'The First $100K Changes Everything', 2: 'Looking Rich Is Keeping You Poor', 3: 'The Magic of Compound Interest',
          4: 'Your Paycheck Is Not Your Wealth', 5: 'Stop Depending on One Income', 6: 'Pay Yourself First',
          7: 'Wealth Is Built in Silence'}


# ================================================================= Pexels
USED = f'{WORK}/clips/used.json'


def pexels_search(q, need):
    url = 'https://api.pexels.com/videos/search?' + urllib.parse.urlencode(dict(query=q, orientation='portrait', size='medium', per_page=20))
    req = urllib.request.Request(url, headers={'User-Agent': 'wb-shorts/1.0'})
    data = json.load(urllib.request.urlopen(req, timeout=30))
    used = set(json.load(open(USED))) if os.path.exists(USED) else set()
    best = None
    for v in data.get('videos', []):
        if v['id'] in used or v['duration'] < need:
            continue
        files = [f for f in v['video_files'] if f.get('width') and f['width'] >= 1080 and f['height'] > f['width']]
        if not files:
            continue
        f = min(files, key=lambda f: f['width'])
        best = (v['id'], f['link']); break
    if not best:   # relax: any portrait-ish file
        for v in data.get('videos', []):
            if v['id'] in used:
                continue
            files = sorted([f for f in v['video_files'] if f.get('width')], key=lambda f: -f['width'])
            if files:
                best = (v['id'], files[0]['link']); break
    return best


def fetch(S):
    os.makedirs(f'{WORK}/clips', exist_ok=True)
    cuts, _ = spec(S)
    times = [t for t, q in cuts] + [S.end_t]
    plan = []
    used = json.load(open(USED)) if os.path.exists(USED) else []
    for k, (t, q) in enumerate(cuts):
        need = times[k + 1] - t + 0.5
        r = pexels_search(q, need)
        if not r:
            print('NO RESULT', q); plan.append(None); continue
        vid, link = r
        path = f'{WORK}/clips/{vid}.mp4'
        if not os.path.exists(path):
            req = urllib.request.Request(link, headers={'User-Agent': 'wb-shorts/1.0'})
            with urllib.request.urlopen(req, timeout=120) as resp, open(path, 'wb') as fh:
                fh.write(resp.read())
        used.append(vid); json.dump(used, open(USED, 'w'))
        plan.append(dict(t=t, q=q, id=vid, path=path, url=f'https://www.pexels.com/video/{vid}/'))
        print(f'{t:6.2f} {q} -> {vid}')
    json.dump(plan, open(f'{WORK}/clips/plan{S.n}.json', 'w'), indent=1)


def build_footage(S):
    """monta a trilha de vídeo (cortes secos, zoom lento, grade dourado) -> footage{n}.mp4"""
    plan = json.load(open(f'{WORK}/clips/plan{S.n}.json'))
    times = [p['t'] if p else None for p in plan]
    cuts, _ = spec(S)
    bounds = [t for t, q in cuts] + [S.dur]
    segs = []
    os.makedirs(f'{WORK}/tmp', exist_ok=True)
    for k, p in enumerate(plan):
        d = bounds[k + 1] - bounds[k]
        out = f'{WORK}/tmp/s{S.n}_{k:02d}.mp4'
        zin = k % 2 == 0
        z = f"'1+0.07*t/{d:.3f}'" if zin else f"'1.07-0.07*t/{d:.3f}'"
        vf = (f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps={FPS},"
              f"scale=w='trunc(1080*{z[1:-1]}/2)*2':h=-2:eval=frame,crop=1080:1920,setsar=1,"
              "eq=contrast=1.07:saturation=0.78:brightness=-0.035:gamma=0.97,"
              "colorbalance=rs=0.03:gs=0.01:bs=-0.05:rm=0.04:gm=0.015:bm=-0.04:rh=0.03:bh=-0.04")
        if p:
            src = ['-ss', '0.3', '-stream_loop', '-1', '-i', p['path']]
        else:
            src = ['-f', 'lavfi', '-i', f'color=c=0x0a0d14:s=1080x1920:r={FPS}']
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *src, '-t', f'{d:.3f}', '-vf', vf, '-an',
                        '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16', '-pix_fmt', 'yuv420p', out], check=True)
        segs.append(out)
    with open(f'{WORK}/tmp/list{S.n}.txt', 'w') as fh:
        for s in segs:
            fh.write(f"file '{s}'\n")
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', f'{WORK}/tmp/list{S.n}.txt',
                    '-c', 'copy', f'{WORK}/tmp/footage{S.n}.mp4'], check=True)


# ================================================================= fallback (sem filmagem): fundo animado da marca
_bg = {}
_rnd = __import__('random').Random(7)
PARTS = [(_rnd.uniform(0, W + 200), _rnd.uniform(0, H), _rnd.uniform(4, 14), _rnd.uniform(0.15, 0.7), _rnd.uniform(0, 6.28), _rnd.uniform(0.05, 0.18)) for _ in range(30)]


def _sprite():
    if 'b' not in _bg:
        sp = cairo.ImageSurface(cairo.FORMAT_ARGB32, 128, 128); cc = cairo.Context(sp)
        gr = cairo.RadialGradient(64, 64, 0, 64, 64, 64)
        gr.add_color_stop_rgba(0, *GOLD2, 1); gr.add_color_stop_rgba(0.55, *GOLD, 0.45); gr.add_color_stop_rgba(1, *GOLD, 0)
        cc.set_source(gr); cc.paint(); _bg['b'] = sp
    return _bg['b']


import wb_engine as _WE

ICON_MAP = [(('car', 'lamborghini', 'driving'), 'car'), (('house', 'home', 'building'), 'house'), (('watch', 'clock', 'calendar'), 'watch'),
            (('coin', 'piggy', 'jar', 'dollar', 'money', 'bills', 'salary', 'wallet', 'paycheck'), 'coins'),
            (('chart', 'stock', 'market', 'investment', 'portfolio', 'financial', 'data'), 'chart'),
            (('card', 'payment', 'terminal'), 'card'), (('shopping', 'bags', 'store', 'mall'), 'bag'),
            (('phone', 'app', 'notification', 'banking'), 'phone'), (('laptop', 'office', 'business', 'work', 'desk', 'freelanc', 'designer', 'shop'), 'briefcase'),
            (('plant', 'tree', 'growing'), 'palm'), (('learning', 'studying', 'writing', 'notebook', 'skill', 'calculator', 'budget'), 'compass'),
            (('handshake', 'family'), 'heart'), (('man', 'woman', 'person', 'people', 'worker', 'runner', 'workout', 'crowd'), 'person'),
            (('door', 'opening'), 'shield'), (('construction', 'stairs'), 'house')]


def icon_for(q):
    for keys, ic in ICON_MAP:
        if any(k in q for k in keys):
            return ic
    return 'bolt'


def big_icon(c, kind, x, y, s, a):
    if kind in ('coins', 'chart', 'card', 'bag', 'phone'):
        c.save(); c.translate(x, y); c.scale(s / 100, s / 100)
        c.set_source_rgba(*GOLD2, a); c.set_line_width(2.4 * 100 / s); c.set_line_join(cairo.LINE_JOIN_ROUND)
        if kind == 'coins':
            for k in range(5):
                yy = 30 - k * 14
                c.save(); c.translate(-10 if k % 2 else 0, yy); c.scale(1, 0.35); c.arc(0, 0, 34, 0, 6.3); c.restore(); c.stroke()
            c.save(); c.translate(40, 20); c.scale(1, 0.35); c.arc(0, 0, 26, 0, 6.3); c.restore(); c.stroke()
        elif kind == 'chart':
            c.rectangle(-48, -40, 96, 80); c.stroke()
            c.move_to(-38, 26); c.line_to(-16, 6); c.line_to(2, 14); c.line_to(36, -26); c.stroke()
            c.move_to(24, -26); c.line_to(36, -26); c.line_to(36, -14); c.stroke()
        elif kind == 'card':
            rrect(c, -50, -32, 100, 64, 8); c.stroke(); c.move_to(-50, -14); c.line_to(50, -14); c.stroke()
            c.rectangle(-38, 6, 22, 14); c.stroke()
        elif kind == 'bag':
            c.move_to(-36, -18); c.line_to(36, -18); c.line_to(42, 44); c.line_to(-42, 44); c.close_path(); c.stroke()
            c.move_to(-16, -18); c.curve_to(-16, -46, 16, -46, 16, -18); c.stroke()
        elif kind == 'phone':
            rrect(c, -28, -50, 56, 100, 10); c.stroke(); c.move_to(-8, 40); c.line_to(8, 40); c.stroke()
        c.restore()
    elif kind == 'person':
        _WE.person(c, x, y + s * 0.45, s * 0.9, a, GOLD2, 0.05)
    else:
        _WE.icon(c, kind, x, y, s, a, GOLD2, 2.4)


def fallback_kind(q, k):
    if any(w in q for w in ('night', 'late', 'sleeping')):
        return 'night'
    if any(w in q for w in ('sunrise', 'sunset', 'dusk', 'aerial', 'skyline', 'city', 'morning')):
        return 'dawn' if k % 2 else 'night'
    return 'dark'


def fallback_bg(c, g, kind, t0, t1, k, q=''):
    c.set_source_rgb(*BG0); c.paint()
    p = clamp((g - t0) / max(0.5, t1 - t0))
    if kind == 'dark':
        kind = 'night' if k % 2 == 0 else 'dawn'
        themed = True
    else:
        themed = False
    if kind in ('night', 'dawn'):
        if kind not in _bg:
            _bg[kind] = cairo.ImageSurface.create_from_png(f'{WORK}/bg_{kind}.png')
        img = _bg[kind]
        z = (H / 1350) * (1.08 + 0.06 * (p if k % 2 == 0 else 1 - p))
        c.save(); c.translate(CX + (-1 if k % 2 else 1) * (p - 0.5) * 160, H / 2); c.scale(z, z)
        c.set_source_surface(img, -1200 + (k % 3 - 1) * 260, -760); c.paint(); c.restore()
        c.set_source_rgba(0, 0, 0, 0.25 if not themed else 0.55); c.paint()
        if themed:
            ia = 0.55 * sm((g - t0) / 0.4)
            glow(c, CX, H * 0.40, 520, GOLD, 0.16 * ia)
            sz = 560 * (1.0 + 0.06 * p)
            big_icon(c, icon_for(q), CX + (k % 3 - 1) * 40, H * 0.40, sz, ia)
    else:
        cx = W * (0.3 + 0.4 * ((k * 0.37) % 1)); cy = H * (0.25 + 0.3 * ((k * 0.61) % 1))
        gr = cairo.RadialGradient(cx, cy, 0, cx, cy, 1300)
        gr.add_color_stop_rgb(0, 0.10, 0.11, 0.16); gr.add_color_stop_rgb(0.5, 0.05, 0.065, 0.10); gr.add_color_stop_rgb(1, *BG0)
        c.set_source(gr); c.paint()
        # linhas finas douradas em perspectiva (grade "blueprint")
        c.set_source_rgba(*GOLD, 0.06); c.set_line_width(1.5)
        for j in range(-8, 9):
            c.move_to(CX + j * 40, H * 0.55); c.line_to(CX + j * 260, H); c.stroke()
        for j in range(10):
            yy = H * 0.55 + (H * 0.45) * ((j / 10 + g * 0.05) % 1) ** 2
            c.move_to(0, yy); c.line_to(W, yy); c.stroke()
    sp = _sprite()
    for x0, y0, vx, sc, ph, al in PARTS:
        x = (x0 + vx * g * 3) % (W + 200) - 100
        y = (y0 - g * 12 * sc) % H
        c.save(); c.translate(x, y); c.scale(sc, sc); c.set_source_surface(sp, -64, -64)
        c.paint_with_alpha(al * (0.6 + 0.4 * math.sin(g + ph))); c.restore()


# ================================================================= frame compose
def draw_overlay(c, S, g, gfx):
    # top & bottom gradient for legibility
    gr = cairo.LinearGradient(0, 0, 0, 420)
    gr.add_color_stop_rgba(0, 0, 0, 0, 0.55); gr.add_color_stop_rgba(1, 0, 0, 0, 0)
    c.set_source(gr); c.rectangle(0, 0, W, 420); c.fill()
    gr = cairo.LinearGradient(0, H * 0.55, 0, H)
    gr.add_color_stop_rgba(0, 0, 0, 0, 0); gr.add_color_stop_rgba(1, 0, 0, 0, 0.6)
    c.set_source(gr); c.rectangle(0, H * 0.55, W, H * 0.45); c.fill()
    # cut flash (subtle) on hard cuts
    cuts, _ = spec(S)
    for t, q in cuts[1:]:
        if 0 <= g - t < 0.12:
            c.set_source_rgba(1, 0.95, 0.85, 0.10 * (1 - (g - t) / 0.12)); c.paint()
    for f in gfx:
        f(c, g)
    brand_top(c, g, S)
    hook_title(c, g, S, TITLES[S.n])
    captions(c, S, g)
    end_card(c, g, S)
    # film vignette
    v = cairo.RadialGradient(CX, H / 2, H * 0.35, CX, H / 2, H * 0.75)
    v.add_color_stop_rgba(0, 0, 0, 0, 0); v.add_color_stop_rgba(1, 0, 0, 0, 0.45)
    c.set_source(v); c.paint()


def render(S, out_path):
    cuts, gfx = spec(S)
    plan = json.load(open(f'{WORK}/clips/plan{S.n}.json'))
    N = int(S.dur * FPS)
    dec = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', f'{WORK}/tmp/footage{S.n}.mp4', '-f', 'rawvideo',
                            '-pix_fmt', 'bgra', '-'], stdout=subprocess.PIPE)
    enc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}',
                            '-r', str(FPS), '-i', '-', '-i', f'{WORK}/mix{S.n}.wav', '-map', '0:v', '-map', '1:a',
                            '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p',
                            '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-shortest', out_path], stdin=subprocess.PIPE)
    fb = W * H * 4
    last = None
    for f in range(N):
        raw = dec.stdout.read(fb)
        if len(raw) == fb:
            last = raw
        arr = np.frombuffer(bytearray(last), np.uint8).reshape(H, W, 4).copy()
        surf = cairo.ImageSurface.create_for_data(memoryview(arr), cairo.FORMAT_ARGB32, W, H)
        c = cairo.Context(surf)
        g = f / FPS
        k = max(i for i, (t, q) in enumerate(cuts) if t <= g + 1e-6)
        if plan[k] is None:
            t1 = cuts[k + 1][0] if k + 1 < len(cuts) else S.dur
            fallback_bg(c, g, fallback_kind(cuts[k][1], k), cuts[k][0], t1, k, cuts[k][1])
        draw_overlay(c, S, g, gfx)
        surf.flush()
        enc.stdin.write(arr.tobytes())
    enc.stdin.close(); enc.wait(); dec.terminate()


def mix(S):
    sr = wb_audio.SR
    prog = {1: 'dm', 2: 'fm', 3: 'up', 4: 'am', 5: 'dm', 6: 'up', 7: 'am'}[S.n]
    bed = wb_audio.make_bed(S.dur, seed=S.n, prog=prog, bpm=84, pulse=0.8, swell_at=S.end_t)
    sig = wb_audio.signature()
    s0 = int((S.end_t - 0.1) * sr)
    full = bed.copy()
    full[s0:s0 + len(sig)] += sig[:len(full) - s0] * 1.0
    full[s0:] *= np.linspace(1, 0.35, len(full) - s0)[:, None] ** 0.5 if False else 1
    sf.write(f'{WORK}/bed{S.n}.wav', full.astype(np.float32), sr)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'{WORK}/v{S.n}.wav', '-i', f'{WORK}/bed{S.n}.wav', '-filter_complex',
                    '[0:a]aresample=48000,adelay=0|0,highpass=f=70,equalizer=f=180:t=q:w=1:g=1.5,equalizer=f=3500:t=q:w=1.2:g=2,'
                    'acompressor=threshold=-22dB:ratio=3:attack=8:release=160:makeup=2,aformat=channel_layouts=stereo,apad,asplit=2[v][sc];'
                    '[1:a]highpass=f=38,equalizer=f=110:t=q:w=1:g=-3,volume=0.5[m];'
                    '[m][sc]sidechaincompress=threshold=0.03:ratio=4:attack=60:release=500[md];'
                    '[v][md]amix=inputs=2:normalize=0:duration=shortest,loudnorm=I=-14:TP=-1.5:LRA=9[o]',
                    '-map', '[o]', '-ar', '48000', '-t', f'{S.dur:.3f}', f'{WORK}/mix{S.n}.wav'], check=True)


if __name__ == '__main__':
    mode, n = sys.argv[1], int(sys.argv[2])
    S = Short(n)
    if mode == 'fetch':
        fetch(S)
    elif mode == 'render':
        if not os.path.exists(f'{WORK}/clips/plan{n}.json'):
            cuts, _ = spec(S)
            os.makedirs(f'{WORK}/clips', exist_ok=True)
            json.dump([None] * len(cuts), open(f'{WORK}/clips/plan{n}.json', 'w'))
        build_footage(S)
        mix(S)
        os.makedirs(f'{WORK}/out', exist_ok=True)
        render(S, f'{WORK}/out/short{n}.mp4')
        print('ok', n, round(S.dur, 1))
    elif mode == 'frames':
        cuts, gfx = spec(S)
        os.makedirs(f'{WORK}/frames', exist_ok=True)
        for tt in sys.argv[3:]:
            g = float(tt)
            arr = np.zeros((H, W, 4), np.uint8); arr[..., :3] = (20, 14, 10); arr[..., 3] = 255
            surf = cairo.ImageSurface.create_for_data(memoryview(arr), cairo.FORMAT_ARGB32, W, H)
            c = cairo.Context(surf)
            gr = cairo.LinearGradient(0, 0, W, H); gr.add_color_stop_rgb(0, 0.25, 0.22, 0.2); gr.add_color_stop_rgb(1, 0.08, 0.09, 0.12)
            c.set_source(gr); c.paint()
            draw_overlay(c, S, g, gfx)
            surf.write_to_png(f'{WORK}/frames/s{n}_{g:05.1f}.png')
