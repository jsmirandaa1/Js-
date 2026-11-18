import os, re, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
O = f"{D}/../f7"
TR = f"{D}/rs/tr/GTAVI_Launch_Trailer.mp4"
PL = f"{D}/rs/tr/GTAVI_Pre-Load_Now.mp4"
SHOTS = [l.strip()[2:] for l in open(f"{D}/rs/tr/shots.txt")]
def IMG(i): return f"{D}/rs/tr/shots/{SHOTS[i]}"
ANTON = f"{D}/../v/Anton.ttf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
W, H, FPS = 1080, 1920, 30
DUR = 82.44
os.makedirs(f"{O}/shots", exist_ok=True)
def run(cmd): subprocess.run(cmd, check=True)

# (start, end, kind, src, param, xoff/pan)
SH = [
    # titulo + gancho
    (0.00, 1.24, "v", TR, 26.2, 0.45), (1.24, 2.24, "v", TR, 53.0, 0.5), (2.24, 3.20, "v", TR, 49.4, 0.5),
    (3.20, 4.70, "v", TR, 25.0, 0.5), (4.70, 5.88, "i", IMG(137), 0, (0.2, 0.5)), (5.88, 7.26, "v", TR, 73.0, 0.4),
    (7.26, 8.66, "v", TR, 61.0, 0.5), (8.66, 9.78, "v", TR, 38.0, 0.5), (9.78, 11.80, "v", TR, 69.0, 0.5),
    # 1 meia-noite
    (11.80, 14.00, "v", TR, 18.2, 0.5), (14.00, 15.44, "v", TR, 70.0, 0.5), (15.44, 17.60, "i", IMG(120), 0, (0.6, 0.3)),
    (17.60, 18.84, "v", TR, 72.0, 0.4), (18.84, 20.90, "v", TR, 34.0, 0.5),
    # 2 pre-download
    (20.90, 23.78, "v", PL, 15.0, 0.5), (23.78, 25.66, "v", PL, 11.0, 0.5), (25.66, 28.00, "v", PL, 3.0, 0.5),
    (28.00, 30.58, "v", PL, 19.0, 0.5),
    # 3 plataformas
    (30.58, 32.76, "v", TR, 81.5, 0.5), (32.76, 35.28, "v", PL, 23.0, 0.5), (35.28, 37.80, "i", IMG(0), 0, (0.3, 0.5)),
    # 4 Jason & Lucia
    (37.80, 40.14, "i", IMG(44), 0, (0.3, 0.6)), (40.14, 41.56, "v", TR, 40.5, 0.5), (41.56, 43.50, "i", IMG(56), 0, (0.4, 0.6)),
    (43.50, 45.84, "i", IMG(67), 0, (0.55, 0.35)),
    # 5 Leonida / Vice City
    (45.84, 47.80, "v", TR, 3.2, 0.5), (47.80, 49.46, "i", IMG(84), 0, (0.2, 0.7)), (49.46, 50.46, "i", IMG(125), 0, (0.7, 0.4)),
    (50.46, 52.58, "i", IMG(111), 0, (0.3, 0.6)),
    # 6 mapa
    (52.58, 55.00, "i", IMG(91), 0, (0.2, 0.7)), (55.00, 56.60, "v", TR, 5.0, 0.5), (56.60, 57.64, "i", IMG(86), 0, (0.6, 0.3)),
    (57.64, 58.68, "i", IMG(115), 0, (0.4, 0.6)), (58.68, 59.30, "v", TR, 14.0, 0.5), (59.30, 59.86, "i", IMG(102), 0, (0.4, 0.6)),
    (59.86, 61.82, "i", IMG(92), 0, (0.3, 0.7)), (61.82, 63.10, "v", TR, 20.9, 0.45), (63.10, 64.56, "i", IMG(96), 0, (0.3, 0.6)),
    # 7 13 anos
    (64.56, 66.08, "v", TR, 80.0, 0.5), (66.08, 68.46, "i", IMG(118), 0, (0.3, 0.7)), (68.46, 71.32, "i", IMG(128), 0, (0.4, 0.6)),
    (71.32, 73.88, "v", TR, 35.0, 0.5),
    # CTA
    (73.88, 76.12, "v", TR, 59.0, 0.5), (76.12, 78.76, "v", TR, 57.5, 0.5), (78.76, 80.28, "i", IMG(47), 0, (0.35, 0.6)),
    (80.28, DUR, "v", TR, 27.0, 0.45),
]
files = []
for i, (a, b, kind, src, st, xo) in enumerate(SH):
    out = f"{O}/shots/s{i:02d}.mp4"; files.append(out); d = b - a
    if os.path.exists(out) and not os.environ.get("REDO"): continue
    grade = ",eq=contrast=1.06:saturation=1.18"
    if kind == "v":
        cw = int(2160 * 9 / 16); x = int((3840 - cw) * xo)
        run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{st}", "-i", src, "-t", f"{d:.3f}",
             "-vf", f"crop={cw}:2160:{x}:0,scale={W}:{H}{grade},fps={FPS},format=yuv420p", "-an",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", out])
    else:
        im = Image.open(src).convert("RGB"); sc = (H * 1.08) / im.height
        im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS); tmp = f"{O}/shots/i{i:02d}.png"; im.save(tmp)
        p0, p1 = xo; mw = im.width - W; mh = im.height - H
        run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", str(FPS), "-i", tmp, "-t", f"{d:.3f}",
             "-vf", f"crop={W}:{H}:'{mw}*({p0}+({p1}-{p0})*t/{d:.3f})':'{mh}*(0.5)'{grade},format=yuv420p",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", out])
