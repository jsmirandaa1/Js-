import os, re, subprocess, math, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
TR = f"{D}/rs/tr/GTAVI_Launch_Trailer.mp4"
PL = f"{D}/rs/tr/GTAVI_Pre-Load_Now.mp4"
ANTON = f"{D}/../v/Anton.ttf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
W, H, FPS = 1080, 1920, 30
DUR = 65.65
os.makedirs(f"{D}/shots", exist_ok=True)

def run(cmd):
    subprocess.run(cmd, check=True)

# ---------------- shots: (start, end, src, src_t, xoff 0..1, mode) ----------------
SH = [
    # hook
    (0.00, 1.30, TR, 26.2, 0.45, ""), (1.30, 2.40, TR, 53.0, 0.5, ""), (2.40, 3.50, TR, 49.4, 0.5, ""),
    (3.50, 4.60, TR, 21.1, 0.45, ""), (4.60, 5.80, TR, 73.0, 0.4, ""), (5.80, 7.42, TR, 25.0, 0.5, ""),
    # fase 1 hype
    (7.42, 9.60, TR, 18.2, 0.5, ""), (9.60, 11.20, TR, 19.4, 0.5, ""), (11.20, 13.00, TR, 40.0, 0.5, ""),
    (13.00, 14.60, TR, 45.0, 0.55, ""), (14.60, 16.20, TR, 35.0, 0.5, ""), (16.20, 17.80, TR, 63.0, 0.6, ""),
    (17.80, 19.25, TR, 22.28, 0.5, "zoom"), (19.25, 20.72, TR, 64.38, 0.45, "zoom"),
    # fase 2 negação
    (20.72, 22.86, TR, 47.0, 0.5, ""), (22.86, 25.40, TR, 12.3, 0.55, ""), (25.40, 27.60, TR, 8.0, 0.5, ""),
    (27.60, 28.95, TR, 55.2, 0.5, ""),
    # fase 3 luto
    (28.95, 30.93, TR, 59.0, 0.5, "gray"), (30.93, 32.60, TR, 65.5, 0.45, "gray"), (32.60, 35.20, TR, 36.3, 0.5, "gray"),
    (35.20, 36.87, TR, 28.0, 0.5, "gray"), (36.87, 39.70, TR, 70.0, 0.5, "gray"),
    # fase 4 ansiedade
    (39.70, 42.00, PL, 15.0, 0.5, ""), (42.00, 44.50, PL, 11.0, 0.5, ""), (44.50, 46.19, PL, 19.0, 0.5, ""),
    (46.19, 46.98, None, 0, 0, "black"), (46.98, 49.29, PL, 9.0, 0.5, ""),
    # fase 5 meia-noite
    (49.29, 51.54, TR, 80.0, 0.5, ""), (51.54, 53.60, TR, 38.0, 0.5, ""), (53.60, 55.20, TR, 61.0, 0.5, ""),
    (55.20, 56.40, TR, 72.0, 0.4, ""), (56.40, 58.33, TR, 67.5, 0.5, ""),
    # CTA
    (58.33, 60.60, TR, 27.0, 0.45, ""), (60.60, 62.10, TR, 75.0, 0.5, ""), (62.10, DUR, TR, 41.0, 0.5, ""),
]

files = []
for i, (a, b, src, st, xo, mode) in enumerate(SH):
    out = f"{D}/shots/s{i:02d}.mp4"; files.append(out)
    d = b - a
    if os.path.exists(out) and not os.environ.get("REDO"): continue
    if mode == "black":
        run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"color=black:s={W}x{H}:r={FPS}:d={d:.3f}",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", out]); continue
    cw = 2160 * 9 / 16  # 1215 of 3840x2160
    x = int((3840 - cw) * xo)
    vf = f"crop={int(cw)}:2160:{x}:0,scale={W}:{H}"
    if mode == "zoom":
        vf = f"setpts=3.1*PTS,fps=30,crop={int(cw)}:2160:{x}:0,scale={W*2}:{H*2},zoompan=z='min(1+0.25*on/({d}*{FPS}),1.25)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={W}x{H}:fps={FPS}"
    vf += ",eq=contrast=1.06:saturation=1.18"
    if mode == "gray":
        vf += ",hue=s=0,eq=brightness=-0.06:contrast=1.15,vignette=PI/4"
    vf += f",fps={FPS},format=yuv420p"
    run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{st}", "-i", src, "-t", f"{d:.3f}", "-vf", vf, "-an",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", out])
