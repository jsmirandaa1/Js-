"""Thumbnail (1280x720), legenda .srt e capítulos do Ep. 001.
Uso: WORK=/root/work/ep1 OUT=/home/user/Js-/videos/dark python3 ep001_extras.py
"""
import os, math, cairo
import ep001_build as B

WORK = B.WORK
OUT = os.environ.get('OUT', WORK)
os.makedirs(OUT, exist_ok=True)


def fmt(t, srt=True):
    h, r = divmod(t, 3600); m, s = divmod(r, 60)
    if srt:
        return f'{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)) % 1000:03d}'
    return f'{int(m)}:{int(s):02d}'


# ---------------- SRT
def chunks(text, maxc=84):
    words = text.split()
    if len(text) <= maxc:
        return [text]
    n = math.ceil(len(text) / maxc)
    per = math.ceil(len(words) / n)
    return [' '.join(words[i:i + per]) for i in range(0, len(words), per)]


lines = []
k = 1
for x in B.TL:
    parts = chunks(x['text'])
    tot = sum(len(p) for p in parts)
    t = x['start']
    for p in parts:
        d = (x['end'] - x['start']) * len(p) / tot
        lines.append(f'{k}\n{fmt(t)} --> {fmt(t + d)}\n{p}\n')
        k += 1; t += d
open(f'{OUT}/ep001_first_100k.en.srt', 'w').write('\n'.join(lines))

# ---------------- chapters
ch = [(0, 'Imagine $100,000 in your account'), (B.T(12) - 0.5, 'Why the first $100,000 feels impossible'),
      (B.E(27) + 0.5, 'The power of your first $100,000'), (B.E(44) + 0.5, 'Compound growth: the real game changer'),
      (B.E(62) + 0.5, 'How to reach your first $100,000'), (B.E(82) + 0.5, 'The mindset shift'),
      (B.E(94) + 0.5, 'The beginning')]
open(f'{WORK}/chapters.txt', 'w').write('\n'.join(f'{fmt(t, False)} {s}' for t, s in ch))

# ---------------- thumbnail
TW, TH = 1280, 720
s = cairo.ImageSurface(cairo.FORMAT_ARGB32, TW, TH)
c = cairo.Context(s)
c.set_source_rgb(*B.BG0); c.paint()
gr = cairo.RadialGradient(TW * .72, TH * .45, 0, TW * .72, TH * .45, 800)
gr.add_color_stop_rgb(0, 0.10, 0.12, 0.18); gr.add_color_stop_rgb(1, *B.BG0)
c.set_source(gr); c.paint()
# compound curve (right side)
x0, x1, y0, y1 = 640, 1240, 640, 70
pts = [(x0 + (x1 - x0) * k / 100, y0 - (y0 - y1) * ((1.07 ** (k / 100 * 30) - 1) / (1.07 ** 30 - 1))) for k in range(101)]
c.move_to(x0, y0)
for p in pts:
    c.line_to(*p)
c.line_to(x1, y0); c.close_path()
g2 = cairo.LinearGradient(0, y1, 0, y0)
g2.add_color_stop_rgba(0, *B.GOLD, 0.45); g2.add_color_stop_rgba(1, *B.GOLD, 0.0)
c.set_source(g2); c.fill()
for lw, a in ((26, 0.08), (14, 0.18), (6, 1.0)):
    c.move_to(*pts[0])
    for p in pts:
        c.line_to(*p)
    c.set_source_rgba(*B.GOLD2, a); c.set_line_width(lw); c.stroke()
B.glow(c, pts[-1][0], pts[-1][1], 120, B.GOLD2, 0.7)
c.set_source_rgba(*B.GOLD2, 1); c.arc(pts[-1][0], pts[-1][1], 12, 0, 6.3); c.fill()
# "slow" zone marker
c.set_dash([8, 8]); B.line(c, x0 + 330, y0, x0 + 330, 300, B.IVORY, 0.35, 2); c.set_dash([])
B.text(c, 'HARD', x0 + 165, y0 - 30, 30, 'xb', B.RED, 0.95, 'c', 4)
B.text(c, 'EASIER', x0 + 470, y0 - 30, 30, 'xb', B.GOLD2, 0.95, 'c', 4)
# left text
B.glow(c, 330, 330, 360, B.GOLD, 0.15)
B.text(c, 'YOUR FIRST', 60, 190, 64, 'xb', B.IVORY, 1, 'l', 2)
B.text(c, '$100K', 50, 370, 200, 'xb', B.GOLD2, 1, 'l')
B.text(c, 'IS THE', 60, 460, 64, 'xb', B.IVORY, 1, 'l', 2)
# HARDEST with red highlight block
w = B.tw(c, 'HARDEST', 'xb', 96, 2)
B.rrect(c, 44, 486, w + 36, 116, 10); c.set_source_rgba(*B.RED, 1); c.fill()
B.text(c, 'HARDEST', 62, 580, 96, 'xb', B.IVORY, 1, 'l', 2)
B.vignette  # noqa
v = cairo.RadialGradient(TW / 2, TH / 2, TH * 0.4, TW / 2, TH / 2, TW * 0.75)
v.add_color_stop_rgba(0, 0, 0, 0, 0); v.add_color_stop_rgba(1, 0, 0, 0, 0.6)
c.set_source(v); c.paint()
s.write_to_png(f'{OUT}/ep001_thumbnail.png')
print('extras ok')