open(f"{O}/shots/list.txt", "w").write("".join(f"file '{f}'\n" for f in files))
run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{O}/shots/list.txt", "-c", "copy", f"{O}/base.mp4"])

# ---------------- captions (phrase-level timings measured from the narration) ----------------
CAP = [
    ("Hoje à meia-noite", 0.00, 2.34), ("sai o GTA 6.", 2.45, 4.41), ("E se você não souber", 4.87, 7.33),
    ("essas sete coisas,", 7.51, 9.89), ("vai passar vergonha.", 10.06, 11.38),
    ("O jogo libera à meia-noite, horário de Brasília.", 12.48, 15.25),
    ("Mas na Nova Zelândia o pessoal começa a jogar horas antes.", 15.57, 19.19), ("Então cuidado com spoiler.", 19.30, 20.59),
    ("Se você comprou a versão digital,", 21.83, 24.82),
    ("o pré-download já tá liberado. Baixa agora, porque o jogo é pesado e a internet brasileira não perdoa.", 24.95, 30.26),
    ("Não tem pra PC.", 31.34, 32.55), ("Só PS5 e Xbox Series.", 32.81, 35.10), ("E não, não roda no PS4.", 35.34, 37.51),
    ("São dois protagonistas, Jason e Lúcia.", 38.56, 41.29),
    ("E a Lúcia é a primeira protagonista mulher da era moderna do GTA.", 41.50, 45.60),
    ("A história se passa em Leonida, um estado inspirado na Flórida.", 46.65, 50.26), ("E sim:", 50.42, 50.90),
    ("Vice City voltou.", 51.08, 52.30),
    ("Segundo quem já viu prévias, o mapa seria quase o dobro do GTA 5.", 53.49, 57.43),
    ("Tem praia, ilhas, pântano…", 57.74, 59.84),
    ("e o primeiro trailer já mostrou um jacaré entrando numa loja de conveniência.", 59.95, 64.23),
    ("Foram treze anos de espera desde o GTA 5, que vendeu mais de duzentos milhões de cópias.", 65.84, 71.08),
    ("Ou seja, a pressão é gigante.", 71.34, 73.61),
    ("E aí, você vai jogar à meia-noite ou vai pro trabalho amanhã fingindo que tá doente?", 73.97, 78.44),
    ("Segue aí, que amanhã eu trago os segredos que ninguém te contou.", 78.80, 82.23),
]
HL = {"GTA", "6", "5", "6.", "5.", "MEIA-NOITE", "SETE", "VERGONHA", "BRASÍLIA", "SPOILER", "PRÉ-DOWNLOAD", "BAIXA", "AGORA",
      "PC", "PS5", "XBOX", "SERIES", "PS4", "JASON", "LÚCIA", "LEONIDA", "VICE", "CITY", "DOBRO", "JACARÉ", "TREZE",
      "DUZENTOS", "MILHÕES", "GIGANTE", "DOENTE", "SEGUE", "SEGREDOS", "NOVA", "ZELÂNDIA", "PRIMEIRA", "MULHER"}
