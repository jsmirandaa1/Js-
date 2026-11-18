import re, subprocess, math, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

D = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
ANTON = f"{D}/Anton.ttf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
DUR = 82.44

vals = list(map(float, open(f"{D}/pauses.txt").read().split()))
pauses = [(vals[i], vals[i + 1]) for i in range(0, len(vals) - 1, 2)]

# (label_span, body_span, body_text, card)
S = [
    (None, (0.0, 11.38), "Hoje à meia-noite sai o GTA 6. E se você não souber essas sete coisas, vai passar vergonha.",
     dict(n=0, emoji="🚨", head="7 COISAS", sub="ANTES DE JOGAR GTA 6")),
    ((11.83, 12.10), (12.40, 20.59), "O jogo libera à meia-noite, horário de Brasília. Mas na Nova Zelândia o pessoal começa a jogar horas antes. Então cuidado com spoiler.",
     dict(n=1, emoji="🕛", head="LIBERA 00:00", sub="HORÁRIO DE BRASÍLIA")),
    ((20.97, 21.52), (21.67, 30.29), "Se você comprou a versão digital, o pré-download já tá liberado. Baixa agora, porque o jogo é pesado e a internet brasileira não perdoa.",
     dict(n=2, emoji="📥", head="BAIXA AGORA", sub="PRÉ-DOWNLOAD LIBERADO")),
    ((30.60, 31.07), (31.34, 37.52), "Não tem pra PC. Só PS5 e Xbox Series. E não, não roda no PS4.",
     dict(n=3, emoji="🚫", head="SEM PC, SEM PS4", sub="SÓ PS5 E XBOX SERIES")),
    ((37.85, 38.27), (38.55, 45.61), "São dois protagonistas, Jason e Lúcia. E a Lúcia é a primeira protagonista mulher da era moderna do GTA.",
     dict(n=4, emoji="👫", head="JASON & LÚCIA", sub="2 PROTAGONISTAS")),
    ((45.88, 46.41), (46.55, 52.32), "A história se passa em Leonida, um estado inspirado na Flórida. E sim: Vice City voltou.",
     dict(n=5, emoji="🌴", head="VICE CITY VOLTOU", sub="ESTADO DE LEONIDA")),
    ((52.60, 53.20), (53.48, 64.24), "Segundo quem já viu prévias, o mapa seria quase o dobro do GTA 5. Tem praia, ilhas, pântano… e o primeiro trailer já mostrou um jacaré entrando numa loja de conveniência.",
     dict(n=6, emoji="🐊", head="MAPA GIGANTE", sub="QUASE 2X O GTA 5*", note="*SEGUNDO PRÉVIAS")),
    ((64.53, 65.70), (65.84, 73.64), "Foram treze anos de espera desde o GTA 5, que vendeu mais de duzentos milhões de cópias. Ou seja, a pressão é gigante.",
     dict(n=7, emoji="😭", head="13 ANOS", sub="DE ESPERA")),
    (None, (73.97, 82.25), "E aí, você vai jogar à meia-noite ou vai pro trabalho amanhã fingindo que tá doente? Segue aí, que amanhã eu trago os segredos que ninguém te contou.",
     dict(n=8, emoji="👇", head="SEGUE AÍ", sub="AMANHÃ TEM PARTE 2")),
]
LABELS = ["UM:", "DOIS:", "TRÊS:", "QUATRO:", "CINCO:", "SEIS:", "SETE:"]
HL = {"GTA", "6", "5", "PC", "PS5", "PS4", "XBOX", "SERIES", "JASON", "LÚCIA", "VICE", "CITY", "LEONIDA", "MEIA-NOITE",
      "SPOILER", "SETE", "TREZE", "DUZENTOS", "MILHÕES", "JACARÉ", "BAIXA", "AGORA", "DOBRO", "VERGONHA", "SEGUE"}


def snap(t, lo, hi):
    best = None
    for a, b in pauses:
        if lo < a < hi and abs(a - t) < 0.9:
            if best is None or abs(a - t) < abs(best[0] - t):
                best = (a, b)
    return best


def SL(x):
    return len(re.sub(r"GTA", "gê tê á", x))