open(f"{D}/shots/list.txt", "w").write("".join(f"file '{f}'\n" for f in files))
run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{D}/shots/list.txt", "-c", "copy", f"{D}/base.mp4"])

# ---------------- captions ----------------
CAP = [
    ("Se você esperou o GTA 6,", 0, 2.99), ("você passou por essas cinco fases.", 3.47, 5.03), ("E não adianta negar.", 5.23, 7.19),
    ("Dezembro de 2023, sai o primeiro trailer. Você assistiu umas quarenta vezes, pausou cada frame e jurou que tinha achado um segredo no reflexo de um carro.", 9.97, 20.22),
    ("O jogo é adiado pra maio de 2026.", 22.86, 25.42), ("Tranquilo, é só mais um pouquinho.", 25.76, 27.54), ("Eu espero.", 27.86, 28.41),
    ("Adiaram de novo, agora pra novembro.", 30.93, 33.15), ("Você ficou olhando pro teto, questionando a vida…", 33.61, 36.31),
    ("e começou o GTA 5 pela décima vez.", 36.87, 39.24),
    ("Pré-download liberado.", 41.95, 43.12), ("Você liga o console só pra ver a barrinha andar.", 43.48, 45.81),
    ("Desliga.", 46.19, 46.64), ("Cinco minutos depois, liga de novo.", 46.98, 48.78),
    ("Vou jogar só dez minutinhos pra testar.", 51.54, 53.56), ("Quando você olha o relógio, são seis da manhã…", 53.96, 56.36),
    ("e você tem que trabalhar.", 56.76, 57.88),
    ("E aí, em qual fase você tá agora?", 58.33, 60.38), ("Comenta aí.", 60.67, 61.21),
    ("E segue, porque a partir de amanhã", 61.60, 63.75), ("eu trago tudo do GTA 6 pra você.", 63.93, 65.44),
]
HL = {"GTA", "6", "5", "6,", "CINCO", "FASES", "2023", "2026", "QUARENTA", "SEGREDO", "ADIADO", "MAIO", "NOVEMBRO", "DÉCIMA",
      "PRÉ-DOWNLOAD", "DESLIGA", "DEZ", "MINUTINHOS", "SEIS", "MANHÃ", "TRABALHAR", "FASE", "COMENTA", "SEGUE", "NEGAR", "TETO", "VIDA"}

def SL(x): return len(x.replace("GTA", "gê tê á").replace("2023", "dois mil e vinte e três").replace("2026", "dois mil e vinte e seis"))

def at(t):
    return f"0:{int(t//60):02d}:{t%60:05.2f}"

ev = []
for text, a, b in CAP:
    ws = text.split(); chunks, c = [], []
    for w in ws:
        c.append(w)
        if len(" ".join(c)) >= 11 or len(c) >= 3 or re.search(r"[,.?!:…]$", w):
            chunks.append(" ".join(c)); c = []
    if c: chunks.append(" ".join(c))
    L = sum(SL(x) + 2 for x in chunks); t = a
    for x in chunks:
        d = (b - a) * (SL(x) + 2) / L; ev.append((t, t + d, x)); t += d

def fmt(x):
    out = []
    for w in x.upper().split():
        core = re.sub(r"[,.?!:…]", "", w)
        out.append("{\\c&H00E6FF&}" + w + "{\\c&HFFFFFF&}" if core in HL or w in HL else w)
    return " ".join(out)

lines = []
for j, (a, b, x) in enumerate(ev):
    nxt = ev[j + 1][0] if j + 1 < len(ev) else DUR
    b = min(max(b, a + 0.3), nxt) if nxt - a > 0.3 else nxt
    if nxt - b < 0.35: b = nxt
    lines.append(f"Dialogue: 0,{at(a)},{at(b)},Cap,,0,0,0,,{{\\pos(540,1330)\\fscx70\\fscy70\\t(0,80,\\fscx104\\fscy104)\\t(80,140,\\fscx100\\fscy100)}}{fmt(x)}")