def SL(x): return len(x.replace("GTA", "gê tê á").replace("PS5", "pê ésse cinco").replace("PS4", "pê ésse quatro"))
def at(t): return f"0:{int(t//60):02d}:{t%60:05.2f}"
import sys; sys.path.insert(0, D)
from capw import build_ev
ev = build_ev(f"{O}/voz_words.json", [("saiu GTA", "sai o GTA"), ("vai ser e", "Vice City"), ("Prévias,", "prévias,")], DUR)
def fmt(x):
    o = []
    for w in x.upper().split():
        core = re.sub(r"[,.?!:…]", "", w)
        o.append("{\\c&H00E6FF&}" + w + "{\\c&HFFFFFF&}" if core in HL or w in HL else w)
    return " ".join(o)
lines = []
for j, (a, b, x) in enumerate(ev):
    lines.append(f"Dialogue: 0,{at(a)},{at(b)},Cap,,0,0,0,,{{\\pos(540,1330)\\fscx70\\fscy70\\t(0,80,\\fscx104\\fscy104)\\t(80,140,\\fscx100\\fscy100)}}{fmt(x)}")
open(f"{O}/caps.ass", "w").write(f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Anton,112,&H00FFFFFF,&H00FFFFFF,&H00000000,&HA0000000,0,0,0,0,100,100,1,0,1,10,6,5,80,80,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(lines) + "\n")

# ---------------- overlay PNGs ----------------
def F(s): return ImageFont.truetype(ANTON, s)
def emoji(e, size):
    im = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((100, 100), e, font=ImageFont.truetype(EMOJI, 109), embedded_color=True, anchor="mm")
    im = im.crop(im.getbbox()); s = size / max(im.size)
    return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)

# shade
g = Image.new("L", (1, H))
for y in range(H):
    a = int(150 * (1 - y / 420)) if y < 420 else (int(170 * min(1, (y - 1100) / 500)) if y > 1100 else 0)
    g.putpixel((0, y), a)
sh = Image.new("RGBA", (W, H), (0, 0, 0, 255)); sh.putalpha(g.resize((W, H))); sh.save(f"{O}/o_shade.png")

ITEMS = [("🕛", (60, 160, 255)), ("📥", (40, 200, 110)), ("🎮", (230, 40, 60)), ("👫", (255, 90, 160)),
         ("🌴", (255, 150, 40)), ("🐊", (60, 190, 90)), ("😭", (160, 70, 255))]
LBL = [(11.80, 20.90), (20.90, 30.58), (30.58, 37.80), (37.80, 45.84), (45.84, 52.58), (52.58, 64.56), (64.56, 73.88)]

def badge(k):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for j in range(7):
        x = 540 + (j - 3) * 92; on = j <= k; cur = j == k; rr = 30 if cur else 22
        d.ellipse([x - rr, 190 - rr, x + rr, 190 + rr], fill=(255, 230, 0) if on else (255, 255, 255, 70), outline=(0, 0, 0), width=4)
        d.text((x, 190), str(j + 1), font=F(30 if cur else 24), fill=(0, 0, 0) if on else (255, 255, 255), anchor="mm")
    t = "7 COISAS ANTES DE JOGAR GTA 6"; f = F(42); tw = d.textlength(t, font=f)
    d.rounded_rectangle([540 - tw / 2 - 28, 250, 540 + tw / 2 + 28, 316], 33, fill=(0, 0, 0, 170))
    d.text((540, 283), t, font=f, fill=(255, 255, 255), anchor="mm")
    im.save(f"{O}/o_badge{k}.png")

