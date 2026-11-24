"""Ep. 002: thumbnail (mesmo estilo do Ep. 001), legenda .srt e capítulos.
Uso: WORK=/root/work/ep2 OUT=/home/user/Js-/videos/dark python3 ep002_extras.py
"""
import os, math, cairo
import wb_engine as B

WORK = B.WORK
OUT = os.environ.get('OUT', WORK)
os.makedirs(OUT, exist_ok=True)


def fmt(t, srt=True):
    h, r = divmod(t, 3600); m, s = divmod(r, 60)
    if srt:
        return f'{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)) % 1000:03d}'
    return f'{int(m)}:{int(s):02d}'


def chunks(text, maxc=84):
    words = text.split()
    if len(text) <= maxc:
        return [text]
    n = math.ceil(len(text) / maxc); per = math.ceil(len(words) / n)
    return [' '.join(words[i:i + per]) for i in range(0, len(words), per)]


lines, k = [], 1
for x in B.TL:
    parts = chunks(x['text']); tot = sum(len(p) for p in parts); t = x['start']
    for p in parts:
        d = (x['end'] - x['start']) * len(p) / tot
        lines.append(f'{k}\n{fmt(t)} --> {fmt(t + d)}\n{p}\n'); k += 1; t += d
open(f'{OUT}/ep002_rich_dont_work_for_money.en.srt', 'w').write('\n'.join(lines))

T, E = B.T, B.E
ch = [(0, 'Two people, same alarm'), (T(10) - 0.5, 'The time trap'), (E(26) + 0.5, 'What the wealthy actually work for'),
      (E(46) + 0.5, 'Your money can clock in'), (E(65) + 0.5, 'Leverage: do the work once'),
      (E(81) + 0.5, 'How to start without quitting your job'), (E(97) + 0.5, 'The real question')]
open(f'{WORK}/chapters.txt', 'w').write('\n'.join(f'{fmt(t, False)} {s}' for t, s in ch) + '\n')

# ---------------- thumbnail (mesma linguagem do Ep. 001: texto à esquerda, gráfico à direita, bloco vermelho)
TW, TH = 1280, 720
s = cairo.ImageSurface(cairo.FORMAT_ARGB32, TW, TH); c = cairo.Context(s)
c.set_source_rgb(*B.BG0); c.paint()
gr = cairo.RadialGradient(TW * .74, TH * .45, 0, TW * .74, TH * .45, 800)
gr.add_color_stop_rgb(0, 0.10, 0.12, 0.18); gr.add_color_stop_rgb(1, *B.BG0)
c.set_source(gr); c.paint()
# right: clock (time) crossed vs gold rising bars (assets)
cx, cy, r = 1060, 215, 105
c.set_source_rgba(*B.IVORY, 0.85); c.set_line_width(8); c.arc(cx, cy, r, 0, 2 * math.pi); c.stroke()
for k in range(12):
    a = k / 12 * 2 * math.pi
    B.line(c, cx + math.cos(a) * r * .8, cy + math.sin(a) * r * .8, cx + math.cos(a) * r * .9, cy + math.sin(a) * r * .9, B.IVORY, 0.7, 4)
B.line(c, cx, cy, cx, cy - 70, B.IVORY, 1, 9); B.line(c, cx, cy, cx + 55, cy + 25, B.IVORY, 1, 7)
B.line(c, cx - 130, cy - 130, cx + 130, cy + 130, B.RED, 1, 15)
B.text(c, 'TIME', cx, cy + 175, 34, 'xb', B.IVORY, 0.9, 'c', 6)
bars = [60, 100, 150, 210, 280]
for k, h in enumerate(bars):
    x = 830 + k * 78
    B.rrect(c, x, 680 - h, 58, h, 6)
    g2 = cairo.LinearGradient(0, 680 - h, 0, 680)
    g2.add_color_stop_rgba(0, *B.GOLD2, 1); g2.add_color_stop_rgba(1, *B.GOLDD, 1)
    c.set_source(g2); c.fill()
B.glow(c, 1170, 420, 160, B.GOLD2, 0.5)
B.text(c, 'ASSETS', 1020, 708, 30, 'xb', B.GOLD2, 0.95, 'c', 6)
# left text
B.glow(c, 330, 330, 360, B.GOLD, 0.15)
B.text(c, 'RICH PEOPLE', 60, 170, 70, 'xb', B.IVORY, 1, 'l', 2)
B.text(c, "DON'T WORK", 56, 330, 120, 'xb', B.GOLD2, 1, 'l')
B.text(c, 'FOR', 60, 430, 70, 'xb', B.IVORY, 1, 'l', 2)
w = B.tw(c, 'MONEY', 'xb', 110, 2)
B.rrect(c, 44, 460, w + 36, 132, 10); c.set_source_rgba(*B.RED, 1); c.fill()
B.text(c, 'MONEY', 62, 568, 110, 'xb', B.IVORY, 1, 'l', 2)
v = cairo.RadialGradient(TW / 2, TH / 2, TH * 0.4, TW / 2, TH / 2, TW * 0.75)
v.add_color_stop_rgba(0, 0, 0, 0, 0); v.add_color_stop_rgba(1, 0, 0, 0, 0.6)
c.set_source(v); c.paint()
s.write_to_png(f'{OUT}/ep002_thumbnail.png')
print('extras ok')