open(f"{D}/caps.ass", "w").write(f"""[Script Info]
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
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((80, 80), e, font=ImageFont.truetype(EMOJI, 109), embedded_color=True, anchor="mm")
    im = im.crop(im.getbbox()); s = size / max(im.size)
    return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)

PH = [("HYPE", "🔥", (255, 90, 30)), ("NEGAÇÃO", "🙂", (40, 140, 255)), ("LUTO", "💀", (120, 120, 120)),
      ("ANSIEDADE", "⏳", (255, 200, 0)), ("MEIA-NOITE", "🌙", (160, 60, 255))]
PT = [(7.42, 20.72), (20.72, 28.95), (28.95, 39.70), (39.70, 49.29), (49.29, 58.33)]

# shading (top/bottom gradient for legibility)
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); px = sh.load()
g = Image.new("L", (1, H))
for y in range(H):
    a = 0
    if y < 420: a = int(150 * (1 - y / 420))
    if y > 1100: a = int(170 * min(1, (y - 1100) / 500))
    g.putpixel((0, y), a)
sh = Image.new("RGBA", (W, H), (0, 0, 0, 255)); sh.putalpha(g.resize((W, H))); sh.save(f"{D}/o_shade.png")

def badge(k):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    name, em, col = PH[k]
    # progress pills
    for j in range(5):
        x = 540 + (j - 2) * 120
        d.rounded_rectangle([x - 50, 150, x + 50, 166], 8, fill=(PH[j][2] + (255,)) if j <= k else (255, 255, 255, 80))
    t = f"FASE {k+1}: {name}"
    f = F(70); tw = d.textlength(t, font=f); e = emoji(em, 70)
    bw = tw + e.width + 90
    d.rounded_rectangle([540 - bw / 2, 195, 540 + bw / 2, 305], 30, fill=col + (235,), outline=(0, 0, 0), width=5)
    tx = 540 - bw / 2 + 35
    d.text((tx, 250), t, font=f, fill=(0, 0, 0) if k == 3 else (255, 255, 255), anchor="lm")
    im.alpha_composite(e, (int(tx + tw + 20), 250 - e.height // 2))
    im.save(f"{D}/o_badge{k}.png")

def bigcard(k):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    name, em, col = PH[k]
    e = emoji(em, 260); im.alpha_composite(e, (540 - e.width // 2, 560 - e.height // 2))
    d.text((540, 820), f"FASE {k+1}", font=F(230), fill=(255, 255, 255), anchor="mm", stroke_width=14, stroke_fill=(0, 0, 0))
    size = 170
    while d.textlength(name, font=F(size)) > 980: size -= 6
    d.text((540, 1020), name, font=F(size), fill=col, anchor="mm", stroke_width=12, stroke_fill=(0, 0, 0))
    im.save(f"{D}/o_big{k}.png")

def stamp(text, sub, fn, rot=-12):
    im = Image.new("RGBA", (1000, 460), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    red = (230, 20, 30, 255)
    d.rounded_rectangle([20, 20, 980, 440], 30, outline=red, width=22)
    size = 210
    while d.textlength(text, font=F(size)) > 880: size -= 6
    d.text((500, 190), text, font=F(size), fill=red, anchor="mm")
    d.text((500, 360), sub, font=F(90), fill=(255, 255, 255, 255), anchor="mm", stroke_width=8, stroke_fill=(0, 0, 0))
    im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0)); c.alpha_composite(im, (540 - im.width // 2, 760 - im.height // 2))
    c.save(f"{D}/{fn}")

def label(lines_, fn, y=760, col=(255, 230, 0), size=150, em=None):
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    yy = y
    if em:
        e = emoji(em, 200); c.alpha_composite(e, (540 - e.width // 2, yy - 230))
    for i, t in enumerate(lines_):
        s = size if i == 0 else int(size * 0.55)
        while d.textlength(t, font=F(s)) > 980: s -= 6
        d.text((540, yy), t, font=F(s), fill=col if i == 0 else (255, 255, 255), anchor="mm", stroke_width=12, stroke_fill=(0, 0, 0))
        yy += int(s * 1.05)
    c.save(f"{D}/{fn}")

for k in range(5): badge(k); bigcard(k)
stamp("ADIADO", "MAIO 2026", "o_st1.png", -10)
stamp("ADIADO DE NOVO", "NOVEMBRO 2026", "o_st2.png", 8)
label(["AS 5 FASES", "DE QUEM ESPEROU O GTA 6"], "o_title.png", 700, (255, 230, 0), 200, "😭")
label(["DEZ 2023", "TRAILER 1"], "o_dez.png", 700, (255, 120, 200), 190)
label(["40x"], "o_40x.png", 800, (255, 230, 0), 230, "👀")
label(["SEGREDO?"], "o_seg.png", 800, (255, 230, 0), 190, "🔍")
label(["GTA 5", "PELA 10ª VEZ"], "o_gta5.png", 720, (255, 255, 255), 200)
label(["00:00"], "o_0000.png", 740, (160, 220, 255), 260, "🎮")
label(["06:00"], "o_0600.png", 740, (255, 80, 60), 260, "😵")
label(["EM QUAL FASE", "VOCÊ TÁ?"], "o_cta.png", 760, (255, 230, 0), 170, "👇")
label(["SEGUE PRA", "PARTE 2"], "o_follow.png", 760, (255, 230, 0), 170, "🔔")
label(["DESLIGA"], "o_desl.png", 840, (255, 255, 255), 200, "🔌")
# download bar frame
c = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
d.rounded_rectangle([90, 640, 990, 900], 36, fill=(10, 10, 20, 225), outline=(255, 255, 255), width=5)
d.text((140, 700), "GRAND THEFT AUTO VI", font=F(64), fill=(255, 255, 255), anchor="lm")
d.text((140, 775), "BAIXANDO...", font=F(46), fill=(200, 200, 200), anchor="lm")
d.rounded_rectangle([140, 820, 940, 860], 20, fill=(60, 60, 70))
c.save(f"{D}/o_dl.png")

# timed overlays: (png, start, end, fade)
OV = [("o_shade.png", 0, DUR), ("o_title.png", 0.0, 2.9)]
for k, (a, b) in enumerate(PT):
    OV.append((f"o_badge{k}.png", a + 1.6, b))
    OV.append((f"o_big{k}.png", a, a + 1.75))
OV += [("o_dez.png", 9.9, 11.6), ("o_40x.png", 14.0, 16.0), ("o_seg.png", 18.2, 20.6),
       ("o_st1.png", 23.2, 25.6), ("o_st2.png", 31.0, 33.4), ("o_gta5.png", 37.0, 39.6),
       ("o_dl.png", 41.9, 46.19), ("o_desl.png", 46.19, 46.98), ("o_dl.png", 47.2, 49.29),
       ("o_0000.png", 51.6, 53.5), ("o_0600.png", 54.6, 58.2), ("o_cta.png", 58.33, 61.4), ("o_follow.png", 61.6, DUR)]

# ---------------- music + sfx (synthesized) ----------------
SR = 44100
N = int(SR * (DUR + 0.5)); t = np.arange(N) / SR
bpm = 104; beat = 60 / bpm
mus = np.zeros(N)
def env(n, a=0.01, r=0.3):
    e = np.ones(n); na = int(a * SR); e[:na] = np.linspace(0, 1, na); return e * np.exp(-np.arange(n) / SR / r)
prog = [(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [48, 52, 55]), (55, [55, 59, 62])]  # Am F C G
def hz(m): return 440 * 2 ** ((m - 69) / 12)
bar = 4 * beat
nb = int(DUR / bar) + 1
for i in range(nb):
    root, ch = prog[i % 4]; s0 = int(i * bar * SR); n = min(int(bar * SR), N - s0)
    if n <= 0: break
    tt = np.arange(n) / SR
    pad = sum(np.sign(np.sin(2 * np.pi * hz(m) * tt + k)) * 0.5 + np.sin(2 * np.pi * hz(m) * 1.003 * tt) for k, m in enumerate(ch))
    pad *= 0.05 * np.minimum(1, tt / 0.4) * np.minimum(1, (bar - tt) / 0.3)
    mus[s0:s0 + n] += np.convolve(pad, np.ones(12) / 12, "same")
    for e8 in range(8):  # bass eighths
        b0 = s0 + int(e8 * beat / 2 * SR); bn = int(beat / 2 * SR * 0.9)
        if b0 + bn > N: break
        bt = np.arange(bn) / SR
        saw = 2 * ((hz(root - 12) * bt) % 1) - 1
        mus[b0:b0 + bn] += 0.16 * np.convolve(saw, np.ones(30) / 30, "same") * env(bn, 0.005, 0.18)
    for q in range(4):
        k0 = s0 + int(q * beat * SR); kn = int(0.35 * SR)
        if k0 + kn > N: break
        kt = np.arange(kn) / SR
        mus[k0:k0 + kn] += 0.5 * np.sin(2 * np.pi * (50 + 90 * np.exp(-kt * 30)) * kt) * np.exp(-kt * 9)
        if q % 2 == 1:
            sn = np.random.randn(int(0.2 * SR)) * np.exp(-np.arange(int(0.2 * SR)) / SR * 18) * 0.18
            mus[k0:k0 + len(sn)] += sn
        for hh in (0, 0.5):
            h0 = k0 + int(hh * beat * SR); hn = int(0.05 * SR)
            hs = np.diff(np.random.randn(hn + 1)) * np.exp(-np.arange(hn) / SR * 80) * 0.05
            mus[h0:h0 + hn] += hs
# luto section: lowpass + quieter
a3, b3 = int(28.95 * SR), int(39.7 * SR)
mus[a3:b3] = np.convolve(mus[a3:b3], np.ones(60) / 60, "same") * 0.7
mus /= np.max(np.abs(mus)) + 1e-9
sfx = np.zeros(N)
def whoosh(at_, dur=0.45, amp=0.5):
    n = int(dur * SR); s0 = int(at_ * SR) - n // 2
    noise = np.random.randn(n); k = np.linspace(40, 4, n).astype(int)
    out = np.array([noise[max(0, i - k[i]):i + 1].mean() for i in range(n)])
    out *= np.sin(np.pi * np.arange(n) / n) ** 2
    sfx[max(0, s0):s0 + n] += amp * out[:N - s0] / (np.abs(out).max() + 1e-9)
def thump(at_, amp=0.8):
    n = int(0.5 * SR); s0 = int(at_ * SR); kt = np.arange(n) / SR
    x = np.sin(2 * np.pi * (40 + 120 * np.exp(-kt * 25)) * kt) * np.exp(-kt * 6) + np.random.randn(n) * np.exp(-kt * 40) * 0.4
    sfx[s0:s0 + n] += amp * x[:N - s0]
for a, _ in PT: whoosh(a)
for x in (23.2, 31.0): thump(x)
thump(46.19, 0.6); whoosh(54.6, 0.4, 0.4)
def wav(fn, x):
    x = np.clip(x, -1, 1); w = wave.open(fn, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((x * 32767).astype(np.int16).tobytes()); w.close()
wav(f"{D}/music.wav", mus * 0.9); wav(f"{D}/sfx.wav", sfx / (np.abs(sfx).max() + 1e-9) * 0.8)

# ---------------- final composite ----------------
inp = ["-i", f"{D}/base.mp4"]
for p, *_ in OV: inp += ["-loop", "1", "-framerate", str(FPS), "-i", f"{D}/{p}"]
inp += ["-i", f"{D}/voz.mp3", "-i", f"{D}/music.wav", "-i", f"{D}/sfx.wav"]
fc = []; prev = "0:v"
for i, (p, a, b) in enumerate(OV):
    fc.append(f"[{i+1}:v]format=rgba,trim=duration={DUR},fade=in:st={a}:d=0.12:alpha=1[o{i}]")
    fc.append(f"[{prev}][o{i}]overlay=0:0:enable='between(t,{a},{b})':shortest=1[v{i}]"); prev = f"v{i}"
# flashes at phase starts + animated download bar
flash = "+".join(f"between(t,{a},{a+0.1})" for a, _ in PT)
fc.append(f"[{prev}]drawbox=x=0:y=0:w=iw:h=ih:color=white@0.85:t=fill:enable='{flash}',"
          f"drawbox=x=140:y=820:w='max(1,800*min(1,(t-41.9)/4.3))':h=40:color=0x22DD66:t=fill:enable='between(t,41.9,46.19)',"
          f"drawbox=x=140:y=820:w='800*min(0.99,0.62+(t-47.2)/6)':h=40:color=0x22DD66:t=fill:enable='between(t,47.2,49.29)',"
          f"ass={D}/caps.ass:fontsdir={os.path.dirname(ANTON)},format=yuv420p[v]")
nv = len(OV) + 1
fc.append(f"[{nv+1}:a]volume=0.16[m];[{nv}:a]asplit=2[vo][sc];[m][sc]sidechaincompress=threshold=0.05:ratio=6:attack=20:release=300[md];"
          f"[{nv+2}:a]volume=0.55[fx];[vo]volume=1.15[vv];[vv][md][fx]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.95[a]")
run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + inp + ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
     "-t", str(DUR), "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-c:a", "aac", "-b:a", "192k",
     "-movflags", "+faststart", f"{D}/5fases_gta6.mp4"])
print("ok")