def bigcard(k):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    em, col = ITEMS[k]
    d.text((540, 800), str(k + 1), font=F(560), fill=col, anchor="mm", stroke_width=22, stroke_fill=(0, 0, 0))
    e = emoji(em, 220); im.alpha_composite(e, (760, 470))
    im.save(f"{O}/o_big{k}.png")

def label(lines_, fn, y=760, col=(255, 230, 0), size=150, em=None):
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(c); yy = y
    if em: e = emoji(em, 190); c.alpha_composite(e, (540 - e.width // 2, yy - 220))
    for i, t in enumerate(lines_):
        s = size if i == 0 else int(size * 0.55)
        while d.textlength(t, font=F(s)) > 980: s -= 6
        d.text((540, yy), t, font=F(s), fill=col if i == 0 else (255, 255, 255), anchor="mm", stroke_width=12, stroke_fill=(0, 0, 0))
        yy += int(s * 1.05)
    c.save(f"{O}/{fn}")

def stamp(text, sub, fn, rot=-10):
    im = Image.new("RGBA", (1000, 460), (0, 0, 0, 0)); d = ImageDraw.Draw(im); red = (230, 20, 30, 255)
    d.rounded_rectangle([20, 20, 980, 440], 30, outline=red, width=22)
    s = 210
    while d.textlength(text, font=F(s)) > 880: s -= 6
    d.text((500, 190), text, font=F(s), fill=red, anchor="mm")
    d.text((500, 360), sub, font=F(90), fill=(255, 255, 255, 255), anchor="mm", stroke_width=8, stroke_fill=(0, 0, 0))
    im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0)); c.alpha_composite(im, (540 - im.width // 2, 760 - im.height // 2)); c.save(f"{O}/{fn}")

for k in range(7): badge(k); bigcard(k)
label(["HOJE 00:00", "GTA 6 CHEGA"], "o_h1.png", 760, (255, 230, 0), 200, "🚨")
label(["NÃO PASSA", "VERGONHA"], "o_h3.png", 760, (255, 230, 0), 210, "😳")
label(["7 COISAS", "QUE VOCÊ PRECISA SABER"], "o_h2.png", 760, (255, 230, 0), 220, "😱")
label(["00:00", "HORÁRIO DE BRASÍLIA"], "o_1a.png", 760, (120, 200, 255), 240)
label(["NZ JOGA ANTES"], "o_1b.png", 780, (255, 255, 255), 150, "🇳🇿")
label(["SPOILER!"], "o_1c.png", 780, (255, 60, 60), 210, "⚠️")
label(["BAIXA AGORA"], "o_2b.png", 780, (60, 230, 120), 190, "⬇️")
stamp("SEM PC", "SÓ CONSOLE", "o_3a.png", -10)
label(["PS5", "XBOX SERIES X|S"], "o_3b.png", 780, (255, 255, 255), 220, "✅")
stamp("SEM PS4", "NÃO RODA", "o_3c.png", 8)
label(["JASON & LÚCIA", "2 PROTAGONISTAS"], "o_4a.png", 780, (255, 120, 190), 170)
label(["1ª PROTAGONISTA", "MULHER DA ERA MODERNA"], "o_4b.png", 780, (255, 120, 190), 150, "👑")
label(["LEONIDA", "INSPIRADO NA FLÓRIDA"], "o_5a.png", 780, (255, 170, 60), 210)
label(["VICE CITY", "VOLTOU"], "o_5b.png", 780, (255, 90, 200), 230, "🌴")
label(["2X GTA 5*", "*SEGUNDO PRÉVIAS"], "o_6a.png", 780, (255, 230, 0), 220, "🗺️")
label(["PRAIA • ILHAS • PÂNTANO"], "o_6b.png", 800, (255, 255, 255), 120)
label(["JACARÉ NA LOJA"], "o_6c.png", 780, (90, 230, 110), 160, "🐊")
label(["13 ANOS", "DE ESPERA"], "o_7a.png", 780, (190, 120, 255), 240)
label(["+200 MILHÕES", "DE CÓPIAS DO GTA 5"], "o_7b.png", 780, (60, 230, 120), 170, "💰")
label(["PRESSÃO", "GIGANTE"], "o_7c.png", 780, (255, 80, 60), 220, "😰")
label(["00:00 OU", "TRABALHO?"], "o_c1.png", 760, (255, 230, 0), 210, "🤒")
label(["SEGUE PRA", "PARTE 2"], "o_c2.png", 760, (255, 230, 0), 200, "🔔")
c = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
d.rounded_rectangle([90, 640, 990, 900], 36, fill=(10, 10, 20, 225), outline=(255, 255, 255), width=5)
d.text((140, 700), "GRAND THEFT AUTO VI", font=F(64), fill=(255, 255, 255), anchor="lm")
d.text((140, 775), "PRÉ-DOWNLOAD...", font=F(46), fill=(200, 200, 200), anchor="lm")
d.rounded_rectangle([140, 820, 940, 860], 20, fill=(60, 60, 70)); c.save(f"{O}/o_dl.png")

OV = [("o_shade.png", 0, DUR), ("o_h2.png", 0.0, 4.6), ("o_h1.png", 4.70, 7.2), ("o_h3.png", 7.26, 11.75)]
for k, (a, b) in enumerate(LBL):
    OV.append((f"o_big{k}.png", a, a + 0.6)); OV.append((f"o_badge{k}.png", a, b))
OV += [("o_1a.png", 12.44, 15.4), ("o_1b.png", 15.44, 18.8), ("o_1c.png", 18.84, 20.9),
       ("o_dl.png", 21.84, 25.6), ("o_2b.png", 25.66, 30.58),
       ("o_3a.png", 31.3, 32.7), ("o_3b.png", 32.76, 35.2), ("o_3c.png", 35.28, 37.8),
       ("o_4a.png", 38.58, 41.5), ("o_4b.png", 41.56, 45.8),
       ("o_5a.png", 46.74, 50.4), ("o_5b.png", 51.2, 52.55),
       ("o_6a.png", 52.94, 57.6), ("o_6b.png", 57.64, 59.8), ("o_6c.png", 59.86, 64.5),
       ("o_7a.png", 65.36, 68.4), ("o_7b.png", 68.46, 71.3), ("o_7c.png", 71.32, 73.85),
       ("o_c1.png", 73.88, 78.7), ("o_c2.png", 78.76, DUR)]

# ---------------- music + sfx ----------------
SR = 44100; N = int(SR * (DUR + 0.5)); np.random.seed(7)
bpm = 112; beat = 60 / bpm; bar = 4 * beat; mus = np.zeros(N)
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def env(n, a=0.01, r=0.3):
    e = np.ones(n); na = int(a * SR); e[:na] = np.linspace(0, 1, na); return e * np.exp(-np.arange(n) / SR / r)
prog = [(50, [50, 53, 57]), (46, [46, 50, 53]), (48, [48, 52, 55]), (45, [45, 49, 52])]  # Dm Bb C A
for i in range(int(DUR / bar) + 1):
    root, ch = prog[i % 4]; s0 = int(i * bar * SR); n = min(int(bar * SR), N - s0)
    if n <= 0: break
    tt = np.arange(n) / SR
    pad = sum(np.sign(np.sin(2 * np.pi * hz(m + 12) * tt + k)) * 0.5 + np.sin(2 * np.pi * hz(m + 12) * 1.004 * tt) for k, m in enumerate(ch))
    pad *= 0.045 * np.minimum(1, tt / 0.3) * np.minimum(1, (bar - tt) / 0.3)
    mus[s0:s0 + n] += np.convolve(pad, np.ones(12) / 12, "same")
    for e8 in range(8):
        b0 = s0 + int(e8 * beat / 2 * SR); bn = int(beat / 2 * SR * 0.9)
        if b0 + bn > N: break
        bt = np.arange(bn) / SR; saw = 2 * ((hz(root - 12) * bt) % 1) - 1
        mus[b0:b0 + bn] += 0.16 * np.convolve(saw, np.ones(30) / 30, "same") * env(bn, 0.005, 0.15)
    for q in range(4):
        k0 = s0 + int(q * beat * SR); kn = int(0.35 * SR)
        if k0 + kn > N: break
        kt = np.arange(kn) / SR
        mus[k0:k0 + kn] += 0.5 * np.sin(2 * np.pi * (50 + 90 * np.exp(-kt * 30)) * kt) * np.exp(-kt * 9)
        if q % 2 == 1:
            sn = np.random.randn(int(0.2 * SR)) * np.exp(-np.arange(int(0.2 * SR)) / SR * 18) * 0.18; mus[k0:k0 + len(sn)] += sn
        for hh in (0, 0.5):
            h0 = k0 + int(hh * beat * SR); hn = int(0.05 * SR)
            mus[h0:h0 + hn] += np.diff(np.random.randn(hn + 1)) * np.exp(-np.arange(hn) / SR * 80) * 0.05
mus /= np.max(np.abs(mus)) + 1e-9
sfx = np.zeros(N)
def whoosh(at_, dur=0.45, amp=0.5):
    n = int(dur * SR); s0 = max(0, int(at_ * SR) - n // 2); noise = np.random.randn(n); k = np.linspace(40, 4, n).astype(int)
    out = np.array([noise[max(0, i - k[i]):i + 1].mean() for i in range(n)]) * np.sin(np.pi * np.arange(n) / n) ** 2
    sfx[s0:s0 + n] += amp * out / (np.abs(out).max() + 1e-9)
def thump(at_, amp=0.8):
    n = int(0.5 * SR); s0 = int(at_ * SR); kt = np.arange(n) / SR
    sfx[s0:s0 + n] += amp * (np.sin(2 * np.pi * (40 + 120 * np.exp(-kt * 25)) * kt) * np.exp(-kt * 6) + np.random.randn(n) * np.exp(-kt * 40) * 0.4)
for a, _ in LBL: whoosh(a)
for x in (31.3, 35.28): thump(x)
whoosh(4.7, 0.4, 0.4)
def wav(fn, x):
    x = np.clip(x, -1, 1); w = wave.open(fn, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((x * 32767).astype(np.int16).tobytes()); w.close()
wav(f"{O}/music.wav", mus * 0.9); wav(f"{O}/sfx.wav", sfx / (np.abs(sfx).max() + 1e-9) * 0.8)

# ---------------- final ----------------
inp = ["-i", f"{O}/base.mp4"]
for p, *_ in OV: inp += ["-loop", "1", "-framerate", str(FPS), "-i", f"{O}/{p}"]
inp += ["-i", f"{O}/voz.mp3", "-i", f"{O}/music.wav", "-i", f"{O}/sfx.wav"]
fc = []; prev = "0:v"
for i, (p, a, b) in enumerate(OV):
    fc.append(f"[{i+1}:v]format=rgba,trim=duration={DUR},fade=in:st={a}:d=0.12:alpha=1[o{i}]")
    fc.append(f"[{prev}][o{i}]overlay=0:0:enable='between(t,{a},{b})':shortest=1[v{i}]"); prev = f"v{i}"
flash = "+".join(f"between(t,{a},{a+0.1})" for a, _ in LBL)
fc.append(f"[{prev}]drawbox=x=0:y=0:w=iw:h=ih:color=white@0.85:t=fill:enable='{flash}',"
          f"drawbox=x=140:y=820:w='max(1,800*min(0.97,(t-21.84)/3.6))':h=40:color=0x22DD66:t=fill:enable='between(t,21.84,25.6)',"
          f"ass={O}/caps.ass:fontsdir={os.path.dirname(ANTON)},format=yuv420p[v]")
nv = len(OV) + 1
fc.append(f"[{nv+1}:a]volume=0.16[m];[{nv}:a]asplit=2[vo][sc];[m][sc]sidechaincompress=threshold=0.05:ratio=6:attack=20:release=300[md];"
          f"[{nv+2}:a]volume=0.55[fx];[vo]volume=1.15[vv];[vv][md][fx]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.95[a]")
run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + inp + ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
     "-t", str(DUR), "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-c:a", "aac", "-b:a", "192k",
     "-movflags", "+faststart", f"{O}/7coisas_gta6_v2.mp4"])
print("ok")