def timeline(text, a, b):
    """Split into sentences, snap boundaries to pauses, then chunk words."""
    sents = [s.strip() for s in re.split(r"(?<=[.?!:])\s+", text) if s.strip()]
    tot = sum(SL(s) for s in sents)
    spans, cur, acc = [], a, 0
    for i, s in enumerate(sents):
        acc += SL(s)
        if i == len(sents) - 1:
            spans.append((cur, b)); break
        pred = a + (b - a) * acc / tot
        sp = snap(pred, cur + 0.3, b - 0.3)
        end, nxt = (sp if sp else (pred, pred))
        spans.append((cur, end)); cur = nxt
    out = []
    for s, (sa, sb) in zip(sents, spans):
        words = s.split()
        chunks, c = [], []
        for w in words:
            c.append(w)
            if len(" ".join(c)) >= 11 or len(c) >= 3 or re.search(r"[,.?!:…]$", w):
                chunks.append(c); c = []
        if c: chunks.append(c)
        L = sum(SL(" ".join(c)) + 2 for c in chunks)
        t = sa
        for c in chunks:
            d = (sb - sa) * (SL(" ".join(c)) + 2) / L
            out.append((t, t + d, " ".join(c)))
            t += d
    return out


def ass_time(t):
    t = max(0, t); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def fmt(chunk):
    ws = []
    for w in chunk.upper().split():
        core = re.sub(r"[,.?!:…]", "", w)
        ws.append("{\\c&H00E6FF&}" + w + "{\\c&HFFFFFF&}" if core in HL else w)
    return " ".join(ws)


ev = []
for i, (lab, (a, b), text, card) in enumerate(S):
    if lab:
        ev.append((lab[0], lab[1] + 0.2, LABELS[card["n"] - 1]))
    for t0, t1, c in timeline(text, a, b):
        ev.append((t0, t1, c))
ev.sort()
lines = []
for j, (t0, t1, c) in enumerate(ev):
    nxt = ev[j + 1][0] if j + 1 < len(ev) else DUR
    t1 = min(max(t1, t0 + 0.25), nxt)
    lines.append(f"Dialogue: 0,{ass_time(t0)},{ass_time(t1)},Cap,,0,0,0,,{{\\fscx75\\fscy75\\t(0,90,\\fscx100\\fscy100)}}{fmt(c)}")

ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Anton,104,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,1,0,1,9,5,5,90,90,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(l.replace(",Cap,,0,0,0,,", ",Cap,,0,0,0,,{\\pos(540,1390)}") for l in lines) + "\n"
open(f"{D}/caps.ass", "w").write(ass)

# ---------- background ----------
bg = Image.new("RGB", (W, H))
px = bg.load()
stops = [(0, (22, 6, 48)), (0.45, (120, 20, 110)), (0.75, (255, 46, 136)), (1, (255, 150, 60))]
for y in range(H):
    f = y / (H - 1)
    for k in range(len(stops) - 1):
        if stops[k][0] <= f <= stops[k + 1][0]:
            u = (f - stops[k][0]) / (stops[k + 1][0] - stops[k][0])
            col = tuple(int(stops[k][1][c] + (stops[k + 1][1][c] - stops[k][1][c]) * u) for c in range(3))
    for x in range(W):
        px[x, y] = col
d = ImageDraw.Draw(bg, "RGBA")
# synthwave sun
cx, cy, r = 540, 1240, 330
sun = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(sun)
for yy in range(cy - r, cy + r):
    f = (yy - (cy - r)) / (2 * r)
    half = int(math.sqrt(max(0, r * r - (yy - cy) ** 2)))
    gap = yy > cy and (yy - cy) % 46 < 6 + (yy - cy) // 20
    if not gap:
        sd.line([(cx - half, yy), (cx + half, yy)], fill=(255, int(230 - 120 * f), int(90 - 40 * f), 150))
bg.paste(sun, (0, 0), sun)
# perspective grid
hz = 1560
for k in range(-12, 13):
    d.line([(540 + k * 40, hz), (540 + k * 260, H)], fill=(255, 120, 220, 110), width=3)
y, step = hz, 12
while y < H:
    d.line([(0, y), (W, y)], fill=(255, 120, 220, 110), width=3); step *= 1.35; y += int(step)
d.rectangle([0, 0, W, H], fill=(0, 0, 0, 70))
bg = bg.filter(ImageFilter.GaussianBlur(1))
bg.save(f"{D}/bg.png")

# ---------- cards ----------
def emoji_img(e, size):
    f = ImageFont.truetype(EMOJI, 109, layout_engine=ImageFont.Layout.RAQM) if False else ImageFont.truetype(EMOJI, 109)
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((80, 80), e, font=f, embedded_color=True, anchor="mm")
    im = im.crop(im.getbbox())
    s = size / max(im.size)
    return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)


def text_c(d, y, txt, size, fill, stroke=10, maxw=980):
    while True:
        f = ImageFont.truetype(ANTON, size)
        if d.textlength(txt, font=f) <= maxw or size < 40: break
        size -= 4
    d.text((540, y), txt, font=f, fill=fill, anchor="mm", stroke_width=stroke, stroke_fill=(0, 0, 0))


for i, (_, _, _, c) in enumerate(S):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # top pill
    f = ImageFont.truetype(ANTON, 46)
    t = "GTA 6  •  7 COISAS PRA SABER"
    tw = d.textlength(t, font=f)
    d.rounded_rectangle([540 - tw / 2 - 34, 150, 540 + tw / 2 + 34, 228], 39, fill=(0, 0, 0, 170))
    d.text((540, 189), t, font=f, fill=(255, 255, 255), anchor="mm")
    # progress dots
    for k in range(7):
        x = 540 + (k - 3) * 92
        on = 1 <= c["n"] <= 8 and k < c["n"]
        cur = k == c["n"] - 1
        rr = 30 if cur else 22
        d.ellipse([x - rr, 300 - rr, x + rr, 300 + rr], fill=(255, 230, 0) if on else (255, 255, 255, 70),
                  outline=(0, 0, 0), width=4)
        d.text((x, 300), str(k + 1), font=ImageFont.truetype(ANTON, 30 if cur else 24),
               fill=(0, 0, 0) if on else (255, 255, 255), anchor="mm")
    # giant faded number
    if 1 <= c["n"] <= 7:
        big = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(big).text((540, 640), str(c["n"]), font=ImageFont.truetype(ANTON, 640),
                                 fill=(255, 255, 255, 55), anchor="mm")
        im = Image.alpha_composite(im, big); d = ImageDraw.Draw(im)
    e = emoji_img(c["emoji"], 300)
    im.alpha_composite(e, (540 - e.width // 2, 600 - e.height // 2))
    text_c(d, 900, c["head"], 150, (255, 255, 255), 12)
    text_c(d, 1045, c["sub"], 80, (255, 230, 0), 8)
    if c.get("note"):
        text_c(d, 1130, c["note"], 40, (255, 255, 255), 5)
    im.save(f"{D}/card{i}.png")

# ---------- ffmpeg ----------
starts = [0.0] + [s[0][0] if s[0] else s[1][0] for s in S[1:]]
ends = starts[1:] + [DUR]
inputs = ["-loop", "1", "-framerate", "30", "-i", f"{D}/bg.png"]
for i in range(len(S)):
    inputs += ["-loop", "1", "-framerate", "30", "-t", f"{ends[i] - starts[i] + 0.01:.2f}", "-i", f"{D}/card{i}.png"]
inputs += ["-i", f"{D}/voz.mp3"]
fc = ["[0:v]scale=1188:2112,crop=1080:1920:'54+54*sin(t/5)':'96+96*cos(t/7)',format=rgba[b0]"]
prev = "b0"
for i in range(len(S)):
    # pop-in: scale from 88% to 100% in 0.15s, plus fade
    fc.append(f"[{i + 1}:v]format=rgba,fade=in:st=0:d=0.15:alpha=1,setpts=PTS+{starts[i]}/TB[c{i}]")
    fc.append(f"[{prev}][c{i}]overlay=0:0:enable='between(t,{starts[i]},{ends[i]})':eof_action=pass[b{i + 1}]")
    prev = f"b{i + 1}"
fc.append(f"[{prev}]ass={D}/caps.ass:fontsdir={D},format=yuv420p[v]")
cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + inputs + [
    "-filter_complex", ";".join(fc), "-map", "[v]", "-map", f"{len(S) + 1}:a",
    "-t", str(DUR), "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", f"{D}/7coisas_gta6.mp4"]
print(" ".join(cmd[:6]), "...")
subprocess.run(cmd, check=True)
print("ok")
